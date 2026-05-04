import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y CONSTANTES (BRANDING NAFIN/BANCOMEXT)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Arancelario | NAFIN - BANCOMEXT",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Avanzados - Identidad Institucional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&display=swap');

    /* Hack para renderizado forzado de banderas */
    .bandera {
        font-family: 'Noto Color Emoji', sans-serif;
    }
            
    /* Fuerza la fuente de emojis como respaldo dentro de las tablas de Streamlit */
    [data-testid="stDataFrame"] {
        font-family: sans-serif, 'Noto Color Emoji' !important;
    }

    /* Fondo general de la aplicación ligeramente gris para resaltar las tarjetas blancas */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Diseño de menú estilo "Tabs" para el Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Fija el encabezado del sidebar (donde está el botón de colapsar) al hacer scroll */
    [data-testid="stSidebarHeader"] {
        position: sticky !important;
        top: 0px !important;
        z-index: 999 !important;
        background-color: #ffffff !important;
        padding-bottom: 10px;
    }

    /* Contenedores de Métricas y Tarjetas Estilo NAFIN */
    .metric-container, .card-hover {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .metric-container:hover, .card-hover:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.06) !important;
    }
    
    /* Tipografía institucional para métricas customizadas */
    .metric-title {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #0F172A;
        font-size: 2rem;
        font-weight: 800;
        margin: 5px 0;
        letter-spacing: -0.5px;
    }
    
    /* Separadores y Títulos */
    hr { margin: 15px 0; border-top: 1px solid #E2E8F0; }
    h1, h2, h3 { color: #0F172A !important; font-weight: 800 !important; letter-spacing: -0.5px; }

    /* Estilo para los DataFrames de Streamlit */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }

    [data-testid="stSidebar"] [data-baseweb="input"] {
        background-color: #F8FAFC !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 8px !important;
        transition: border-color 0.3s ease !important;
    }
    [data-testid="stSidebar"] [data-baseweb="input"]:focus-within {
        border-color: #2596be !important;
    } 
</style>
""", unsafe_allow_html=True)

# Encabezado Principal Institucional
st.markdown("<h1 style='color: #2596be; font-size: 2.8rem;'>Monitor de Comercio y Aranceles</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #2596be; margin-top: -10px; border-width: 2px;'>", unsafe_allow_html=True)

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
# 2. FUNCIONES DE LIMPIEZA Y PARSEO
# -----------------------------------------------------------------------------

def clean_percentage(val):
    """Función conservada para usos genéricos o cálculos numéricos limpios"""
    if pd.isna(val): return 0.0
    val_str = str(val).strip().lower()
    if 'annex' in val_str: return "Annex III"
    if val_str in ['ex.', 'ex', 'libre', 'free', 'n/a', '-', '']: return 0.0
    try:
        clean = ''.join(c for c in val_str if c.isdigit() or c == '.')
        return float(clean) if clean else 0.0
    except: return 0.0

def parse_hts_duties(val):
    """
    Nuevo Parser dinámico para extraer 'Math Base Duty', 'General Duty' y 'Fixed Duty'.
    Maneja aranceles mixtos como '$1.035/kg + 8.5%'.
    """
    if pd.isna(val): 
        return 0.0, "Free", None
        
    val_str = str(val).strip()
    lower_val = val_str.lower()
    if lower_val in ['ex.', 'ex', 'libre', 'free', 'n/a', '-', '']:
        return 0.0, "Free", None
        
    parts = [p.strip() for p in val_str.split('+')]
    
    general_math = 0.0
    general_str = None
    fixed_str = None
    
    for part in parts:
        if '%' in part:
            general_str = part
            try:
                # Extrae únicamente la porción numérica de la sección de porcentaje
                general_math = float(''.join(c for c in part if c.isdigit() or c == '.'))
            except: 
                pass
        else:
            fixed_str = part
            
    # Si no hubo signo '+', determinamos si es porcentaje o texto fijo
    if len(parts) == 1:
        if '%' in val_str:
            return general_math, val_str, None
        else:
            return 0.0, None, val_str
            
    return general_math, general_str, fixed_str

def normalize_cols(df):
    df.columns = df.columns.str.strip()
    return df

def clean_numeric_code(df, col_name):
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.strip().str.replace('.', '', regex=False)
    return df

@st.cache_data(show_spinner="Cargando bases de datos v2... Por favor espere.")
def load_data(target_country="China"):
    base_path = 'data/parquet_v2/'
    
    # Mapeos exactos para que encajen con la lógica del Dashboard
    map_ligie = {'codigo': 'Código', 'seccion': 'Sección', 'capitulo': 'Capítulo', 'partida': 'Partida', 'desdoblamiento': 'Desdoblamiento', 'subpartida': 'Subpartida', 'fraccion': 'Fracción', 'general': 'General'}
    map_hts = {'code': 'Code', 'section': 'Section', 'chapter': 'Chapter', 'heading': 'Heading', 'breakdown': 'Breakdown', 'subheading': 'Subheading', 'description': 'Description', 'general': 'General'}
    map_aux = {'code': 'Code', 'duty': 'Duty', 'description': 'Description'}

    # LIGIE
    ligie = pd.read_parquet(f'{base_path}ligie.parquet')
    ligie = normalize_cols(ligie)
    ligie.rename(columns=map_ligie, inplace=True)
    ligie = clean_numeric_code(ligie, 'Código')
    
    # HTS
    hts = pd.read_parquet(f'{base_path}hts.parquet')
    hts = normalize_cols(hts)
    hts.rename(columns=map_hts, inplace=True)
    hts = clean_numeric_code(hts, 'Code')

    # SEC 301
    sec301 = pd.read_parquet(f'{base_path}sec_301.parquet')
    sec301 = normalize_cols(sec301)
    sec301.rename(columns=map_aux, inplace=True)
    sec301 = clean_numeric_code(sec301, 'Code')
    if 'Duty' in sec301.columns:
        sec301['Duty'] = sec301['Duty'].apply(clean_percentage)

    # SECCIÓN 232
    sec232_db = pd.read_parquet(f'{base_path}sec_232.parquet')
    sec232_db = normalize_cols(sec232_db)
    sec232_db.rename(columns=map_aux, inplace=True)
    sec232_db = clean_numeric_code(sec232_db, 'Code')
    if 'Duty' in sec232_db.columns:
        sec232_db['Duty'] = sec232_db['Duty'].apply(clean_percentage)

    # TMEC
    tmec = pd.read_parquet(f'{base_path}tmec.parquet')
    tmec = normalize_cols(tmec)
    tmec.rename(columns=map_aux, inplace=True)
    tmec = clean_numeric_code(tmec, 'Code')

    # AUXILIAR
    auxiliar = pd.read_parquet(f'{base_path}auxiliar.parquet')
    auxiliar = normalize_cols(auxiliar)
    auxiliar.rename(columns=map_aux, inplace=True)
    auxiliar = clean_numeric_code(auxiliar, 'Code')

    # HISTÓRICOS
    part = pd.read_parquet(f'{base_path}participacion.parquet')
    part = normalize_cols(part)
    part.rename(columns={'subpartida': 'Subpartida', 'date': 'Date'}, inplace=True)
    if 'Date' in part.columns:
        part['Date'] = pd.to_datetime(part['Date'])
    part = clean_numeric_code(part, 'Subpartida')

    aranceles = pd.read_parquet(f'{base_path}efectivos.parquet')
    aranceles = normalize_cols(aranceles)
    aranceles.rename(columns={'subpartida': 'Subpartida', 'date': 'Date'}, inplace=True)
    if 'Date' in aranceles.columns:
        aranceles['Date'] = pd.to_datetime(aranceles['Date'])
    aranceles = clean_numeric_code(aranceles, 'Subpartida')

    return ligie, hts, sec301, sec232_db, tmec, part, aranceles, auxiliar

# -----------------------------------------------------------------------------
# 3. LÓGICA DE CÁLCULO
# -----------------------------------------------------------------------------

def get_10digit_children(hts_8_digit, sec232_db, auxiliar_db):
    hts_8 = str(hts_8_digit).strip()
    children_232 = sec232_db[
        (sec232_db['Code'].str.len() == 10) & 
        (sec232_db['Code'].str.startswith(hts_8))
    ].copy()
    
    if children_232.empty: 
        return pd.DataFrame()
        
    all_children = auxiliar_db[
        (auxiliar_db['Code'].str.len() == 10) & 
        (auxiliar_db['Code'].str.startswith(hts_8))
    ].copy()
    
    if all_children.empty:
        children_232['Description'] = children_232['Code'] + " - Opción específica"
        return children_232[['Code', 'Duty', 'Description']]
        
    sec232_unique = children_232[['Code', 'Duty']].drop_duplicates('Code')
    merged = all_children.merge(sec232_unique, on='Code', how='left')
    merged['Duty'] = merged['Duty'].fillna("0")
    merged['Description'] = merged['Code'] + " - " + merged['Description'].fillna("Descripción no disponible")
    
    return merged

def get_direct_matches(hts_8, sec232_db):
    for length in [8, 5, 4]:
        sub = hts_8[:length]
        matches = sec232_db[sec232_db['Code'] == sub]
        if not matches.empty:
            return sub, matches.iloc[0]['Duty']
    return None, 0.0

# -----------------------------------------------------------------------------
# 4. INTERFAZ
# -----------------------------------------------------------------------------

def show_hierarchy_item(label, value):
    val_str = str(value).strip()
    if val_str.lower() not in ['nan', 'none', 'null', '']:
        st.markdown(f"**{label}:** {val_str}")

# --- SIDEBAR ---
col_logo1, col_logo2 = st.sidebar.columns(2)
try:
    with col_logo1:
        st.image("logos/logo-01.png", use_container_width=True)
    with col_logo2:
        st.image("logos/logo-02.png", use_container_width=True)
except Exception as e:
    st.sidebar.warning("Logos no encontrados en ruta 'logos/'")

st.sidebar.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)

st.sidebar.header("🔍 Consulta")
hs6_input = st.sidebar.text_input("Subpartida (6 Dígitos):", max_chars=6, placeholder="Ej: 722020")
st.sidebar.markdown("---")

apply_mx = True
apply_us = True
target_country = "China"

# --- CARGA ---
try:
    ligie, hts, sec301, sec232_db, tmec, part, aranceles, auxiliar = load_data(target_country)
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

# --- ESTADO WIZARD ---
if 'wizard_step' not in st.session_state: st.session_state.wizard_step = 0 
if 'user_232_decisions' not in st.session_state: st.session_state.user_232_decisions = {}
if 'last_search' not in st.session_state: st.session_state.last_search = ""
if 'wizard_expanded' not in st.session_state: st.session_state.wizard_expanded = True

if hs6_input != st.session_state.last_search:
    st.session_state.last_search = hs6_input
    st.session_state.wizard_step = 0
    st.session_state.user_232_decisions = {}
    st.session_state.wizard_expanded = True

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
            st.markdown("<h2 style='color: #0F172A;'><span class='bandera'>🇲🇽</span> México</h2>", unsafe_allow_html=True)
            if 'Código' in ligie.columns:
                ligie_filtrado = ligie[ligie['Código'].str.startswith(hs6_input)].copy()
            else: ligie_filtrado = pd.DataFrame()

            if not ligie_filtrado.empty:
                try:
                    with st.expander("📂 Ley de Impuestos Generales de Importación y Exportación (LIGIE)", expanded=True):
                        row = ligie_filtrado.iloc[0]
                        show_hierarchy_item("Sección", row.get('Sección'))
                        show_hierarchy_item("Capítulo", row.get('Capítulo'))
                        show_hierarchy_item("Partida", row.get('Partida'))
                        show_hierarchy_item("Subpartida", row.get('Subpartida'))
                        show_hierarchy_item("Desdoblamiento", row.get('Desdoblamiento'))
                except: pass

                ligie_filtrado['Tasa General'] = ligie_filtrado['General'].apply(clean_percentage)
                
                df_display_mx = ligie_filtrado[['Código', 'Fracción', 'Tasa General']].copy()
                df_display_mx.columns = ['Código', 'Descripción', 'Arancel']
                st.dataframe(
                    df_display_mx.style
                    .format({'Arancel': '{:.2f}%'})
                    .set_properties(subset=['Descripción'], **{'white-space': 'normal', 'word-wrap': 'break-word'}),
                    use_container_width=True, hide_index=True
                )
            else:
                st.warning(f"No se encontró información en LIGIE para {hs6_input}")
            st.markdown("---")

        # =====================================================================
        # MÓDULO ESTADOS UNIDOS
        # =====================================================================
        if apply_us:
            st.markdown("<h2 style='color: #0F172A;'><span class='bandera'>🇺🇸</span> Estados Unidos</h2>", unsafe_allow_html=True)
            
            if 'Code' in hts.columns:
                hts_filtrado = hts[hts['Code'].str.startswith(hs6_input)].copy()
            else: hts_filtrado = pd.DataFrame()

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

                # --- NUEVA LÓGICA DE PARSEO HTS ---
                parsed_duties = hts_filtrado['General'].apply(parse_hts_duties)
                hts_filtrado['Math Base Duty'] = parsed_duties.apply(lambda x: x[0])
                hts_filtrado['General Duty'] = parsed_duties.apply(lambda x: x[1])
                hts_filtrado['Fixed Duty'] = parsed_duties.apply(lambda x: x[2])

                wizard_queue = []
                unique_hts_codes = hts_filtrado['Code'].unique()
                has_sec232_match = False  
                
                for code in unique_hts_codes:
                    children = get_10digit_children(code, sec232_db, auxiliar)
                    if not children.empty:
                        has_sec232_match = True
                        possible_duties = children['Duty'].unique()
                        if len(possible_duties) == 1 and possible_duties[0] != "Annex III":
                            st.session_state.user_232_decisions[code] = possible_duties[0]
                        else:
                            wizard_queue.append({'hts_8': code, 'type': '10_digit', 'children_df': children})
                    else:
                        match_code, duty = get_direct_matches(code, sec232_db)
                        if match_code:
                            has_sec232_match = True
                            if duty == "Annex III":
                                wizard_queue.append({'hts_8': code, 'type': 'annex_iii'})
                            else:
                                st.session_state.user_232_decisions[code] = duty
                
                if wizard_queue:
                    if st.session_state.wizard_step >= len(wizard_queue):
                        st.session_state.wizard_step = len(wizard_queue) - 1
                    
                    current_task = wizard_queue[st.session_state.wizard_step]
                    current_hts = current_task['hts_8']
                    
                    with st.expander("⚠️ Clasificación Requerida: Sección 232", expanded=st.session_state.wizard_expanded):
                        st.markdown("""
                        <div style='padding: 15px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 5px solid #2596be; border-radius: 6px; margin-bottom: 20px;'>
                            <p style='margin:0; font-size: 0.95rem; color: #0F172A;'>Seleccione las características del producto para determinar el arancel aplicable.</p>
                        </div>
                        """, unsafe_allow_html=True)

                        col_wiz_1, col_wiz_2 = st.columns([2.5, 1.5])
                        duty_result = "0"
                        is_annex_iii = False
                        
                        with col_wiz_1:
                            if current_task['type'] == '10_digit':
                                st.markdown(f"**Fracción {current_hts}:** Seleccione el producto específico:")
                                children_df = current_task['children_df']
                                descriptions = children_df['Description'].tolist()
                                selected_desc = st.radio("L", descriptions, key=f"rad_10_{current_hts}", label_visibility="collapsed")
                                
                                row_match = children_df[children_df['Description'] == selected_desc]
                                if not row_match.empty:
                                    duty_val = row_match.iloc[0]['Duty']
                                    if duty_val == "Annex III":
                                        is_annex_iii = True
                                    else:
                                        duty_result = duty_val
                            
                            elif current_task['type'] == 'annex_iii':
                                is_annex_iii = True
                            
                            if is_annex_iii:
                                if current_task['type'] == '10_digit':
                                    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                
                                st.markdown(f"**Fracción {current_hts} (Annex III):** ¿El metal fue fundido y moldeado en los Estados Unidos?")
                                usa_melted = st.radio("Melted", ["No (Otro país)", "Sí, en Estados Unidos"], key=f"rad_annex_{current_hts}", label_visibility="collapsed")
                                
                                # Extraemos la base de cálculo numérica en lugar de la representación visual
                                base_duty = hts_filtrado[hts_filtrado['Code'] == current_hts]['Math Base Duty'].iloc[0]
                                
                                if usa_melted == "Sí, en Estados Unidos":
                                    if base_duty < 10.0:
                                        calc_duty = 10.0 - base_duty
                                    else:
                                        calc_duty = 0.0
                                else:
                                    if base_duty < 15.0:
                                        calc_duty = 15.0 - base_duty
                                    else:
                                        calc_duty = 0.0
                                
                                duty_result = calc_duty

                        with col_wiz_2:
                            try:
                                d_val = float(duty_result)
                                val_str = f"{d_val:.2f}%"
                            except:
                                val_str = str(duty_result)
                                
                            st.markdown(f"""
                            <div class="metric-container" style="padding: 15px; border-top: 4px solid #2596be; text-align: center; margin-bottom: 15px;">
                                <div class="metric-title" style="margin-bottom: 8px;">Arancel 232 Calculado</div>
                                <div class="metric-value" style="font-size: 1.8rem;">{val_str}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c_prev, c_next = st.columns(2)
                            if st.session_state.wizard_step > 0:
                                if c_prev.button("Anterior", use_container_width=True):
                                    st.session_state.wizard_step -= 1
                                    st.rerun()
                            
                            is_last = (st.session_state.wizard_step == len(wizard_queue) - 1)
                            btn_label = "Listo" if is_last else "Siguiente"
                            
                            if c_next.button(btn_label, use_container_width=True):
                                st.session_state.user_232_decisions[current_hts] = duty_result
                                if not is_last:
                                    st.session_state.wizard_step += 1
                                else:
                                    st.session_state.wizard_expanded = False
                                st.rerun()
                            
                            st.markdown(f"<p style='text-align: center; color: #64748B; font-size: 0.85rem; margin-top: 10px;'>Fracción {st.session_state.wizard_step + 1} de {len(wizard_queue)}</p>", unsafe_allow_html=True)

                hts_filtrado = hts_filtrado.merge(sec301[['Code', 'Duty']], left_on='Code', right_on='Code', how='left')
                hts_filtrado.rename(columns={'Duty': '301 Duty'}, inplace=True)
                hts_filtrado['301 Duty'] = hts_filtrado['301 Duty'].fillna(0.0)
                hts_filtrado['is_tmec'] = hts_filtrado['Code'].isin(tmec['Code'])

                def calculate_232_row(row):
                    code = row['Code']
                    if code in st.session_state.user_232_decisions:
                        return st.session_state.user_232_decisions[code]
                    if wizard_queue and code == current_hts:
                        return duty_result
                    
                    match_code, duty = get_direct_matches(code, sec232_db)
                    if match_code and duty != "Annex III":
                        return duty
                    return 0.0

                hts_filtrado['232 Duty'] = hts_filtrado.apply(calculate_232_row, axis=1)
                
                # --- NUEVA LÓGICA TOTAL DUTY ADAPTATIVA ---
                def calc_total_row(row):
                    math_base = row['Math Base Duty']
                    
                    try: sec232 = float(row['232 Duty'])
                    except: sec232 = 0.0
                    
                    try: sec301 = float(row['301 Duty'])
                    except: sec301 = 0.0
                        
                    sum_pct = math_base + sec232 + sec301
                    fixed = row['Fixed Duty']
                    
                    # Si contiene Fixed, empaquetamos el componente porcentual entre paréntesis.
                    if pd.notna(fixed) and fixed:
                        if sum_pct > 0:
                            return f"{fixed} + {sum_pct:.2f}%"
                        else:
                            return fixed
                    else:
                        # Si no hay Fixed pero es 'Free' y no aplica ninguna otra tarifa
                        if str(row['General Duty']).lower() == 'free' and sum_pct == 0:
                            return "Free"
                        return f"{sum_pct:.2f}%"

                hts_filtrado['Total Duty'] = hts_filtrado.apply(calc_total_row, axis=1)
                
                def smart_pct(val):
                    try:
                        v = float(val)
                        return f"{v:.2f}%"
                    except: return str(val)

                if hts_filtrado['is_tmec'].any():
                    st.info("📄 Los registros marcados en verde representan fracciones incluidas en el TMEC.")
                
                # --- COLUMNAS DINÁMICAS ---
                cols_final = ['Code', 'Description']
                format_dict = {'301 Duty': '{:.2f}%'}
                
                if hts_filtrado['General Duty'].notna().any():
                    cols_final.append('General Duty')
                if hts_filtrado['Fixed Duty'].notna().any():
                    cols_final.append('Fixed Duty')
                
                # --- NUEVO CÓDIGO: Reemplazar "None" por texto vacío ---
                hts_filtrado['General Duty'] = hts_filtrado['General Duty'].fillna("")
                hts_filtrado['Fixed Duty'] = hts_filtrado['Fixed Duty'].fillna("")
                # -------------------------------------------------------
                
                cols_final.append('301 Duty')
                
                if has_sec232_match:
                    cols_final.append('232 Duty')
                    format_dict['232 Duty'] = smart_pct
                    
                cols_final.append('Total Duty')
                
                def highlight_tmec_row(row):
                    is_tmec = hts_filtrado.loc[row.name, 'is_tmec']
                    return ['background-color: #dcfce7; color: #166534'] * len(row) if is_tmec else [''] * len(row)

                st.dataframe(
                    hts_filtrado[cols_final].style.apply(highlight_tmec_row, axis=1).format(format_dict).set_properties(subset=['Description'], **{'white-space': 'normal', 'word-wrap': 'break-word'}),
                    use_container_width=True, hide_index=True
                )

                # --- ANÁLISIS HISTÓRICO ULTRA-RESILIENTE (Diseño NAFIN) ---
                st.markdown("<hr style='border-color: #E2E8F0; margin-top: 30px;'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color: #0F172A;'>Desempeño Histórico: México vs {target_country}</h3>", unsafe_allow_html=True)
                
                code_match = str(hs6_input).strip()
                
                df_part_sub = part[part['Subpartida'].astype(str).str.startswith(code_match)].copy()
                df_aranceles_sub = aranceles[aranceles['Subpartida'].astype(str).str.startswith(code_match)].copy()

                if not df_part_sub.empty:
                    df_part_sub = df_part_sub.groupby('Date', as_index=False).sum(numeric_only=True).sort_values('Date')
                
                if not df_aranceles_sub.empty:
                    df_aranceles_sub = df_aranceles_sub.groupby('Date', as_index=False).mean(numeric_only=True).sort_values('Date')

                rows_part = len(df_part_sub) > 0
                rows_ara = len(df_aranceles_sub) > 0
                
                if rows_part or rows_ara:
                    meses_es = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}

                    def get_series_stats(df, col):
                        valid = df.dropna(subset=[col, 'Date'])
                        if valid.empty:
                            return np.nan, np.nan, ""
                        last_row = valid.iloc[-1]
                        last_date = last_row['Date']
                        date_txt = f"{meses_es.get(last_date.month, '')} {last_date.year}"
                        last_val = last_row[col]
                        avg_12m = valid[col].iloc[-12:].mean()
                        return last_val, avg_12m, date_txt

                    def build_cell(val_mx, val_ch, is_curr, date_mx="", date_ch=""):
                        fmt = "${:,.2f}" if is_curr else "{:,.2f}%"
                        
                        def format_line(flag, val, d_txt):
                            if pd.isna(val):
                                return f"<span class='bandera' style='font-size:1.1rem;'>{flag}</span> <span style='color:#0F172A; font-weight:700;'>N/D</span>"
                            res = f"<span class='bandera' style='font-size:1.1rem;'>{flag}</span> <span style='color:#0F172A; font-weight:700;'>{fmt.format(val)}</span>"
                            if d_txt:
                                res += f" <span style='color:#64748B; font-size:0.8rem; font-weight:normal;'>({d_txt})</span>"
                            return res

                        l_mx = format_line('🇲🇽', val_mx, date_mx)
                        l_ch = format_line('🇨🇳', val_ch, date_ch)
                        return f"<div style='line-height: 1.6;'>{l_mx}<br>{l_ch}</div>"

                    money_last_mx = money_avg_mx = share_last_mx = share_avg_mx = np.nan
                    money_last_ch = money_avg_ch = share_last_ch = share_avg_ch = np.nan
                    money_date_mx = money_date_ch = share_date_mx = share_date_ch = ""

                    tariff_last_mx = tariff_avg_mx = tariff_last_ch = tariff_avg_ch = np.nan
                    tariff_date_mx = tariff_date_ch = ""

                    if rows_part:
                        for col in ['Mexico', 'Total', 'China', 'participacion_mexico', 'participacion_china']:
                            if col in df_part_sub.columns:
                                df_part_sub[col] = pd.to_numeric(df_part_sub[col], errors='coerce')

                        if 'Mexico' in df_part_sub.columns:
                            money_last_mx, money_avg_mx, money_date_mx = get_series_stats(df_part_sub, 'Mexico')
                        if 'China' in df_part_sub.columns:
                            money_last_ch, money_avg_ch, money_date_ch = get_series_stats(df_part_sub, 'China')
                        
                        if 'participacion_mexico' in df_part_sub.columns:
                            share_last_mx, share_avg_mx, share_date_mx = get_series_stats(df_part_sub, 'participacion_mexico')
                        if 'participacion_china' in df_part_sub.columns:
                            share_last_ch, share_avg_ch, share_date_ch = get_series_stats(df_part_sub, 'participacion_china')

                    if rows_ara:
                        for col in ['Mexico', 'China']:
                            if col in df_aranceles_sub.columns:
                                df_aranceles_sub[col] = pd.to_numeric(df_aranceles_sub[col], errors='coerce')
                        
                        if 'Mexico' in df_aranceles_sub.columns:
                            tariff_last_mx, tariff_avg_mx, tariff_date_mx = get_series_stats(df_aranceles_sub, 'Mexico')
                        if 'China' in df_aranceles_sub.columns:
                            tariff_last_ch, tariff_avg_ch, tariff_date_ch = get_series_stats(df_aranceles_sub, 'China')

                    val_money_last = build_cell(money_last_mx, money_last_ch, True, money_date_mx, money_date_ch)
                    val_money_avg = build_cell(money_avg_mx, money_avg_ch, True)
                    
                    val_share_last = build_cell(share_last_mx, share_last_ch, False, share_date_mx, share_date_ch)
                    val_share_avg = build_cell(share_avg_mx, share_avg_ch, False)

                    val_tariff_last = build_cell(tariff_last_mx, tariff_last_ch, False, tariff_date_mx, tariff_date_ch)
                    val_tariff_avg = build_cell(tariff_avg_mx, tariff_avg_ch, False)
                    
                    resumen_data = {
                        'Concepto': ["<strong>Último Dato Disponible</strong>", "<strong>Promedio 12 Meses</strong>"],
                        'Importaciones ($) desde': [val_money_last, val_money_avg],
                        'Participación': [val_share_last, val_share_avg],
                        'Arancel Efectivo': [val_tariff_last, val_tariff_avg]
                    }
                    
                    df_resumen = pd.DataFrame(resumen_data)
                    html_table = df_resumen.to_html(escape=False, index=False, classes='tabla-nafin', border=0)
                    
                    st.markdown(f"""
                    <div class='card-hover' style='padding: 20px; margin-bottom: 20px; border-top: 4px solid #2596be;'>
                        <style>
                            table.tabla-nafin {{ border: none !important; width: 100%; border-collapse: collapse; text-align: left; }}
                            .tabla-nafin th {{ border-bottom: 2px solid #E2E8F0 !important; border-top: none !important; padding: 10px 15px; color: #64748B; font-size: 0.85rem; text-transform: uppercase; font-weight: 700; text-align: left !important; }}
                            .tabla-nafin td {{ border-bottom: 1px solid #E2E8F0 !important; border-top: none !important; padding: 12px 15px; color: #475569; font-size: 0.95rem; vertical-align: middle; }}
                        </style>
                        {html_table}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_chart1, col_chart2 = st.columns(2)
                    
                    def prepare_chart_data(df, col_mx, col_ch, label_mx="México", label_ch="China"):
                        df_temp = df.copy()
                        df_temp['Date'] = pd.to_datetime(df_temp['Date'])
                        df_temp = df_temp.set_index('Date')
                        
                        if not df_temp.empty:
                            df_temp = df_temp.resample('MS').asfreq()
                            
                        data = pd.DataFrame(index=df_temp.index)
                        colors = []
                        
                        if col_mx in df_temp.columns and df_temp[col_mx].notna().any():
                            data[label_mx] = df_temp[col_mx]
                            colors.append("#2596be") 
                            
                        if col_ch in df_temp.columns and df_temp[col_ch].notna().any():
                            data[label_ch] = df_temp[col_ch]
                            colors.append("#008889") 
                            
                        return data, colors

                    def plot_altair_chart(chart_data, palette, y_title):
                        df_melted = chart_data.reset_index().melt('Date', var_name='País', value_name='Valor')
                        
                        chart = alt.Chart(df_melted).mark_line(
                            strokeWidth=3,
                            interpolate='linear'
                        ).encode(
                            x=alt.X('Date:T', title='', axis=alt.Axis(grid=False, labelColor='#64748B')),
                            y=alt.Y('Valor:Q', title=y_title, axis=alt.Axis(gridColor='#F1F5F9', labelColor='#94A3B8')),
                            color=alt.Color('País:N', scale=alt.Scale(domain=chart_data.columns.tolist(), range=palette), legend=alt.Legend(title=None, orient="bottom")),
                            tooltip=[alt.Tooltip('Date:T', title='Fecha', format='%Y-%m'), alt.Tooltip('País:N'), alt.Tooltip('Valor:Q', format='.2f')]
                        ).properties(
                            height=350
                        ).configure_view(
                            strokeWidth=0
                        )
                        
                        st.altair_chart(chart, use_container_width=True)

                    st.markdown("""
                    <style>
                        div:has(> div.element-container > div > div > div.chart-card-mx) {
                            background-color: #ffffff;
                            border: 1px solid #E2E8F0;
                            border-top: 4px solid #2596be !important;
                            padding: 24px;
                            border-radius: 12px;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
                            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
                        }
                        div:has(> div.element-container > div > div > div.chart-card-mx):hover {
                            transform: translateY(-2px) !important;
                            box-shadow: 0 10px 25px rgba(0,0,0,0.06) !important;
                        }

                        div:has(> div.element-container > div > div > div.chart-card-ch) {
                            background-color: #ffffff;
                            border: 1px solid #E2E8F0;
                            border-top: 4px solid #008889 !important;
                            padding: 24px;
                            border-radius: 12px;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
                            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
                        }
                        div:has(> div.element-container > div > div > div.chart-card-ch):hover {
                            transform: translateY(-2px) !important;
                            box-shadow: 0 10px 25px rgba(0,0,0,0.06) !important;
                        }
                                
                        .vega-embed summary {
                            display: none !important;
                        }
                    </style>
                    """, unsafe_allow_html=True)

                    with col_chart1:
                        with st.container():
                            st.markdown("<div class='chart-card-mx'></div>", unsafe_allow_html=True)
                            st.markdown("<div style='color: #0F172A; font-weight: 800; font-size: 1.1rem; margin-bottom: 15px;'>Participación de Mercado (%)</div>", unsafe_allow_html=True)
                            if rows_part:
                                chart_data, palette = prepare_chart_data(df_part_sub, 'participacion_mexico', 'participacion_china', "México", target_country)
                                if not chart_data.dropna(how='all').empty:
                                    plot_altair_chart(chart_data, palette, '% Participación')
                                else:
                                    st.info("Datos no disponibles.")
                            else:
                                st.info("Sin datos de participación.")

                    with col_chart2:
                        with st.container():
                            st.markdown("<div class='chart-card-ch'></div>", unsafe_allow_html=True)
                            st.markdown("<div style='color: #0F172A; font-weight: 800; font-size: 1.1rem; margin-bottom: 15px;'>Arancel Efectivo (%)</div>", unsafe_allow_html=True)
                            if rows_ara:
                                chart_data, palette = prepare_chart_data(df_aranceles_sub, 'Mexico', 'China', "México", target_country)
                                if not chart_data.dropna(how='all').empty:
                                    plot_altair_chart(chart_data, palette, '% Arancel')
                                else:
                                    st.info("Datos no disponibles.")
                            else:
                                st.info("Sin datos de aranceles.")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                else:
                    st.info(f"No hay registros históricos para la subpartida {hs6_input}.")

            else:
                st.warning(f"No se encontró información en HTS para {hs6_input}")

else:
    st.info("👈 Ingresa una subpartida para comenzar.")