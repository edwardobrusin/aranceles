# =============================================================================
# 1. PAQUETERÍAS
# =============================================================================
# Importamos Streamlit para la creación de la interfaz web interactiva.
import streamlit as st
# Importamos Pandas para la manipulación y análisis de datos estructurados (DataFrames).
import pandas as pd
# Importamos Numpy para operaciones matemáticas y manejo de valores nulos o condiciones.
import numpy as np
# Importamos Altair para la creación de visualizaciones y gráficas interactivas.
import altair as alt


# =============================================================================
# 2. CONFIGURACIONES GENERALES
# =============================================================================
# Configuramos la página de Streamlit para que use todo el ancho de la pantalla 
# y le asignamos un título a la pestaña del navegador.
st.set_page_config(layout="wide", page_title="Dashboard Arancelario")

# Mostramos el título principal visible en la interfaz web de la aplicación.
st.title("📊 Monitor de Comercio y Aranceles: México - EUA")

# Diccionario crudo que mapea los códigos arancelarios de la Sección 232 
# (Acero y Aluminio) con sus respectivas descripciones detalladas.
RAW_232_MAP = {
    # ACERO - Mapeos de códigos a descripciones
    "9903.81.87": "Productos básicos de hierro o acero (sin incluir derivados).",
    "9903.81.88": "Hierro o acero básico (Zona Franca antes mar-2025).",
    "9903.81.89": "Productos manufacturados de acero (lista original).",
    "9903.81.90": "Nuevos productos manufacturados de acero (Cap. 73).",
    "9903.81.91": "Nuevos productos manufacturados de acero (fuera Cap. 73).",
    "9903.81.92": "Productos de acero hechos en el extranjero (acero USA).",
    "9903.81.93": "Productos manufacturados de acero (viejos y nuevos) que estaban en una Zona Franca antes de marzo de 2025.",
    # ALUMINIO - Mapeos de códigos a descripciones
    "9903.85.02": "Productos básicos de aluminio (sin incluir derivados).",
    "9903.85.04": "Productos manufacturados de aluminio (lista original).",
    "9903.85.07": "Nuevos productos manufacturados de aluminio (Cap. 76).",
    "9903.85.08": "Nuevos productos manufacturados de aluminio (fuera Cap. 76)."
}

# Creamos un nuevo diccionario limpio donde a las llaves se les quitan los puntos 
# y los espacios, permitiendo una búsqueda más fácil y estandarizada.
SEC232_MAP = {k.replace('.', '').strip(): v for k, v in RAW_232_MAP.items()}


# =============================================================================
# 3. DEFINICIONES (TODAS LAS FUNCIONES Y FÓRMULAS)
# =============================================================================

# Función para limpiar valores que representan porcentajes.
def clean_percentage(val):
    # Si el valor es nulo (NaN), regresamos 0.0
    if pd.isna(val): return 0.0
    # Convertimos a string, quitamos espacios en los extremos y pasamos a minúsculas
    val_str = str(val).strip().lower()
    # Si el valor es una de estas palabras que indican exención o vacío, regresamos 0.0
    if val_str in ['ex.', 'ex', 'libre', 'free', 'n/a', '-', '']: return 0.0
    try:
        # Mantenemos únicamente los caracteres que sean dígitos numéricos o puntos decimales
        clean = ''.join(c for c in val_str if c.isdigit() or c == '.')
        # Convertimos el string resultante a un número flotante, si está vacío regresamos 0.0
        return float(clean) if clean else 0.0
    # Si ocurre cualquier error en la conversión, devolvemos 0.0
    except: return 0.0

# Función para limpiar y estandarizar los nombres de las columnas de un DataFrame
def normalize_cols(df):
    # Quitamos espacios en blanco al inicio y al final de los nombres de todas las columnas
    df.columns = df.columns.str.strip()
    # Retornamos el DataFrame modificado
    return df

# Función para limpiar columnas que contienen códigos numéricos
def clean_numeric_code(df, col_name):
    # Verificamos si la columna existe en el DataFrame
    if col_name in df.columns:
        # Convertimos a string, quitamos espacios y eliminamos los puntos
        df[col_name] = df[col_name].astype(str).str.strip().str.replace('.', '', regex=False)
    # Retornamos el DataFrame modificado
    return df

# Función para cargar todas las bases de datos. 
# Mantiene la caché en memoria para no recargar si no cambian los parámetros.
# (Nota: El doble decorador se mantiene para no omitir ningún caracter original)
@st.cache_data(show_spinner="Cargando bases de datos... Por favor espere.")
@st.cache_data(show_spinner="Cargando bases de datos... Por favor espere.")
def load_data(target_country="China"):
    # Definimos la ruta base donde se encuentran los archivos Parquet
    base_path = 'data/parquet/'
    
    # --- Carga de LIGIE ---
    # Leemos la base de datos LIGIE
    ligie = pd.read_parquet(f'{base_path}LIGIE.parquet')
    # Normalizamos los nombres de sus columnas
    ligie = normalize_cols(ligie)
    # Limpiamos la columna 'Código' quitando puntos y espacios
    ligie = clean_numeric_code(ligie, 'Código')
    
    # --- Carga de HTS ---
    # Leemos la base de datos HTS
    hts = pd.read_parquet(f'{base_path}HTS.parquet')
    # Normalizamos los nombres de sus columnas
    hts = normalize_cols(hts)
    # Limpiamos la columna 'Code'
    hts = clean_numeric_code(hts, 'Code')
    # Filtramos la tabla HTS para quedarnos solo con los códigos de exactamente 8 caracteres
    hts = hts[hts['Code'].str.len() == 8].copy()

    # --- Carga de AUXILIARES (Sección 301) ---
    # Leemos la base de datos Sec_301
    sec301 = pd.read_parquet(f'{base_path}Sec_301.parquet')
    # Normalizamos columnas
    sec301 = normalize_cols(sec301)
    # Limpiamos la columna 'Code'
    sec301 = clean_numeric_code(sec301, 'Code')
    # Aplicamos la limpieza de porcentajes a la columna 'Duty'
    sec301['Duty'] = sec301['Duty'].apply(clean_percentage)

    # --- Carga de ACERO Y ALUMINIO (Sección 232) ---
    # Leemos la base de Acero
    acero = pd.read_parquet(f'{base_path}Acero.parquet')
    # Normalizamos columnas
    acero = normalize_cols(acero)
    # Limpiamos códigos y encabezados
    acero = clean_numeric_code(acero, 'Code')
    acero = clean_numeric_code(acero, 'Heading')
    # Llenamos nulos con "0", pasamos a string y quitamos espacios en la columna 'Duty'
    acero['Duty'] = acero['Duty'].fillna("0").astype(str).str.strip()
    # Asignamos una etiqueta indicando que es tipo 'Acero'
    acero['Type'] = 'Acero'
    
    # Leemos la base de Aluminio
    aluminio = pd.read_parquet(f'{base_path}Aluminio.parquet')
    # Normalizamos columnas
    aluminio = normalize_cols(aluminio)
    # Limpiamos códigos y encabezados
    aluminio = clean_numeric_code(aluminio, 'Code')
    aluminio = clean_numeric_code(aluminio, 'Heading')
    # Llenamos nulos con "0", pasamos a string y quitamos espacios en 'Duty'
    aluminio['Duty'] = aluminio['Duty'].fillna("0").astype(str).str.strip()
    # Asignamos una etiqueta indicando que es tipo 'Aluminio'
    aluminio['Type'] = 'Aluminio'
    
    # Concatenamos (unimos) ambas tablas de la Sección 232 en un solo DataFrame
    sec232_db = pd.concat([acero, aluminio], ignore_index=True)

    # --- Carga de TMEC ---
    # Leemos la base TMEC
    tmec = pd.read_parquet(f'{base_path}TMEC.parquet')
    # Normalizamos columnas
    tmec = normalize_cols(tmec)
    # Limpiamos la columna 'Code'
    tmec = clean_numeric_code(tmec, 'Code')

    # --- Carga de Base Auxiliar ---
    # Leemos la base Auxiliar
    auxiliar = pd.read_parquet(f'{base_path}Auxiliar.parquet')
    # Normalizamos columnas
    auxiliar = normalize_cols(auxiliar)
    # Limpiamos la columna 'Code'
    auxiliar = clean_numeric_code(auxiliar, 'Code')

    # --- Carga de HISTÓRICOS (Participación y Aranceles Efectivos) ---
    # Leemos la base de Participación
    part = pd.read_parquet(f'{base_path}Participación.parquet')
    # Normalizamos columnas
    part = normalize_cols(part)
    # Si existe la columna Date, la convertimos a formato datetime de Pandas
    if 'Date' in part.columns:
        part['Date'] = pd.to_datetime(part['Date'])
    # Limpiamos el código numérico de 'Subpartida'
    part = clean_numeric_code(part, 'Subpartida')

    # Leemos la base de Aranceles Efectivos
    aranceles = pd.read_parquet(f'{base_path}Aranceles_Efectivos.parquet')
    # Normalizamos columnas
    aranceles = normalize_cols(aranceles)
    # Si existe la columna Date, la convertimos a formato datetime
    if 'Date' in aranceles.columns:
        aranceles['Date'] = pd.to_datetime(aranceles['Date'])
    # Limpiamos el código numérico de 'Subpartida'
    aranceles = clean_numeric_code(aranceles, 'Subpartida')

    # Retornamos todas las bases cargadas y procesadas
    return ligie, hts, sec301, sec232_db, tmec, part, aranceles, auxiliar


# Función para obtener los códigos de 10 dígitos "hijos" de un código de 8 dígitos
def get_10digit_children(hts_8_digit, sec232_db, auxiliar_db):
    # Convertimos el código HTS de 8 dígitos a string y quitamos espacios
    hts_8 = str(hts_8_digit).strip()
    # Filtramos la base 232: buscando códigos que tengan exactamente 10 de longitud y empiecen con nuestro hts_8
    children_232 = sec232_db[
        (sec232_db['Code'].str.len() == 10) & 
        (sec232_db['Code'].str.startswith(hts_8))
    ].copy()
    # Si no encuentra nada, devuelve un DataFrame vacío
    if children_232.empty: return pd.DataFrame()
    # Extraemos solo los códigos únicos encontrados
    unique_children_codes = children_232[['Code']].drop_duplicates()
    # Hacemos un cruce (merge) por la izquierda con la base auxiliar para traer sus descripciones
    merged = unique_children_codes.merge(auxiliar_db[['Code', 'Description']], on='Code', how='left')
    # Si alguna no tiene descripción, le ponemos un texto por defecto
    merged['Description'] = merged['Description'].fillna("Descripción no disponible")
    # Retornamos el DataFrame con los hijos y sus descripciones
    return merged

# Función para obtener el arancel exacto dado un código y un encabezado (Heading)
def get_duty_for_selection(code, heading_clean, sec232_db):
    # Buscamos en la base 232 el registro que coincida exactamente con el Código y el Encabezado
    match = sec232_db[
        (sec232_db['Code'] == code) & 
        (sec232_db['Heading'] == heading_clean)
    ]
    # Si se encontró coincidencia, se extrae el valor del arancel (Duty) del primer registro
    if not match.empty: return match.iloc[0]['Duty']
    # Si no hay coincidencia, devuelve "0"
    return "0"

# Función para buscar coincidencias directas en niveles más generales (8, 6 o 4 dígitos)
def get_direct_matches(hts_8, sec232_db):
    # Itera intentando coincidir la cadena en longitudes de 8, 6 y 4 caracteres
    for length in [8, 6, 4]:
        # Corta el string hts_8 según la longitud actual del ciclo
        sub = hts_8[:length]
        # Busca coincidencias exactas del subcódigo en la base 232
        matches = sec232_db[sec232_db['Code'] == sub]
        # Si encuentra algo, retorna el subcódigo exitoso y los registros correspondientes
        if not matches.empty:
            return sub, matches
    # Si después de iterar todo no encontró nada, retorna nulo y un DataFrame vacío
    return None, pd.DataFrame()

# Función visual que imprime un elemento de jerarquía (texto en negrita con su valor)
def show_hierarchy_item(label, value):
    # Convertimos el valor a string y quitamos espacios
    val_str = str(value).strip()
    # Solo lo imprime si el valor no es nulo o vacío
    if val_str.lower() != 'nan' and val_str != '':
        # Renderiza en Streamlit usando Markdown
        st.markdown(f"**{label}:** {val_str}")

# Función para calcular el arancel de la sección 232 fila por fila (Extraída para lógica limpia)
def calculate_232_row(row):
    # Obtenemos el código de la fila actual
    code = row['Code']
    # Si el usuario ya tomó una decisión en el Wizard sobre este código, devolvemos esa decisión
    if code in st.session_state.user_232_decisions:
        return st.session_state.user_232_decisions[code]
    # Si no, buscamos si hay una coincidencia directa en la base 232
    match_code, matches_df = get_direct_matches(code, sec232_db)
    # Si encontramos una coincidencia directa y es única, devolvemos su arancel
    if match_code and len(matches_df) == 1:
        return matches_df.iloc[0]['Duty']
    # Si es ambigua o no hay, devolvemos 0.0 por defecto
    return 0.0

# Función para calcular el arancel total sumando todos los tipos de aranceles (Extraída para lógica limpia)
def calc_total_row(row):
    # Sumamos los aranceles base (General, 301, Recíproco y Fentanilo)
    base_sum = row['General Duty'] + row['301 Duty'] + row['Reciprocal Duty'] + row['Fentanyl Duty']
    # Obtenemos el valor del arancel 232 calculado previamente
    duty_232_val = row['232 Duty']
    try:
        # Intentamos convertir el arancel 232 a flotante para hacer la suma matemática
        d232_float = float(duty_232_val)
        return base_sum + d232_float
    except:
        # Si el 232 no es un número puro (ej. texto compuesto), devolvemos la fórmula en formato texto
        return f"{base_sum:.2f}% + {duty_232_val}"

# Función para formatear inteligentemente los porcentajes (Extraída para lógica limpia)
def smart_pct(val):
    try:
        # Intenta convertir el valor a flotante
        v = float(val)
        # Si puede, lo retorna con dos decimales y un símbolo de porcentaje
        return f"{v:.2f}%"
    except: 
        # Si falla (ej. si es un texto con símbolos), lo retorna como string original
        return str(val)

# Función para resaltar filas que pertenecen al TMEC (Extraída para lógica limpia)
def highlight_tmec_row(row):
    # Consulta en el DataFrame global si el código de esta fila tiene la bandera is_tmec como True
    is_tmec = hts_filtrado.loc[row.name, 'is_tmec']
    # Si es True, retorna estilos CSS verdes para toda la longitud de la fila, de lo contrario devuelve estilos vacíos
    return ['background-color: #d4edda; color: #155724'] * len(row) if is_tmec else [''] * len(row)

# Función para combinar dos valores de la tabla comparativa (México vs China) en un string (Extraída para lógica limpia)
def combine_vals(val_mx, val_ch, is_curr=True):
    # Si ambos valores son nulos, regresamos "N/D" (No Disponible)
    if pd.isna(val_mx) and pd.isna(val_ch): return "N/D"
    # Aseguramos que si uno es nulo, pase como 0, si no mantiene su valor
    v_mx = val_mx if pd.notna(val_mx) else 0
    v_ch = val_ch if pd.notna(val_ch) else 0
    # Determinamos el formato de salida según si es moneda (True) o porcentaje (False)
    fmt = "${:,.2f}" if is_curr else "{:,.2f}%"
    # Retornamos el string combinado con las banderas e inyecciones de valores
    return f"🇲🇽 {fmt.format(v_mx)} | 🇨🇳 {fmt.format(v_ch)}"

# Función que prepara los datos históricos para ser graficados (Extraída para lógica limpia)
def prepare_chart_data(df, col_mx, col_ch, label_mx="México", label_ch="China"):
    # Hacemos una copia del DataFrame de entrada para no modificar el original
    df_temp = df.copy()
    
    # 1. Asegurar que haya una fecha válida y usarla como índice de Pandas
    df_temp['Date'] = pd.to_datetime(df_temp['Date'])
    df_temp = df_temp.set_index('Date')
    
    # 2. Resamplear mes a mes ('MS') para detectar huecos en el tiempo.
    # Rellena meses faltantes con NaNs forzando el "corte" de línea en la gráfica.
    # Los 0s existentes se mantienen como 0s.
    if not df_temp.empty:
        df_temp = df_temp.resample('MS').asfreq()
        
    # Creamos un nuevo DataFrame vacío compartiendo el índice de fechas
    data = pd.DataFrame(index=df_temp.index)
    # Inicializamos una lista vacía para guardar los colores de las líneas
    colors = []
    
    # Agregar México si la columna existe y si tiene al menos un dato que no sea NaN
    if col_mx in df_temp.columns and df_temp[col_mx].notna().any():
        data[label_mx] = df_temp[col_mx]
        colors.append("#006400") # Asignamos color Verde para México
        
    # Agregar China si la columna existe y si tiene al menos un dato que no sea NaN
    if col_ch in df_temp.columns and df_temp[col_ch].notna().any():
        data[label_ch] = df_temp[col_ch]
        colors.append("#FF0000") # Asignamos color Rojo para China
        
    # Retornamos el dataset construido y su paleta de colores
    return data, colors

# Función auxiliar para graficar utilizando la librería Altair (Extraída para lógica limpia)
def plot_altair_chart(chart_data, palette, y_title):
    # Convertimos los datos de formato "ancho" a formato "largo" necesario para que Altair entienda las series
    df_melted = chart_data.reset_index().melt('Date', var_name='País', value_name='Valor')
    
    # Inicializamos el objeto de Gráfica definiendo el dataset y que será una gráfica de líneas
    chart = alt.Chart(df_melted).mark_line(
        point=True, # ¡Clave! Muestra el punto y no solo la línea, útil si hay 1 solo dato solitario
        interpolate='linear' # Define el tipo de conexión entre puntos (recta)
    ).encode(
        # Asignamos el eje X a la columna de fechas
        x=alt.X('Date:T', title='Fecha'),
        # Asignamos el eje Y a la columna de valores con el título proporcionado
        y=alt.Y('Valor:Q', title=y_title),
        # Asignamos el color dependiendo de la columna 'País', aplicando nuestra paleta de colores
        color=alt.Color('País:N', scale=alt.Scale(domain=chart_data.columns.tolist(), range=palette)),
        # Configuramos los tooltips al pasar el mouse encima de un punto
        tooltip=['Date:T', 'País:N', 'Valor:Q']
    ).interactive() # Hacemos la gráfica interactiva (zoom/pan)
    
    # Desplegamos la gráfica en la interfaz web de Streamlit ocupando todo el ancho del contenedor
    st.altair_chart(chart, use_container_width=True)


# =============================================================================
# 4. LÓGICA Y PROCEDIMIENTO (TRABAJO DURO, SIN DEFs)
# =============================================================================

# --- SIDEBAR ---
# Agregamos un encabezado a la barra lateral (Sidebar)
st.sidebar.header("🔍 Consulta")
# Creamos un campo de texto en la barra lateral para ingresar la subpartida de 6 dígitos
hs6_input = st.sidebar.text_input("Subpartida (6 Dígitos):", max_chars=6, placeholder="Ej: 722020")
# Trazamos una línea divisoria en la barra lateral
st.sidebar.markdown("---")

# Agregamos un subtítulo a la barra lateral para los filtros de países aplicadores
st.sidebar.markdown("### País aplicador del arancel:")
# Checkbox para determinar si se busca y procesa la información para México, activado por defecto
apply_mx = st.sidebar.checkbox("México", value=True)
# Checkbox para determinar si se busca y procesa la información para Estados Unidos, activado por defecto
apply_us = st.sidebar.checkbox("Estados Unidos", value=True)
# Trazamos otra línea divisoria en la barra lateral
st.sidebar.markdown("---")

# Agregamos un subtítulo para definir el país objetivo/gravado
st.sidebar.markdown("### País gravado:")
# Creamos un menú desplegable para elegir al país gravado, con "China" como única/primera opción por ahora
target_country = st.sidebar.selectbox("Seleccione país de origen:", ["China"])

# --- CARGA DE DATOS ---
try:
    # Intentamos ejecutar la función de carga pasándole el país seleccionado
    # Desempaquetamos todas las bases que regresa la función a sus respectivas variables
    ligie, hts, sec301, sec232_db, tmec, part, aranceles, auxiliar = load_data(target_country)
except Exception as e:
    # Si ocurre un error durante la carga, mostramos el error en pantalla de forma gráfica
    st.error(f"Error cargando datos: {e}")
    # Detenemos inmediatamente la ejecución de todo el script restante
    st.stop()

# --- ESTADOS DE LA SESIÓN (WIZARD) ---
# Inicializamos el paso actual del "Wizard" de preguntas de la Sección 232 en el estado de Streamlit
if 'wizard_step' not in st.session_state: st.session_state.wizard_step = 0 
# Inicializamos un diccionario para guardar las decisiones de aranceles 232 que tome el usuario
if 'user_232_decisions' not in st.session_state: st.session_state.user_232_decisions = {}
# Inicializamos el registro de la última búsqueda realizada para comparaciones
if 'last_search' not in st.session_state: st.session_state.last_search = ""
# Inicializamos el estado que controla si el menú desplegable (expander) del Wizard está abierto o cerrado
if 'wizard_expanded' not in st.session_state: st.session_state.wizard_expanded = True

# Verificamos si la búsqueda actual en el campo de texto es diferente a la última realizada
if hs6_input != st.session_state.last_search:
    # Si es diferente, actualizamos la última búsqueda
    st.session_state.last_search = hs6_input
    # Reiniciamos el paso del Wizard al inicio
    st.session_state.wizard_step = 0
    # Limpiamos las decisiones previas del usuario del estado
    st.session_state.user_232_decisions = {}
    # Volvemos a expandir el acordeón del Wizard por defecto para la nueva búsqueda
    st.session_state.wizard_expanded = True

# --- LÓGICA PRINCIPAL DEL DASHBOARD ---
# Ejecutamos toda esta lógica si el usuario presiona el botón "Buscar" o si el campo tiene algún valor
if st.sidebar.button("Buscar") or hs6_input:
    # Limpiamos los espacios en blanco del inicio o final del input de búsqueda
    hs6_input = hs6_input.strip()
    
    # Comprobamos si la longitud de la cadena es menor a 6 caracteres
    if len(hs6_input) < 6:
        # Mostramos una alerta en pantalla pidiendo los 6 dígitos
        st.warning("Por favor ingresa 6 dígitos.")
    else:
        
        # =====================================================================
        # MÓDULO MÉXICO
        # =====================================================================
        # Si el usuario dejó activa la casilla de "México"
        if apply_mx:
            # Imprimimos el encabezado principal para México
            st.header("🇲🇽 México")
            # Si la columna 'Código' sí existe en nuestra tabla LIGIE
            if 'Código' in ligie.columns:
                # Filtramos LIGIE para quedarnos solo con las filas cuyo código empiece con lo ingresado
                ligie_filtrado = ligie[ligie['Código'].str.startswith(hs6_input)].copy()
            else: 
                # Si no existe la columna, creamos un DataFrame vacío para evitar errores posteriores
                ligie_filtrado = pd.DataFrame()

            # Si después de filtrar sí quedaron datos en la tabla
            if not ligie_filtrado.empty:
                try:
                    # Creamos un menú colapsable (expander) abierto por defecto para mostrar jerarquías
                    with st.expander("📂 Ley de Impuestos Generales de Importación y Exportación (LIGIE)", expanded=True):
                        # Tomamos la primera fila del conjunto filtrado como referencia general
                        row = ligie_filtrado.iloc[0]
                        # Mostramos de forma gráfica los metadatos de clasificación arancelaria de México
                        show_hierarchy_item("Sección", row.get('Sección'))
                        show_hierarchy_item("Capítulo", row.get('Capítulo'))
                        show_hierarchy_item("Partida", row.get('Partida'))
                        show_hierarchy_item("Subpartida", row.get('Subpartida'))
                        show_hierarchy_item("Desdoblamiento", row.get('Desdoblamiento'))
                # Ignoramos silenciosamente si algo falla imprimiendo jerarquías
                except: pass

                # Aplicamos limpieza a la columna 'General' para convertir sus aranceles en flotantes limpios
                ligie_filtrado['Tasa General'] = ligie_filtrado['General'].apply(clean_percentage)
                # Calculamos el promedio matemático de la nueva columna de tasas
                avg_rate = ligie_filtrado['Tasa General'].mean()

                # Dividimos el espacio de la interfaz en dos columnas asimétricas (1 parte y 4 partes de ancho)
                col_metrics, col_table = st.columns([1, 4])
                # Dentro de la columna más pequeña (izquierda)
                with col_metrics:
                    # Mostramos una métrica grande y visual del Arancel Promedio LIGIE
                    st.metric("Arancel Promedio LIGIE", f"{avg_rate:,.2f}% 🇨🇳")
                
                # Dentro de la columna más ancha (derecha)
                with col_table:
                    # Extraemos solamente las columnas que nos interesan para visualizarlas
                    df_display_mx = ligie_filtrado[['Código', 'Fracción', 'Tasa General']].copy()
                    # Renombramos las columnas para que sean presentables
                    df_display_mx.columns = ['Código', 'Descripción', 'Arancel']
                    # Mostramos un DataFrame interactivo en la pantalla con los datos procesados
                    st.dataframe(
                        # Aplicamos estilos: Formateamos el arancel como porcentaje a 2 decimales
                        df_display_mx.style
                        .format({'Arancel': '{:.2f}%'})
                        # Configuramos las celdas de 'Descripción' para que hagan salto de línea si son muy largas
                        .set_properties(subset=['Descripción'], **{'white-space': 'normal', 'word-wrap': 'break-word'}),
                        # Configuramos para que ocupe todo el ancho disponible y ocultamos la columna índice numérico de Pandas
                        use_container_width=True, hide_index=True
                    )
            else:
                # Si el filtro dejó la tabla vacía, mostramos advertencia amarilla indicando que no hay datos
                st.warning(f"No se encontró información en LIGIE para {hs6_input}")
            # Línea divisoria de fin de sección México
            st.markdown("---")

        # =====================================================================
        # MÓDULO ESTADOS UNIDOS
        # =====================================================================
        # Si el usuario dejó activa la casilla de "Estados Unidos"
        if apply_us:
            # Imprimimos el encabezado principal para Estados Unidos
            st.header("🇺🇸 Estados Unidos")
            
            # Si la columna 'Code' existe en la base HTS
            if 'Code' in hts.columns:
                # Filtramos los datos de Estados Unidos que empiecen con los 6 dígitos ingresados
                hts_filtrado = hts[hts['Code'].str.startswith(hs6_input)].copy()
            else: 
                # Si no, inicializamos vacío
                hts_filtrado = pd.DataFrame()

            # Si encontramos datos tras filtrar HTS
            if not hts_filtrado.empty:
                try:
                    # Creamos expander para los metadatos de HTS
                    with st.expander("📂 Harmonized Tariff Schedule (HTS)", expanded=True):
                        # Tomamos la primera fila como referencia jerárquica
                        row = hts_filtrado.iloc[0]
                        # Mostramos jerarquías del sistema americano
                        show_hierarchy_item("Section", row.get('Section'))
                        show_hierarchy_item("Chapter", row.get('Chapter'))
                        show_hierarchy_item("Heading", row.get('Heading'))
                        show_hierarchy_item("Breakdown", row.get('Breakdown'))
                        show_hierarchy_item("Subheading", row.get('Subheading'))
                except: pass

                # --- LÓGICA DEL WIZARD SECCIÓN 232 ---
                # Creamos una lista vacía que servirá de "fila" de tareas para el Wizard interactivo
                wizard_queue = []
                # Obtenemos todos los códigos únicos de 8 dígitos de la tabla filtrada actual
                unique_hts_codes = hts_filtrado['Code'].unique()
                
                # Iteramos sobre cada código único encontrado
                for code in unique_hts_codes:
                    # Buscamos si tiene "hijos" de 10 dígitos en la base de la Sección 232
                    children = get_10digit_children(code, sec232_db, auxiliar)
                    # Si se encontraron hijos de 10 dígitos, la decisión no es trivial
                    if not children.empty:
                        # Añadimos una tarea tipo '10_digit' a la fila de tareas del Wizard
                        wizard_queue.append({'hts_8': code, 'type': '10_digit', 'children_df': children})
                    else:
                        # Si no hay hijos a 10 dígitos, verificamos si hay una coincidencia directa del código
                        match_code, matches_df = get_direct_matches(code, sec232_db)
                        # Si encontramos coincidencias pero en múltiples "Headings" (Ambigüedad), el sistema no puede decidir solo
                        if match_code and len(matches_df['Heading'].unique()) > 1:
                            # Añadimos una tarea tipo 'direct_ambiguous' al Wizard para preguntar al usuario
                            wizard_queue.append({
                                'hts_8': code, 
                                'type': 'direct_ambiguous', 
                                'match_code': match_code, 
                                'matches_df': matches_df
                            })
                
                # Si luego de evaluar los códigos resulta que SÍ se agregaron preguntas al Wizard
                if wizard_queue:
                    # Validamos por seguridad que el paso actual no exceda el número de preguntas existentes
                    if st.session_state.wizard_step >= len(wizard_queue):
                        st.session_state.wizard_step = len(wizard_queue) - 1
                    
                    # Identificamos cuál es la tarea "actual" que debemos procesar según el estado
                    current_task = wizard_queue[st.session_state.wizard_step]
                    # Obtenemos el código sobre el cual tratamos de resolver la ambigüedad
                    current_hts = current_task['hts_8']
                    
                    # Creamos un contenedor (expander) interactivo y de alerta
                    with st.expander("⚠️ Atención: Algunas de las fracciones arancelarias son elegibles para aranceles de la Sección 232", expanded=st.session_state.wizard_expanded):
                        # Dividimos el Wizard en dos columnas internas
                        col_wiz_1, col_wiz_2 = st.columns([3, 1])
                        # Asignamos un arancel inicial por defecto
                        duty_result = "0"
                        
                        # Trabajamos dentro de la primera columna (lado izquierdo del Wizard)
                        with col_wiz_1:
                            # Si la tarea actual requiere discriminar entre hijos de 10 dígitos
                            if current_task['type'] == '10_digit':
                                # Mostramos instrucción textual al usuario
                                st.markdown(f"Para la fracción **{current_hts}**, seleccione el producto de interés:")
                                # Extraemos el DataFrame de los hijos pre-calculado
                                children_df = current_task['children_df']
                                # Obtenemos una lista de descripciones limpias de las opciones
                                descriptions = children_df['Description'].tolist()
                                # Creamos un bloque de Radio Buttons (botones circulares) con las descripciones para seleccionar uno
                                selected_desc = st.radio("L", descriptions, key=f"rad_10_{current_hts}", label_visibility="collapsed")
                                
                                # Buscamos la fila original en la tabla de hijos que empata con la descripción seleccionada por el usuario
                                row_match = children_df[children_df['Description'] == selected_desc]
                                # Extraemos el código seleccionado subyacente de la fila
                                selected_code = row_match.iloc[0]['Code'] if not row_match.empty else ""
                                
                                # Con el código seleccionado a 10 dígitos, buscamos ahora sus reglas 232
                                matches_10 = sec232_db[sec232_db['Code'] == selected_code]
                                # A veces, incluso a 10 dígitos, hay múltiples "Headings" conflictivos. Comprobamos esto
                                if len(matches_10['Heading'].unique()) > 1:
                                    # Dibujamos línea para separar la segunda pregunta de desempate
                                    st.markdown("---")
                                    # Instrucción para elegir la categoría final
                                    st.markdown(f"Para el producto seleccionado, seleccione la categoría correcta:")
                                    # Preparamos las opciones visuales uniendo el código de Heading con su descripción mapeada del diccionario 232
                                    heading_opts = [f"{h}|{SEC232_MAP.get(h, f'Opción ({h}')}" for h in matches_10['Heading'].unique()]
                                    # Separamos sólo la descripción en texto para mostrarla bonita al usuario
                                    display_headings = [o.split("|")[1] for o in heading_opts]
                                    # Generamos los Radio Buttons de desempate del Heading
                                    sel_head_desc = st.radio("C", display_headings, key=f"rad_h_{current_hts}", label_visibility="collapsed")
                                    
                                    # Inicializamos variable vacía para guardar el código Heading a buscar
                                    sel_head_code = ""
                                    # Hacemos loop inverso: buscamos qué código originó el texto que eligió el usuario
                                    for o in heading_opts:
                                        if o.split("|")[1] == sel_head_desc:
                                            sel_head_code = o.split("|")[0]
                                            break
                                    # Finalmente obtenemos el arancel exacto usando el código y el heading seleccionado
                                    duty_result = get_duty_for_selection(selected_code, sel_head_code, sec232_db)
                                # Si no hubo ambigüedad a nivel Heading, se extrae directamente
                                elif len(matches_10) == 1:
                                    duty_result = matches_10.iloc[0]['Duty']
                            
                            # Si la tarea actual es ambigüedad directa desde los 8 dígitos (sin hijos 10 dígitos)
                            elif current_task['type'] == 'direct_ambiguous':
                                # Recuperamos las coincidencias previas
                                matches_df = current_task['matches_df']
                                # Preguntamos la categoría (Heading) al usuario
                                st.markdown(f"Para la fracción **{current_hts}**, seleccione la categoría correcta:")
                                # Construimos las opciones mezclando el código de Heading y su mapeo de texto humano
                                heading_opts = [f"{h}|{SEC232_MAP.get(h, f'Opción ({h}')}" for h in matches_df['Heading'].unique()]
                                # Extraemos solo la parte de texto bonito
                                display_headings = [o.split("|")[1] for o in heading_opts]
                                # Mostramos radio buttons
                                sel_head_desc = st.radio("C", display_headings, key=f"rad_dir_{current_hts}", label_visibility="collapsed")
                                
                                # Loop inverso para descubrir cuál fue el código Heading original
                                sel_head_code = ""
                                for o in heading_opts:
                                    if o.split("|")[1] == sel_head_desc:
                                        sel_head_code = o.split("|")[0]
                                        break
                                # Obtenemos el arancel exacto a partir de ese match original y el código Heading
                                duty_result = get_duty_for_selection(current_task['match_code'], sel_head_code, sec232_db)

                        # Trabajamos dentro de la segunda columna (lado derecho del Wizard)
                        with col_wiz_2:
                            # Intentamos parsear a flotante el arancel resuelto
                            try:
                                d_val = float(duty_result)
                                # Mostramos visualmente el resultado numérico en vivo del arancel 232
                                st.metric("Arancel 232", f"{d_val:.2f}%")
                            except:
                                # Si falló (es texto compuesto o no numérico), se imprime textual
                                st.metric("Arancel 232", str(duty_result))
                            
                            # Creamos dos mini-columnas para los botones de navegación anterior y siguiente
                            c_prev, c_next = st.columns(2)
                            # Sólo mostramos el botón anterior si no estamos en el primer paso
                            if st.session_state.wizard_step > 0:
                                # Si se presiona el botón "Anterior"
                                if c_prev.button("⬅️ Anterior"):
                                    # Reducimos en 1 el índice del estado global del Wizard
                                    st.session_state.wizard_step -= 1
                                    # Mantenemos el Wizard expandido
                                    st.session_state.wizard_expanded = True
                                    # Forzamos a Streamlit a refrescar la pantalla por completo
                                    st.rerun()
                            
                            # Calculamos lógicamente si el usuario se encuentra en el último paso de la fila
                            is_last = (st.session_state.wizard_step == len(wizard_queue) - 1)
                            # Si es el último, el botón dice Confirmar, sino, Siguiente
                            btn_label = "Confirmar ✅" if is_last else "Siguiente ➡️"
                            
                            # Si se presiona el botón de Siguiente/Confirmar
                            if c_next.button(btn_label):
                                # Guardamos formalmente la decisión tomada (el resultado duty) en el estado general asociándolo a ese código 8 dígitos
                                st.session_state.user_232_decisions[current_hts] = duty_result
                                # Si aún no es el último paso
                                if not is_last:
                                    # Avanzamos el índice general del Wizard en +1
                                    st.session_state.wizard_step += 1
                                    # Mantenemos Wizard visible
                                    st.session_state.wizard_expanded = True
                                    # Refrescamos pantalla
                                    st.rerun()
                                else:
                                    # Si fue el último paso, cerramos el expander automático del Wizard ocultándolo
                                    st.session_state.wizard_expanded = False
                                    # Refrescamos pantalla para que avance a cargar la tabla con todos los datos calculados
                                    st.rerun()
                            # Mostramos en texto pequeño en qué paso se encuentra el usuario ej. 1 / 3
                            st.caption(f"{st.session_state.wizard_step + 1} / {len(wizard_queue)}")

                # --- PREPARACIÓN DE LA TABLA ESTADOS UNIDOS ---
                # Limpiamos las tasas arancelarias generales
                hts_filtrado['General Duty'] = hts_filtrado['General'].apply(clean_percentage)
                # Evaluamos si existe una columna de Recíprocos
                if 'Reciprocal' in hts_filtrado.columns:
                    # Limpiamos la tasa arancelaria recíproca
                    hts_filtrado['Reciprocal Duty'] = hts_filtrado['Reciprocal'].apply(clean_percentage)
                else: 
                    # Si no existe, seteamos a 0.0 de forma segura
                    hts_filtrado['Reciprocal Duty'] = 0.0
                # Evaluamos si existe una columna de Fentanilo
                if 'Fentanyl' in hts_filtrado.columns:
                    # Limpiamos tasa arancelaria relacionada a políticas de fentanilo
                    hts_filtrado['Fentanyl Duty'] = hts_filtrado['Fentanyl'].apply(clean_percentage)
                else: 
                    # Si no, a 0.0
                    hts_filtrado['Fentanyl Duty'] = 0.0

                # Hacemos cruce a la tabla 301 para adjuntar esa capa de impuestos. Se hace por el campo 'Code' a la izquierda
                hts_filtrado = hts_filtrado.merge(sec301[['Code', 'Duty']], left_on='Code', right_on='Code', how='left')
                # Renombramos la columna cruda traída a un nombre claro para la tabla final
                hts_filtrado.rename(columns={'Duty': '301 Duty'}, inplace=True)
                # Si algún código no tuvo cruce, su arancel se llenó con NaN. Los reemplazamos con 0.0 explícitamente
                hts_filtrado['301 Duty'] = hts_filtrado['301 Duty'].fillna(0.0)
                # Creamos columna bandera indicando (True o False) si este código existe en el listado de TMEC cargado previamente
                hts_filtrado['is_tmec'] = hts_filtrado['Code'].isin(tmec['Code'])

                # Aplicamos a todas las filas la función de cálculo del arancel 232 que movimos a la sección de Definiciones
                hts_filtrado['232 Duty'] = hts_filtrado.apply(calculate_232_row, axis=1)
                
                # Aplicamos a todas las filas la suma total de aranceles (General + 301 + Reciproco + Fentanilo + 232)
                hts_filtrado['Total Duty'] = hts_filtrado.apply(calc_total_row, axis=1)

                # Intentamos convertir todos los "Total Duty" a un formato verdaderamente numérico (Flotante), 
                # los que fallan (por ser cadenas string con símbolos de error) los fuerza a ser Nulos (coerce)
                numeric_totals = pd.to_numeric(hts_filtrado['Total Duty'], errors='coerce')
                # Calculamos matemáticamente el promedio general de todos los valores válidos
                avg_total_duty = numeric_totals.mean()

                # Preparamos las columnas para organizar la interfaz de la tabla y métricas de EUA (1 vs 4)
                col_metrics_us, col_table_us = st.columns([1, 4])
                
                # En la columna pequeña, dibujamos métrica consolidada para USA
                with col_metrics_us:
                    st.metric("Arancel Promedio Total USA", f"{avg_total_duty:,.2f}% 🇨🇳")

                # En la columna grande (tabla detallada)
                with col_table_us:
                    # Instrucción aclarando para qué es el color verde
                    st.markdown("📄 *Los registros marcados en verde, representan fracciones incluidas en el TMEC.*")
                    # Seleccionamos y ordenamos el arreglo definitivo de columnas a presentar
                    cols_final = ['Code', 'Description', 'General Duty', '301 Duty', '232 Duty', 'Reciprocal Duty', 'Fentanyl Duty', 'Total Duty']
                    
                    # Definimos el diccionario de reglas de formateo para aplicar sufijos '%' e invocar formato inteligente
                    format_dict = {'General Duty': '{:.2f}%', '301 Duty': '{:.2f}%', '232 Duty': smart_pct, 'Reciprocal Duty': '{:.2f}%', 'Fentanyl Duty': '{:.2f}%', 'Total Duty': smart_pct}

                    # Renderizamos la tabla
                    st.dataframe(
                        # Primero, se filtra por las columnas finales a mostrar
                        hts_filtrado[cols_final].style
                        # Segundo, se aplica nuestro coloreado de filas TMEC definido en las Definiciones
                        .apply(highlight_tmec_row, axis=1)
                        # Tercero, se inyectan las reglas de formateo con formato '%' numérico
                        .format(format_dict)
                        # Cuarto, se asegura que la caja de descripciones rompa en varias líneas
                        .set_properties(subset=['Description'], **{'white-space': 'normal', 'word-wrap': 'break-word'}),
                        # Se oculta el índice base de Pandas y se adhiere a la pantalla completa
                        use_container_width=True, hide_index=True
                    )
                
                # --- ANÁLISIS HISTÓRICO ULTRA-RESILIENTE ---
                # Dibujamos encabezado de sub-sección para iniciar gráficas e histórico
                st.subheader(f"Resumen de Desempeño: México vs {target_country}")
                
                # FIX CRÍTICO: Rellenamos con ceros (zfill) por la izquierda hasta asegurar longitud de 6 caracteres 
                # Ej: transforma "010121" en "10121" si es numérico pero como cadena, y garantiza compatibilidad de tipos
                code_match = str(hs6_input).zfill(6)
                
                # Filtramos base Histórica de Participación: Garantiza padding a 6 y filtra donde cruce, luego ordena temporalmente
                df_part_sub = part[part['Subpartida'].astype(str).str.zfill(6) == code_match].sort_values('Date').copy()
                # Filtramos base Histórica de Aranceles bajo la misma lógica y ordenamos
                df_aranceles_sub = aranceles[aranceles['Subpartida'].astype(str).str.zfill(6) == code_match].sort_values('Date').copy()

                # Calculamos variables booleanas de seguridad, True si hay al menos un registro tras los filtros
                rows_part = len(df_part_sub) > 0
                rows_ara = len(df_aranceles_sub) > 0
                
                # Si alguna de las dos tablas tuvo un hit positivo y tiene datos
                if rows_part or rows_ara:
                    
                    # --- Preparación de Métricas de Resumen (Tabla 2x4) ---
                    # Inicializamos los placeholders en caso de que alguna seccción específica no traiga datos
                    money_last = share_last = money_avg = share_avg = "N/D"
                    tariff_last = tariff_avg = "N/D"
                    last_date_txt = "N/D"

                    # Evaluamos si tenemos información de Participación de Mercado
                    if rows_part:
                        # Para estas columnas clave
                        for col in ['Mexico', 'Total', 'China']:
                            # Si la columna existe dentro de nuestro DF de Participación
                            if col in df_part_sub.columns:
                                # Forzamos toda la columna a valores Numéricos por seguridad
                                df_part_sub[col] = pd.to_numeric(df_part_sub[col], errors='coerce')
                        
                        # Si existe la columna que contiene el "Total" mundial
                        if 'Total' in df_part_sub.columns:
                            # Calculamos Share de México: (MX / Total) * 100, asignamos NaN en divisiones por 0
                            df_part_sub['Market_Share_Mex'] = np.where(df_part_sub['Total'] > 0, (df_part_sub['Mexico'] / df_part_sub['Total'] * 100), np.nan)
                            # Calculamos Share de China: (CN / Total) * 100
                            df_part_sub['Market_Share_China'] = np.where(df_part_sub['Total'] > 0, (df_part_sub['China'] / df_part_sub['Total'] * 100), np.nan)
                        
                        # Extraemos temporalmente el último registro de la línea del tiempo como la "Fotografía Actual"
                        last_valid_part = df_part_sub.iloc[-1]
                        # Extraemos la cadena de texto humana de ese último mes "Ej: Febrero 2024"
                        last_date_txt = last_valid_part['Date'].strftime('%B %Y') if pd.notna(last_valid_part['Date']) else "N/D"
                        # Extraemos un corte de los últimos 12 meses exactos (o los que existan si son menos) de la tabla
                        df_12m_part = df_part_sub.iloc[-12:]

                        # Formateamos valores Moneda Últimos usando la definición que hemos extraído a la sección 3 (True = formato moneda $)
                        money_last = combine_vals(last_valid_part.get('Mexico'), last_valid_part.get('China'), True)
                        # Formateamos valores de Share Último (False = formato porcentaje %)
                        share_last = combine_vals(last_valid_part.get('Market_Share_Mex'), last_valid_part.get('Market_Share_China'), False)
                        # Formateamos valores de Promedios 12 Meses en Moneda
                        money_avg = combine_vals(df_12m_part['Mexico'].mean(), df_12m_part['China'].mean(), True)
                        # Formateamos promedios 12 meses en Share de mercado %
                        share_avg = combine_vals(df_12m_part['Market_Share_Mex'].mean(), df_12m_part['Market_Share_China'].mean(), False)

                    # Evaluamos si tenemos información en Aranceles Efectivos
                    if rows_ara:
                        # Repasamos columnas de países en el DataFrame arancelario
                        for col in ['Mexico', 'China']:
                            if col in df_aranceles_sub.columns:
                                # Forzamos el dato a numérico y multiplicamos por 100 para que represente un porcentaje clásico en las métricas
                                df_aranceles_sub[col] = pd.to_numeric(df_aranceles_sub[col], errors='coerce') * 100
                        
                        # Tomamos la fotografía actual (último registro)
                        last_valid_ara = df_aranceles_sub.iloc[-1]
                        # Tomamos bloque de últimos 12 registros
                        df_12m_ara = df_aranceles_sub.iloc[-12:]
                        
                        # Preparamos string comparativo último del Arancel (False = %)
                        tariff_last = combine_vals(last_valid_ara.get('Mexico'), last_valid_ara.get('China'), False)
                        # Preparamos el Promedio histórico
                        tariff_avg = combine_vals(df_12m_ara['Mexico'].mean(), df_12m_ara['China'].mean(), False)

                    # Ensamblamos los Diccionarios estáticos que formarán nuestra mini-tabla de Resumen
                    resumen_data = {
                        'Concepto': [f"Último Dato Disp. ({last_date_txt})", "Promedio 12 Meses"],
                        'Part. $': [money_last, money_avg],
                        'Share %': [share_last, share_avg],
                        'Arancel %': [tariff_last, tariff_avg]
                    }
                    # Mostramos tabla de resumen renderizada ocupando todo el ancho
                    st.dataframe(pd.DataFrame(resumen_data), use_container_width=True, hide_index=True)
                    
                    # --- Dibujado de Gráficas Evolutivas ---
                    # Desplegamos título inferior para la sección puramente visual
                    st.subheader(f"Análisis Histórico: México vs {target_country}")
                    # Creamos dos contenedores lado a lado equitativos
                    col_chart1, col_chart2 = st.columns(2)
                    
                    # Llenamos columna 1 (Izquierda)
                    with col_chart1:
                        # Título interno para la primera gráfica
                        st.markdown("**Participación de Mercado (%)**")
                        # Si tenemos datos de base histórica de Participación
                        if rows_part:
                            # Invocamos función limpia extraída para ensamblar las series de la gráfica usando Market_Share
                            chart_data, palette = prepare_chart_data(df_part_sub, 'Market_Share_Mex', 'Market_Share_China', "México", target_country)
                            # Validamos con dropna si al final de preparar los datos realmente quedó al menos un valor no nulo graficable
                            if not chart_data.dropna(how='all').empty:
                                # Si hay info, disparamos el dibujado (Función movida a bloque 3)
                                plot_altair_chart(chart_data, palette, '% Participación')
                            else:
                                # Si al final era todo NaN, mostramos texto azul
                                st.info("Datos no disponibles.")
                        else:
                            # Si nunca hubo datos para participación, se avisa
                            st.info("Sin datos de participación.")

                    # Llenamos columna 2 (Derecha)
                    with col_chart2:
                        # Título interno
                        st.markdown("**Arancel Efectivo (%)**")
                        # Si tenemos datos de base histórica de Aranceles
                        if rows_ara:
                            # Invocamos la función pero ahora mandando columnas crudas y nombres
                            chart_data, palette = prepare_chart_data(df_aranceles_sub, 'Mexico', 'China', "México", target_country)
                            # Limpieza para no tratar de dibujar el vacío
                            if not chart_data.dropna(how='all').empty:
                                # Disparamos dibujado con título eje Y adaptado
                                plot_altair_chart(chart_data, palette, '% Arancel')
                            else:
                                # Si era puro NaN
                                st.info("Datos no disponibles.")
                        else:
                            # Sin registros
                            st.info("Sin datos de aranceles.")
                
                else:
                    # En caso extremo que ni participación ni aranceles tengan nada de historial, avisamos globalmente
                    st.info(f"No hay registros históricos para la subpartida {hs6_input}.")

            else:
                # Si el filtro en Estados Unidos resultó completamente vacío
                st.warning(f"No se encontró información en HTS para {hs6_input}")

else:
    # Pantalla principal predeterminada antes de que el usuario busque nada
    st.info("👈 Ingresa una subpartida para comenzar.")