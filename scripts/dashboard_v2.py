import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y CONSTANTES
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Dashboard Arancelario V23")

st.title("📊 Monitor de Comercio y Aranceles: México - EUA")

# Diccionario de descripciones para Sección 232 (Acero y Aluminio)
RAW_232_MAP = {
    # ACERO
    "9903.81.87": "Productos básicos de hierro o acero (sin incluir derivados).",
    "9903.81.88": "Hierro o acero básico (Zona Franca antes mar-2025).",
    "9903.81.89": "Productos manufacturados de acero (lista original).",
    "9903.81.90": "Nuevos productos manufacturados de acero (Cap. 73).",
    "9903.81.91": "Nuevos productos manufacturados de acero (fuera Cap. 73).",
    "9903.81.92": "Productos de acero hechos en el extranjero (acero USA).",
    "9903.81.93": "Productos manufacturados de acero (viejos y nuevos) que estaban en una Zona Franca antes de marzo de 2025.",
    # ALUMINIO
    "9903.85.02": "Productos básicos de aluminio (sin incluir derivados).",
    "9903.85.04": "Productos manufacturados de aluminio (lista original).",
    "9903.85.07": "Nuevos productos manufacturados de aluminio (Cap. 76).",
    "9903.85.08": "Nuevos productos manufacturados de aluminio (fuera Cap. 76)."
}

SEC232_MAP = {k.replace('.', '').strip(): v for k, v in RAW_232_MAP.items()}

# -----------------------------------------------------------------------------
# 2. FUNCIONES DE LIMPIEZA
# -----------------------------------------------------------------------------

def clean_percentage(val):
    if pd.isna(val): return 0.0
    val_str = str(val).strip().lower()
    if val_str in ['ex.', 'ex', 'libre', 'free', 'n/a', '-', '']: return 0.0
    try:
        clean = ''.join(c for c in val_str if c.isdigit() or c == '.')
        return float(clean) if clean else 0.0
    except: return 0.0

def normalize_cols(df):
    df.columns = df.columns.str.strip()
    return df

def clean_numeric_code(df, col_name):
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.strip().str.replace('.', '', regex=False)
    return df

@st.cache_data
def load_data(target_country="China"):
    path = 'data/manual/LIGIE_HTS_Dashboard_v2.xlsx'
    
    xls = pd.ExcelFile(path)
    
    # LIGIE
    ligie = pd.read_excel(xls, sheet_name='LIGIE', dtype=str)
    ligie = normalize_cols(ligie)
    ligie = clean_numeric_code(ligie, 'Código')
    
    # HTS
    hts = pd.read_excel(xls, sheet_name='HTS', dtype=str)
    hts = normalize_cols(hts)
    hts = clean_numeric_code(hts, 'Code')
    hts = hts[hts['Code'].str.len() == 8].copy()

    # AUXILIARES
    sec301 = pd.read_excel(xls, sheet_name='Sec 301', dtype=str)
    sec301 = normalize_cols(sec301)
    sec301 = clean_numeric_code(sec301, 'Code')
    sec301['Duty'] = sec301['Duty'].apply(clean_percentage)

    acero = pd.read_excel(xls, sheet_name='Acero', dtype=str)
    acero = normalize_cols(acero)
    acero = clean_numeric_code(acero, 'Code')
    acero = clean_numeric_code(acero, 'Heading')
    acero['Duty'] = acero['Duty'].apply(clean_percentage)
    acero['Type'] = 'Acero'
    
    aluminio = pd.read_excel(xls, sheet_name='Aluminio', dtype=str)
    aluminio = normalize_cols(aluminio)
    aluminio = clean_numeric_code(aluminio, 'Code')
    aluminio = clean_numeric_code(aluminio, 'Heading')
    aluminio['Duty'] = aluminio['Duty'].apply(clean_percentage)
    aluminio['Type'] = 'Aluminio'
    
    sec232_db = pd.concat([acero, aluminio], ignore_index=True)

    tmec = pd.read_excel(xls, sheet_name='TMEC', dtype=str)
    tmec = normalize_cols(tmec)
    tmec = clean_numeric_code(tmec, 'Code')

    # HISTÓRICOS
    part = pd.read_excel(xls, sheet_name='Participación')
    part = normalize_cols(part)
    if 'Date' in part.columns:
        part['Date'] = pd.to_datetime(part['Date'])
    part = clean_numeric_code(part, 'Subpartida')

    aranceles = pd.read_excel(xls, sheet_name='Aranceles Efectivos')
    aranceles = normalize_cols(aranceles)
    if 'Date' in aranceles.columns:
        aranceles['Date'] = pd.to_datetime(aranceles['Date'])
    aranceles = clean_numeric_code(aranceles, 'Subpartida')

    return ligie, hts, sec301, sec232_db, tmec, part, aranceles

# -----------------------------------------------------------------------------
# 3. LÓGICA SEC 232 (Opciones)
# -----------------------------------------------------------------------------

def get_232_options(hts_8_digit, df_232):
    hts_8 = str(hts_8_digit).strip()
    matches = df_232[df_232['Code'] == hts_8].copy()
    
    if matches.empty:
        for length in [6, 4]:
            sub = hts_8[:length]
            matches = df_232[df_232['Code'] == sub].copy()
            if not matches.empty: break
    
    options = []
    if not matches.empty:
        for _, row in matches.iterrows():
            heading_clean = row['Heading']
            desc = SEC232_MAP.get(heading_clean, f"Opción ({heading_clean})")
            options.append({
                'Heading': heading_clean,
                'Description': desc,
                'Duty': row['Duty'],
                'Type': row['Type']
            })
    return options

# -----------------------------------------------------------------------------
# 4. INTERFAZ
# -----------------------------------------------------------------------------

def show_hierarchy_item(label, value):
    val_str = str(value).strip()
    if val_str.lower() != 'nan' and val_str != '':
        st.markdown(f"**{label}:** {val_str}")

# --- SIDEBAR ---
st.sidebar.header("🔍Consulta")
hs6_input = st.sidebar.text_input("Subpartida (6 Dígitos):", max_chars=6, placeholder="Ej: 722020")
st.sidebar.markdown("---")

st.sidebar.markdown("### País aplicador del arancel:")
apply_mx = st.sidebar.checkbox("México", value=True)
apply_us = st.sidebar.checkbox("Estados Unidos", value=True)
st.sidebar.markdown("---")

st.sidebar.markdown("### País gravado:")
target_country = st.sidebar.selectbox("Seleccione país de origen:", ["China"])

# --- CARGA ---
try:
    ligie, hts, sec301, sec232_db, tmec, part, aranceles = load_data(target_country)
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

# --- LÓGICA PRINCIPAL ---
if st.sidebar.button("Buscar") or hs6_input:
    hs6_input = hs6_input.strip()
    
    if len(hs6_input) < 6:
        st.warning("Por favor ingresa 6 dígitos.")
    else:
        
        # =====================================================================
        # MÓDULO MÉXICO
        # =====================================================================
        if apply_mx:
            st.header("🇲🇽 México")
            
            if 'Código' in ligie.columns:
                ligie_filtrado = ligie[ligie['Código'].str.startswith(hs6_input)].copy()
            else:
                ligie_filtrado = pd.DataFrame()

            if not ligie_filtrado.empty:
                try:
                    with st.expander("📂 Ley de los Impuestos Generales de Importación y Exportación (LIGIE)", expanded=True):
                        row = ligie_filtrado.iloc[0]
                        show_hierarchy_item("Sección", row.get('Sección'))
                        show_hierarchy_item("Capítulo", row.get('Capítulo'))
                        show_hierarchy_item("Partida", row.get('Partida'))
                        show_hierarchy_item("Subpartida", row.get('Subpartida'))
                        show_hierarchy_item("Desdoblamiento", row.get('Desdoblamiento'))
                except: pass

                ligie_filtrado['Tasa General'] = ligie_filtrado['General'].apply(clean_percentage)
                avg_rate = ligie_filtrado['Tasa General'].mean()

                col_metrics, col_table = st.columns([1, 4])
                with col_metrics:
                    st.metric("Arancel Promedio LIGIE", f"{avg_rate:,.2f}% 🇨🇳")
                
                with col_table:
                    df_display_mx = ligie_filtrado[['Código', 'Fracción', 'Tasa General']].copy()
                    df_display_mx.columns = ['Código', 'Descripción', 'Arancel']
                    st.dataframe(df_display_mx.style.format({'Arancel': '{:.2f}%'}), use_container_width=True, hide_index=True)

            else:
                st.warning(f"No se encontró información en LIGIE para {hs6_input}")
            
            st.markdown("---")

        # =====================================================================
        # MÓDULO ESTADOS UNIDOS
        # =====================================================================
        if apply_us:
            st.header("🇺🇸 Estados Unidos")
            
            if 'Code' in hts.columns:
                hts_filtrado = hts[hts['Code'].str.startswith(hs6_input)].copy()
            else:
                hts_filtrado = pd.DataFrame()

            if not hts_filtrado.empty:
                try:
                    with st.expander("📂 Harmonized Tariff Schedule (HTS)", expanded=True):
                        row = hts_filtrado.iloc[0]
                        show_hierarchy_item("Section", row.get('Section'))
                        show_hierarchy_item("Chapter", row.get('Chapter'))
                        show_hierarchy_item("Heading", row.get('Heading'))
                        show_hierarchy_item("Breakdown", row.get('Breakdown'))
                        show_hierarchy_item("Subheading", row.get('Subheading'))
                except: pass

                # Procesamiento
                hts_filtrado['General Duty'] = hts_filtrado['General'].apply(clean_percentage)
                
                if 'Reciprocal' in hts_filtrado.columns:
                    hts_filtrado['Reciprocal Duty'] = hts_filtrado['Reciprocal'].apply(clean_percentage)
                else:
                    hts_filtrado['Reciprocal Duty'] = 0.0

                if 'Fentanyl' in hts_filtrado.columns:
                    hts_filtrado['Fentanyl Duty'] = hts_filtrado['Fentanyl'].apply(clean_percentage)
                else:
                    hts_filtrado['Fentanyl Duty'] = 0.0

                hts_filtrado = hts_filtrado.merge(sec301[['Code', 'Duty']], left_on='Code', right_on='Code', how='left')
                hts_filtrado.rename(columns={'Duty': '301 Duty'}, inplace=True)
                hts_filtrado['301 Duty'] = hts_filtrado['301 Duty'].fillna(0.0)
                
                hts_filtrado['is_tmec'] = hts_filtrado['Code'].isin(tmec['Code'])

                code_options_map = {}
                for code in hts_filtrado['Code'].unique():
                    opts = get_232_options(code, sec232_db)
                    if opts:
                        code_options_map[code] = opts
                
                user_232_selections = {}
                for code, options in code_options_map.items():
                    key = f"radio_232_{code}"
                    selected_opt_str = st.session_state.get(key, "Ninguno")
                    duty_val = 0.0
                    if selected_opt_str != "Ninguno":
                        for opt in options:
                            if opt['Description'] == selected_opt_str:
                                duty_val = opt['Duty']
                                break
                    user_232_selections[code] = duty_val

                hts_filtrado['232 Duty'] = hts_filtrado['Code'].map(user_232_selections).fillna(0.0)
                
                hts_filtrado['Total Duty'] = (
                    hts_filtrado['General Duty'] + 
                    hts_filtrado['301 Duty'] + 
                    hts_filtrado['232 Duty'] +
                    hts_filtrado['Reciprocal Duty'] +
                    hts_filtrado['Fentanyl Duty']
                )

                avg_total_duty = hts_filtrado['Total Duty'].mean()

                col_metrics_us, col_table_us = st.columns([1, 4])
                with col_metrics_us:
                    st.metric("Arancel Promedio Total USA", f"{avg_total_duty:,.2f}% 🇨🇳")

                with col_table_us:
                    st.markdown("📄 *Los registros marcados en verde, representan fracciones incluidas en el TMEC.*")
                    
                    cols_final = [
                        'Code', 'Description', 'General Duty', '301 Duty', '232 Duty', 
                        'Reciprocal Duty', 'Fentanyl Duty', 'Total Duty'
                    ]
                    
                    # Highlight solo background
                    def highlight_tmec_row(row):
                        is_tmec = hts_filtrado.loc[row.name, 'is_tmec']
                        if is_tmec:
                            return ['background-color: #d4edda'] * len(row)
                        return [''] * len(row)

                    format_dict = {
                        'General Duty': '{:.2f}%', '301 Duty': '{:.2f}%', '232 Duty': '{:.2f}%',
                        'Reciprocal Duty': '{:.2f}%', 'Fentanyl Duty': '{:.2f}%', 'Total Duty': '{:.2f}%'
                    }

                    st.dataframe(
                        hts_filtrado[cols_final].style.apply(highlight_tmec_row, axis=1).format(format_dict),
                        use_container_width=True, hide_index=True
                    )

                if code_options_map:
                    with st.expander("⚠️ IMPORTANTE: Existe la posibilidad de que algunas de las fracciones presentadas, se encuentren dentro de los aranceles aplicables de la Sección 232. Por favor, seleccione la opción que mejor describa su producto:", expanded=False):
                        for code, options in code_options_map.items():
                            st.markdown(f"**Opciones para Fracción {code}:**")
                            radio_options = ["Ninguno"] + [opt['Description'] for opt in options]
                            st.radio(
                                label=f"Seleccione variante para {code}",
                                options=radio_options,
                                key=f"radio_232_{code}",
                                label_visibility="collapsed"
                            )
                            st.markdown("---")
                
                # --- 2. RESUMEN DE DESEMPEÑO ---
                st.subheader(f"Resumen de Desempeño: México vs {target_country}")
                
                df_part_sub = part[part['Subpartida'] == hs6_input].sort_values('Date').copy()
                df_aranceles_sub = aranceles[aranceles['Subpartida'] == hs6_input].sort_values('Date').copy()

                if not df_part_sub.empty and not df_aranceles_sub.empty:
                    # Limpieza y Cálculo
                    cols_num = ['Mexico', 'Total', 'China']
                    for col in cols_num:
                        if col in df_part_sub.columns:
                            df_part_sub[col] = pd.to_numeric(df_part_sub[col], errors='coerce').fillna(0)
                    
                    if 'Total' in df_part_sub.columns and 'Mexico' in df_part_sub.columns:
                        df_part_sub['Market_Share_Mex'] = df_part_sub.apply(lambda x: (x['Mexico'] / x['Total'] * 100) if x['Total'] > 0 else 0, axis=1)
                        df_part_sub['Market_Share_China'] = df_part_sub.apply(lambda x: (x['China'] / x['Total'] * 100) if x['Total'] > 0 else 0, axis=1)
                    
                    last_row_part = df_part_sub.iloc[-1]
                    last_date_part = last_row_part['Date'].strftime('%B %Y') if pd.notna(last_row_part['Date']) else "Último"
                    df_12m_part = df_part_sub.iloc[-12:]

                    cols_eff = ['Mexico', 'China']
                    for col in cols_eff:
                        if col in df_aranceles_sub.columns:
                            df_aranceles_sub[col] = pd.to_numeric(df_aranceles_sub[col], errors='coerce').fillna(0) * 100

                    last_row_ara = df_aranceles_sub.iloc[-1]
                    df_12m_ara = df_aranceles_sub.iloc[-12:]

                    # --- CONSTRUCCIÓN TABLA ---
                    def combine_vals(val_mx, val_ch, is_curr=True):
                        fmt = "${:,.2f}" if is_curr else "{:,.2f}%"
                        return f"🇲🇽 {fmt.format(val_mx)}   |   🇨🇳 {fmt.format(val_ch)}"

                    money_last = combine_vals(last_row_part.get('Mexico', 0), last_row_part.get('China', 0), True)
                    share_last = combine_vals(last_row_part.get('Market_Share_Mex', 0), last_row_part.get('Market_Share_China', 0), False)
                    tariff_last = combine_vals(last_row_ara.get('Mexico', 0), last_row_ara.get('China', 0), False)

                    money_avg = combine_vals(df_12m_part['Mexico'].mean(), df_12m_part['China'].mean(), True)
                    share_avg = combine_vals(df_12m_part['Market_Share_Mex'].mean(), df_12m_part['Market_Share_China'].mean(), False)
                    tariff_avg = combine_vals(df_12m_ara['Mexico'].mean(), df_12m_ara['China'].mean(), False)

                    resumen_data = {
                        'Concepto': [f"Último Dato ({last_date_part})", "Promedio 12 Meses"],
                        'Participación (Dólares)': [money_last, money_avg],
                        'Market Share': [share_last, share_avg],
                        'Arancel': [tariff_last, tariff_avg]
                    }
                    
                    # Cambio a st.dataframe para evitar colores extraños de st.table
                    st.dataframe(pd.DataFrame(resumen_data), use_container_width=True, hide_index=True)
                    
                    # --- 3. ANÁLISIS HISTÓRICO ---
                    st.subheader(f"Análisis Histórico: México vs {target_country}")
                    
                    col_chart1, col_chart2 = st.columns(2)

                    with col_chart1:
                        st.markdown("**Participación de Mercado (%)**")
                        chart_data_share = df_part_sub[['Date', 'Market_Share_Mex', 'Market_Share_China']].set_index('Date')
                        chart_data_share.columns = ['México', target_country]
                        st.line_chart(chart_data_share, color=["#006400", "#FF0000"]) 

                    with col_chart2:
                        st.markdown("**Arancel Efectivo (%)**")
                        chart_data_tariff = df_aranceles_sub[['Date', 'Mexico', 'China']].set_index('Date')
                        chart_data_tariff.columns = ['México', target_country]
                        st.line_chart(chart_data_tariff, color=["#006400", "#FF0000"])
                
                else:
                    st.info("No se encontraron datos históricos completos para esta subpartida.")

            else:
                st.warning(f"No se encontró información en HTS para {hs6_input}")

else:
    st.info("👈 Ingresa una subpartida para comenzar.")