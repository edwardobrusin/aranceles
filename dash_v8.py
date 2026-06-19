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
    
    /* Reduce el espacio muerto en la parte superior de la página */
    .block-container {
        padding-top: 1.5rem !important; 
        padding-bottom: 0rem !important;
    }

    /* Opcional: Reduce el espacio entre el sidebar y el contenido principal */
    [data-testid="stSidebarNav"] {
        padding-top: 0rem !important;
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
    hr { margin-top: 5px; margin-bottom: 5px; border-top: 1px solid #E2E8F0; }
    h1, h2, h3 { color: #0F172A !important; font-weight: 800 !important; letter-spacing: -0.5px; }

    /* Estilo para los DataFrames de Streamlit */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }

    /* Estilo profesional para el Input y también los Selectbox (Listas desplegables) */
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #F8FAFC !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 8px !important;
        transition: border-color 0.3s ease !important;
    }
    [data-testid="stSidebar"] [data-baseweb="input"]:focus-within,
    [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
        border-color: #2596be !important;
    }
            
    /* Estilo de tablas Homogéneo V5 ULTRA COMPACTO */
    table.tabla-aranceles { 
        table-layout: fixed !important; 
        width: 100% !important; 
        min-width: 100% !important;
        border-collapse: collapse; 
        border: none !important;
        margin-bottom: 0px !important;
    }
    .tabla-aranceles th { 
        border-bottom: 2px solid #E2E8F0 !important; 
        padding: 6px 10px !important; 
        color: #64748B; 
        font-size: 0.75rem !important; 
        text-transform: uppercase; 
        font-weight: 700; 
        background-color: transparent; 
        text-align: center !important; 
    }
    .tabla-aranceles td { 
        border-bottom: 1px solid #E2E8F0 !important; 
        padding: 6px 10px !important; 
        color: #475569; 
        font-size: 0.85rem !important; 
        vertical-align: middle; 
        word-wrap: break-word;
    }
    /* El primer y segundo th/td siempre alineados a la izquierda */
    .tabla-aranceles th:nth-child(1), .tabla-aranceles td:nth-child(1),
    .tabla-aranceles th:nth-child(2), .tabla-aranceles td:nth-child(2) { 
        text-align: left !important; 
    }
    .tabla-aranceles tr:last-child td { border-bottom: none !important; }
</style>
""", unsafe_allow_html=True)

# Encabezado Principal Institucional
st.markdown("<h1 style='color: #2596be; font-size: 2.8rem;'>Monitor de Comercio y Aranceles</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 0.85rem; margin-top: -15px; margin-bottom: 5px; text-align: right;'>Última actualización: 19/06/2026</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #2596be; margin-top: -10px; margin-bottom: 15px; border-width: 2px;'>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SECCIÓN INFORMATIVA: MARCO ARANCELARIO GENERAL
# -----------------------------------------------------------------------------
with st.expander("📖 Marco Arancelario General", expanded=False):
    st.markdown("""<div style='padding: 10px;'>

<details style='margin-bottom: 10px;'>
<summary style='color: #008889; font-size: 1.5rem; font-weight: bold; cursor: pointer;'>🇲🇽 México</summary>
<div style='padding-left: 15px; padding-top: 10px;'>

<details style='margin-bottom: 5px;'>
<summary style='color: #73c6e3; font-size: 1.2rem; font-weight: bold; cursor: pointer;'><a href='https://www.snice.gob.mx/cs/avi/snice/ligie.info22.html' target='_blank' style='color: inherit; text-decoration: none;'>LIGIE (Ley de los Impuestos Generales de Importación y de Exportación)</a></summary>
<div style='padding-left: 15px;'>
<p style='color: #475569; font-size: 0.9rem;'>
La <a href='https://www.snice.gob.mx/cs/avi/snice/ligie.info22.html' target='_blank' style='color: #2596be; text-decoration: none;'>LIGIE</a> es el instrumento jurídico mediante el cual se define la política comercial de México, ya que permite identificar los impuestos a la exportación e importación de las mercancías y es la base para la generación de las estadísticas del comercio exterior necesarias para establecer y evaluar distintas políticas públicas, así como realizar análisis económicos más específicos.<br>
La base de datos de la <a href='https://www.snice.gob.mx/cs/avi/snice/ligie.info22.html' target='_blank' style='color: #2596be; text-decoration: none;'>LIGIE</a> es el insumo para aplicar el <i>Arancel</i> en esta sección.
</p>
</div>
</details>

</div>
</details>

<hr style='border-color: #E2E8F0;'>

<details style='margin-bottom: 10px;'>
<summary style='color: #008889; font-size: 1.5rem; font-weight: bold; cursor: pointer;'>🇺🇸 Estados Unidos</summary>
<div style='padding-left: 15px; padding-top: 10px;'>

<details style='margin-bottom: 5px;'>
<summary style='color: #73c6e3; font-size: 1.2rem; font-weight: bold; cursor: pointer;'><a href='https://hts.usitc.gov/' target='_blank' style='color: inherit; text-decoration: none;'>HTS (Harmonized Tariff Schedule)</a></summary>
<div style='padding-left: 15px;'>
<p style='color: #475569; font-size: 0.9rem;'>
El <a href='https://hts.usitc.gov/' target='_blank' style='color: #2596be; text-decoration: none;'>HTS</a> de los Estados Unidos establece las tasas arancelarias y las categorías estadísticas para todas las mercancías importadas a los Estados Unidos. El <a href='https://hts.usitc.gov/' target='_blank' style='color: #2596be; text-decoration: none;'>HTS</a> se basa en el <a href='https://www.wcoomd.org/en/topics/nomenclature/overview/what-is-the-harmonized-system.aspx' target='_blank' style='color: #2596be; text-decoration: none;'>Sistema Armonizado</a> internacional, que es el sistema global de nomenclatura aplicado a la mayoría del comercio mundial de mercancías.<br>
La base de datos del <a href='https://hts.usitc.gov/' target='_blank' style='color: #2596be; text-decoration: none;'>HTS</a> es el insumo para aplicar el arancel <i>General</i> en esta sección.
</p>
</div>
</details>

<details style='margin-bottom: 5px;'>
<summary style='color: #73c6e3; font-size: 1.2rem; font-weight: bold; cursor: pointer;'><a href='https://www.whitehouse.gov/presidential-actions/2026/02/imposing-a-temporary-import-surcharge-to-address-fundamental-international-payments-problems/' target='_blank' style='color: inherit; text-decoration: none;'>Sección 122</a></summary>
<div style='padding-left: 15px;'>
<ul style='color: #475569; font-size: 0.9rem;'>
<li><b>Arancel Temporal a la Importación (Temporary Import Surcharge)</b></li>
<li><b>Arancel:</b> 10% ad valorem</li>
<li><b>Reparaciones en el Extranjero:</b> 10% sobre el valor de la reparación.</li>
<li><b>Ensamblado en el Extranjero:</b> 10% sobre el valor total menos el valor de los componentes de EUA.</li>
<li><b>Productos clasificados en la Sección 232 de Metales:</b> 10% sobre el contenido que no es acero, aluminio o cobre.</li>
<li><b>Exenciones:</b>
<ul>
<li>Productos originarios de México o Canadá que cumplan con los requisitos de ingreso por TMEC.</li>
<li><b>Anexo II (Fracciones Exentas):</b>
<ul>
<li><b>Ex:</b> La fracción tiene arancel, excepto el producto especificado.</li>
<li><b>Aeronaves (Aircraft):</b> Si son partes, componentes o ensamblajes de aeronaves civiles.</li>
</ul>
</li>
<li><b>Sectoriales 232:</b> Automóviles y sus partes, vehículos pesados y sus partes, autobuses y sus partes, madera y semiconductores.</li>
</ul>
</li>
<li><b>Fecha de inicio:</b> 24/02/2026.</li>
<li><b>Fecha de término:</b> 24/07/2026.</li>
</ul>
</div>
</details>

<details style='margin-bottom: 5px;'>
<summary style='color: #73c6e3; font-size: 1.2rem; font-weight: bold; cursor: pointer;'>Sección 232 (5 sectores)</summary>
<div style='padding-left: 15px; padding-top: 5px;'>             

<div style='padding-bottom: 10px; color: #475569; font-size: 0.9rem;'>
<b>Jerarquía de Aplicación:</b> Si una fracción arancelaria específica aparece listada en más de un anexo de la Sección 232, <b>solo se cobra una tasa arancelaria (es decir, no se acumulan entre sí)</b>, aplicando el principio de especificidad o la tasa que la proclama presidencial defina como prioritaria.  El orden de prelación para el cobro de la tasa arancelaria sigue una jerarquía específica, la cual se estructura de la siguiente manera:
<ol style="margin-top: 5px; margin-bottom: 5px;">
<li>Semiconductores y derivados</li>
<li>Automóviles y sus partes, MHDV’s y sus partes, Autobuses y sus partes, y Otros</li>
<li>Aluminio, Acero y Cobre</li>
<li>Madera, Troncos y Derivados</li>
</ol>
</div>

<details style='margin-bottom: 5px;'>
<summary style='color: #2596be; font-weight: bold; cursor: pointer;'><a href='https://www.whitehouse.gov/presidential-actions/2026/06/further-adjusting-the-tariff-regimes-for-imports-of-aluminum-steel-and-copper-into-the-united-states/' target='_blank' style='color: inherit; text-decoration: none;'>1. Aluminio, Acero y Cobre (Aluminum, Steel and Copper)</a></summary>
<div style='padding: 10px; color: #475569; font-size: 0.9rem;'>
<b>Vigencia:</b>
<li>El 1 de junio de 2026, se emitió la proclamación <i><a href='https://www.whitehouse.gov/presidential-actions/2026/06/further-adjusting-the-tariff-regimes-for-imports-of-aluminum-steel-and-copper-into-the-united-states/' target='_blank' style='color: #2596be; text-decoration: none;'>Further Adjusting the Tariff Regimes for Imports of Aluminum, Steel and Copper into the United States</a></i>. Esta medida entró en vigor el 8 de junio de 2026 y se mantendrá vigente hasta el 31 de diciembre de 2027.</li>
<li>A partir del 1 de enero de 2028, los esquemas preferenciales temporales y las subpartidas especiales (9903.82.20 a la 9903.82.26) serán eliminados del HTSUS, regresando al mecanismo establecido en la proclamación de abril (<a href='https://www.whitehouse.gov/presidential-actions/2026/04/strengthening-actions-taken-to-adjust-imports-of-aluminum-steel-and-copper-into-the-united-states/' target='_blank' style='color: #2596be; text-decoration: none;'>Strengthening Actions Taken to Adjust Imports of Aluminum, Steel and Copper into the United States</a>) de 2026.</li>
<b>Principales modificaciones respecto a la proclamación de abril:</b> El umbral legal para considerar que un producto está compuesto "enteramente" de metal estadounidense se reduce del 95% al 85%. Se crea un nuevo Anexo, el “<a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-I-C.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>Annex I-C</a>” compuesto enteramente por artículos contenidos previamente en el “<a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-I-B.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>Annex I-B</a>” con un arancel general temporal del 25% y diversas reglas específicas. Se reubicaron 176 productos específicos (10 dígitos).<br><br>
<b>Estructura de Tasas Generales por Anexo</b><br>
<b><a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-I-A.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>Anexo I-A (Materias Primas y Derivados Principales)</a>:</b> Tasa general del 50% (10% si cumple con el umbral de fundición y moldeado de EUA).<br><br>
<b><a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-I-B.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>Anexo I-B (Derivados Secundarios e Insumos)</a>:</b> Tasa general del 25% (10% si cumple con el umbral de fundición y moldeado de EUA).<br>
<ul style="margin-top: 5px; margin-bottom: 15px;">
<li>Si cualquier parte clasificable en los capítulos 84, 85 u 87 dentro de este anexo, entra para uso final en la manufactura de equipo industrial móvil (mobile industrial equipment) listados en el Anexo I-C, y equipo agrícola o industrial fijo (agricultural / fixed industrial equipment) listados en el Anexo III, pero no cumple con el umbral de fundición y moldeado de EUA, el arancel aplicable se calcula usando la fórmula: <i>max{0, (15% - Column 1 Rate)}</i></li>
<li>Para los artículos listados fuera de los Capítulos 72, 73, 74 y 76 del HTSUS, el arancel de la Sección 232 solo aplica si el peso del metal regulado representa al menos el 15% del peso total del artículo importado. Si el producto contiene diversos metales regulados (ej. aluminio y cobre), se debe sumar el peso agregado de dichos metales para calcular si se alcanza el umbral del 15%.</li>
<li>Cualquier parte clasificable en los capítulos 84, 85 u 87 del HTSUS e incluida en el Anexo I-B, quedará totalmente exenta del pago de la Sec. 232 si se importa exclusivamente para la manufactura de motocicletas.</li>
</ul>
<b><a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-I-C.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>Anexo I-C (Maquinaria y Equipo Móvil)</a>:</b> Tasa general temporal del 25%.<br>
<ul style="margin-top: 5px; margin-bottom: 15px;">
<li>Para aluminio fundido y moldeado en EUA o acero derretido y vertido en EUA: <i>max{0, (10% - Column 1 Rate)}</i></li>
<li>Para los artículos listados fuera de los Capítulos 72, 73, 74 y 76 del HTSUS, el arancel de la Sección 232 solo aplica si el peso del metal regulado representa al menos el 15% del peso total del artículo importado. Si el producto contiene diversos metales regulados (ej. aluminio y cobre), se debe sumar el peso agregado de dichos metales para calcular si se alcanza el umbral del 15%.</li>
<li>Si un producto encuadra en múltiples supuestos arancelarios, la autoridad aduanera está obligada a aplicar la tasa arancelaria más baja disponible.</li>
<li>Para los bienes originarios de México y Canadá que califiquen para trato preferencial bajo el T-MEC, el arancel del 25% de la Sección 232 se aplicará de manera seccionada sobre el valor del producto:
<ul style="list-style-type: circle; margin-top: 5px;">
<li>El 25% de arancel adicional aplica sobre el valor total del contenido no estadounidense.</li>
<li>Sobre el contenido estadounidense, la porción que represente hasta el 40% del valor total del producto queda exenta del arancel. Si el contenido estadounidense supera el 40% del valor total, la porción excedente sí paga el 25% de arancel.</li>
<li>Sin importar el resultado matemático del desglose de contenido anterior, el arancel efectivo total cobrado sobre el producto importado nunca podrá ser inferior al 15% ad valorem.</li>
</ul>
</li>
</ul>
<b><a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-II.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>Anexo II (Artículos Exentos)</a>:</b> Tasa general del 0% (excluidos completamente del alcance de la Sección 232).<br><br>
<b><a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-III.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>Anexo III (Reducciones Temporales)</a>:</b> Sujetos a esquemas de reducción arancelaria o techos combinados.<br>
<li>Si no cumple con el umbral de fundición y moldeado de EUA: <i>max{0, (15% - Column 1 Rate)}</i></li>
<li>Si cumple con el umbral de fundición y moldeado de EUA: <i>max{0, (10% - Column 1 Rate)}</i></li>
<li>Para los artículos listados fuera de los Capítulos 72, 73, 74 y 76 del HTSUS, el arancel de la Sección 232 solo aplica si el peso del metal regulado representa al menos el 15% del peso total del artículo importado. Si el producto contiene diversos metales regulados (ej. aluminio y cobre), se debe sumar el peso agregado de dichos metales para calcular si se alcanza el umbral del 15%.</li>
</div>
</details>

<details style='margin-bottom: 5px;'>
<summary style='color: #2596be; font-weight: bold; cursor: pointer;'><a href='https://www.whitehouse.gov/presidential-actions/2025/03/adjusting-imports-of-automobiles-and-autombile-parts-into-the-united-states/' target='_blank' style='color: inherit; text-decoration: none;'>2. Automóviles y Autopartes (Automobile and Automobile Parts)</a></summary>
<div style='padding: 10px; color: #475569; font-size: 0.9rem;'>
<ul style="margin-top: 5px; margin-bottom: 0px;">
<li><b>Vigencia:</b>
<ul style="list-style-type: circle; margin-top: 5px;">
<li><b>Fecha de Proclamación:</b> 26/03/2025.</li>
<li><b>Fecha de Entrada en Vigor:</b>
<ul style="list-style-type: square; margin-top: 5px;">
<li><b>Automóviles de pasajeros:</b> 03/04/2025.</li>
<li><b>Autopartes y componentes vehiculares:</b> 03/05/2025.</li>
</ul>
</li>
</ul>
</li>
<li><b>Arancel:</b> 25% ad valorem.</li>
<li>Posibilidad de presentar documentación sobre el porcentaje de contenido estadounidense en el vehículo, una vez aprobado, el 25% aplica sobre el valor del vehículo que no sea de EUA.</li>
<li>Si la <a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-I-C.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>CBP (US Customs and Border Protection)</a> determina que el porcentaje declarado es impreciso, la sanción será aplicar el 25% sobre el valor total del vehículo. Aplica a todos los vehículos del mismo modelo e importador hasta que se corrija.</li>
<li>No aplica arancel preferente por ensamblaje o reparación en el extranjero, se cobra el 25% sobre el valor total.</li>
<li><b>Exenciones:</b>
<ul style="list-style-type: circle; margin-top: 5px;">
<li><b>Autopartes T-MEC:</b> Excepto kits de desmontaje de automóviles o compilaciones de partes (knock-down kits or parts compilations).</li>
<li><b>Vehículos Antiguos:</b> 25 años o más desde su fabricación.</li>
<li><b>Clasificación:</b> Si no consiste en un vehículo de pasajeros (sedanes, vehículos utilitarios deportivos [SUV], vehículos utilitarios crossover, minivans y furgonetas de carga), camión ligero o sus partes.</li>
</ul>
</li>
</ul>
</div>
</details>

<details style='margin-bottom: 5px;'>
<summary style='color: #2596be; font-weight: bold; cursor: pointer;'><a href='https://www.whitehouse.gov/presidential-actions/2025/10/adjusting-imports-of-medium-and-heavy-duty-vehicles-medium-and-heavy-duty-vehicle-parts-and-buses-into-the-united-states/' target='_blank' style='color: inherit; text-decoration: none;'>3. Vehículos de Carga Mediana y Pesada, Autobuses y Otros Vehículos (MHDV’s, Buses and Other Vehicles)</a></summary>
<div style='padding: 10px; color: #475569; font-size: 0.9rem;'>
<ul style="margin-top: 5px; margin-bottom: 0px;">
<li><b>Vigencia:</b>
<ul style="list-style-type: circle; margin-top: 5px;">
<li><b>Fecha Proclamación:</b> 17/10/2025.</li>
<li><b>Fecha de Entrada en Vigor:</b> 01/11/2025.</li>
</ul>
</li>
<li><b>Arancel:</b> 25% para "Vehículos de carga mediana y pesada" (Medium and heavy duty vehicles) y sus partes.</li>
<li><b>Arancel:</b> 10% para "Autobuses y otros vehículos" (Buses and other vehicles).</li>
<li>Posibilidad de presentar documentación sobre el porcentaje de contenido estadounidense en el vehículo, una vez aprobado, el 25% aplica sobre el valor del vehículo que no sea de EUA.</li>
<li>Se aplica un arancel de 25% a partes certificadas, aún si están fuera de las listas de fracciones reguladas, siempre que vayan a ser usadas en la producción de MHDV’s. Quedan exentos los capítulos 72, 73 y 76.</li>
<li>No aplica arancel preferente por ensamblaje o reparación en el extranjero, se cobra el 25% sobre el valor total.</li>
<li><b>Exenciones:</b>
<ul style="list-style-type: circle; margin-top: 5px;">
<li><b>Partes T-MEC:</b> Excepto kits de desmontaje de vehículos de carga mediana y pesada o compilaciones de partes.</li>
<li><b>Vehículos antiguos:</b> 25 años o más desde su fabricación.</li>
<li><b>Clasificación:</b> Si no se identifica como MHDV’s o sus partes, Autobuses u Otros Vehículos.</li>
</ul>
</li>
</ul>
</div>
</details>

<details style='margin-bottom: 5px;'>
<summary style='color: #2596be; font-weight: bold; cursor: pointer;'><a href='https://www.whitehouse.gov/presidential-actions/2025/09/adjusting-imports-of-timber-lumber-and-their-derivative-products-into-the-united-states/' target='_blank' style='color: inherit; text-decoration: none;'>4. Madera, Troncos y Derivados (Timber, Lumber and Derivatives)</a></summary>
<div style='padding: 10px; color: #475569; font-size: 0.9rem;'>
<ul style="margin-top: 5px; margin-bottom: 0px;">
<li><b>Vigencia:</b>
<ul style="list-style-type: circle; margin-top: 5px;">
<li><b>Fecha Proclamación:</b> 29/09/2025.</li>
<li><b>Fecha de Entrada en Vigor:</b> 14/10/2025.</li>
</ul>
</li>
<li><b>Arancel:</b> 10% para "Madera y troncos de coníferas / madera blanda" (Softwood timber and lumber).</li>
<li><b>Arancel:</b> 25% para "Productos de madera tapizados" (Upholstered wooden products) y "Gabinetes de cocina y tocadores" (Kitchen cabinets and Vanities).</li>
<li><b>Clasificación:</b> Si no se identifica con "Gabinetes de cocina y tocadores" o sus partes dentro de esa misma clasificación, queda libre de arancel.</li>
<li><b>Arancel Madera y Automóviles:</b> Ante el traslape, solo se aplica el régimen de Automóviles.</li>
</ul>
</div>
</details>

<details style='margin-bottom: 5px;'>
<summary style='color: #2596be; font-weight: bold; cursor: pointer;'><a href='https://www.whitehouse.gov/presidential-actions/2026/01/adjusting-imports-of-semiconductors-semiconductor-manufacturing-equipment-and-their-derivative-products-into-the-united-states/' target='_blank' style='color: inherit; text-decoration: none;'>5. Semiconductores y Derivados (Semiconductors and Derivatives)</a></summary>
<div style='padding: 10px; color: #475569; font-size: 0.9rem;'>
<ul style="margin-top: 5px; margin-bottom: 0px;">
<li><b>Vigencia:</b>
<ul style="list-style-type: circle; margin-top: 5px;">
<li><b>Fecha Proclamación:</b> 14/01/2026.</li>
<li><b>Fecha de Entrada en Vigor:</b> 15/01/2026.</li>
</ul>
</li>
<li><b>Arancel:</b> 25% ad valorem.</li>
<li>La aplicación del arancel dependerá de las especificaciones tecnológicas del producto.</li>
<li>Se exentarán los semiconductores y derivados orientados al desarrollo e infraestructura de EUA.</li>
<li>Se sobrepone por completo al T-MEC.</li>
</ul>
</div>
</details>

</div>
</details>

<details style='margin-bottom: 5px;'>
<summary style='color: #73c6e3; font-size: 1.2rem; font-weight: bold; cursor: pointer;'><a href='https://hts.usitc.gov/reststop/file?release=currentRelease&filename=China%20Tariffs' target='_blank' style='color: inherit; text-decoration: none;'>Sección 301 (Prácticas desleales y labor forzada)</a></summary>
<div style='padding-left: 15px;'>
<ul style='color: #475569; font-size: 0.9rem;'>
<li><b>Lista Extensa de Aranceles:</b> El Representante Comercial de EUA (USTR) conserva la facultad de otorgar exclusiones para productos específicos.</li>
<li><b>Países Afectados:</b> En base a la naturaleza de este tablero, solo China se muestra afectado actualmente (existen investigaciones en curso y amenazas a México en este rubro, pero no han sido aplicadas).</li>
<li><b>Vigencia Continua en Fases:</b> La partida 9903.88.16 está suspendida desde diciembre de 2019. Las grúas de barco a costa y otros equipos de manipulación de carga (9903.91.12 y 9903.91.14) se encuentran suspendidos hasta el 10 de noviembre de 2026.</li>
<li><b>Enfoque Primario:</b> Herramienta legal de EUA utilizada para responder activamente a políticas o prácticas de gobiernos extranjeros que se consideran desleales, irrazonables o que restringen el comercio estadounidense.</li>
</ul>
</div>
</details>

<details style='margin-bottom: 5px;'>
<summary style='color: #73c6e3; font-size: 1.2rem; font-weight: bold; cursor: pointer;'><a href='https://dataweb.usitc.gov/tariff/database' target='_blank' style='color: inherit; text-decoration: none;'>T-MEC (USMCA)</a></summary>
<div style='padding-left: 15px;'>
<p style='color: #475569; font-size: 0.9rem;'>
El Tratado entre los Estados Unidos de América, los Estados Unidos Mexicanos y Canadá (<a href='https://dof.gob.mx/2020/SRE/T_MEC_290620.pdf' target='_blank' style='color: #2596be; text-decoration: none;'>T-MEC</a>) es un acuerdo de libre comercio trilateral entre Estados Unidos, México y Canadá, en vigor desde el 1 de julio de 2020.<br>
La base de datos que proporciona el <a href='https://dataweb.usitc.gov' target='_blank' style='color: #2596be; text-decoration: none;'>USITC (US International Trade Commission)</a>, se utiliza como insumo para mapear los códigos arancelarios clasificados dentro del <a href='https://dataweb.usitc.gov/tariff/database' target='_blank' style='color: #2596be; text-decoration: none;'>TMEC</a>.
</p>
</div>
</details>

</div>
</details>

</div>""", unsafe_allow_html=True)

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
    if 'annex i-c' in val_str: return "Annex I-C"
    if 'annex iii' in val_str: return "Annex III"
    if val_str in ['ex.', 'ex', 'libre', 'free', 'n/a', '-', '']: return 0.0
    try:
        clean = ''.join(c for c in val_str if c.isdigit() or c == '.')
        return float(clean) if clean else 0.0
    except: return 0.0

def parse_hts_duties(val):
    """
    Nuevo Parser dinámico para extraer 'Math Base', 'General' y 'Fixed'.
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

@st.cache_data(show_spinner="Cargando bases de datos... Por favor espere.")
def load_data(target_country="China"):
    base_path = 'data/parquet_v4/'
    
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

    # METALS (Acero, Aluminio, Cobre)
    metals_db = pd.read_parquet(f'{base_path}metals.parquet')
    metals_db = normalize_cols(metals_db)
    metals_db.rename(columns=map_aux, inplace=True)
    metals_db = clean_numeric_code(metals_db, 'Code')
    if 'Duty' in metals_db.columns:
        metals_db['Duty'] = metals_db['Duty'].apply(clean_percentage)

    # TMEC
    tmec = pd.read_parquet(f'{base_path}tmec.parquet')
    tmec = normalize_cols(tmec)
    tmec.rename(columns=map_aux, inplace=True)
    tmec = clean_numeric_code(tmec, 'Code')
    
    # RVC
    try:
        rvc_db = pd.read_parquet(f'{base_path}rvc.parquet')
        rvc_db = normalize_cols(rvc_db)
        rvc_db.rename(columns=map_aux, inplace=True)
        rvc_db = clean_numeric_code(rvc_db, 'Code')
    except:
        rvc_db = pd.DataFrame(columns=['Code'])

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

    # SEC 122
    sec122 = pd.read_parquet(f'{base_path}sec_122.parquet')
    sec122 = normalize_cols(sec122)
    if 'code' in sec122.columns:
        sec122 = clean_numeric_code(sec122, 'code')

    # NUEVAS EXCEPCIONES SEC 122 (Auto, MHDV, Wood, Semi)
    auto_db = normalize_cols(pd.read_parquet(f'{base_path}auto.parquet'))
    if 'code' in auto_db.columns: 
        auto_db = clean_numeric_code(auto_db, 'code')
        auto_db.rename(columns={'code': 'Code', 'duty': 'Duty', 'category': 'Category'}, inplace=True)
        if 'Duty' in auto_db.columns:
            auto_db['Duty'] = auto_db['Duty'].apply(clean_percentage)

    mhdv_db = normalize_cols(pd.read_parquet(f'{base_path}mhdv.parquet'))
    if 'code' in mhdv_db.columns:
        mhdv_db = clean_numeric_code(mhdv_db, 'code')
        mhdv_db.rename(columns={'code': 'Code', 'duty': 'Duty', 'category': 'Category'}, inplace=True)
        if 'Duty' in mhdv_db.columns:
            mhdv_db['Duty'] = mhdv_db['Duty'].apply(clean_percentage)

    wood_db = normalize_cols(pd.read_parquet(f'{base_path}wood.parquet'))
    if 'code' in wood_db.columns:
        wood_db = clean_numeric_code(wood_db, 'code')
        wood_db.rename(columns={'code': 'Code', 'duty': 'Duty', 'category': 'Category'}, inplace=True)
        if 'Duty' in wood_db.columns:
            wood_db['Duty'] = wood_db['Duty'].apply(clean_percentage)

    semi_db = normalize_cols(pd.read_parquet(f'{base_path}semi.parquet'))
    if 'code' in semi_db.columns: semi_db = clean_numeric_code(semi_db, 'code')
    semi_db.rename(columns={'code': 'Code', 'duty': 'Duty'}, inplace=True)
    if 'Duty' in semi_db.columns:
        semi_db['Duty'] = semi_db['Duty'].apply(clean_percentage)

    return ligie, hts, sec301, metals_db, tmec, rvc_db, part, aranceles, auxiliar, sec122, auto_db, mhdv_db, wood_db, semi_db

# -----------------------------------------------------------------------------
# 3. LÓGICA DE CÁLCULO
# -----------------------------------------------------------------------------

def get_10digit_children(hts_8_digit, metals_db, auxiliar_db):
    hts_8 = str(hts_8_digit).strip()
    children_metals = metals_db[
        (metals_db['Code'].str.len() == 10) & 
        (metals_db['Code'].str.startswith(hts_8))
    ].copy()
    
    if children_metals.empty: 
        return pd.DataFrame()
        
    all_children = auxiliar_db[
        (auxiliar_db['Code'].str.len() == 10) & 
        (auxiliar_db['Code'].str.startswith(hts_8))
    ].copy()
    
    if all_children.empty:
        children_metals['Description'] = children_metals['Code'] + " - Opción específica"
        return children_metals[['Code', 'Duty', 'Description']]
        
    metals_unique = children_metals[['Code', 'Duty']].drop_duplicates('Code')
    merged = all_children.merge(metals_unique, on='Code', how='left')
    
    # Normalizamos el valor nulo a 0.0 (flotante) en lugar de "0" (texto). 
    # Esto asegura que el sistema identifique que todas las opciones convergen al mismo arancel (0.0).
    merged['Duty'] = merged['Duty'].fillna(0.0)
    
    merged['Description'] = merged['Code'] + " - " + merged['Description'].fillna("Descripción no disponible")
    
    return merged

def get_direct_matches(hts_8, metals_db):
    # Buscamos en todos los niveles jerárquicos posibles de forma descendente (desde 10)
    hts_str = str(hts_8).strip()
    for length in [10, 8, 7, 6, 5, 4]:
        sub = hts_str[:length]
        matches = metals_db[metals_db['Code'] == sub]
        if not matches.empty:
            return sub, matches.iloc[0].get('Duty', 0.0)
    return None, 0.0

def get_auto_match(hts_8, auto_db):
    # Búsqueda jerárquica para Autos, soporta desde Partida (4) hasta fracción completa (10)
    hts_str = str(hts_8).strip()
    for length in [10, 8, 7, 6, 5, 4]:
        sub = hts_str[:length]
        matches = auto_db[auto_db['Code'] == sub]
        if not matches.empty:
            duty = matches.iloc[0].get('Duty', 0.0)
            category = matches.iloc[0].get('Category', '')
            return sub, duty, category
    return None, 0.0, None

def get_mhdv_match(hts_8, mhdv_db):
    hts_str = str(hts_8).strip()
    for length in [10, 8, 7, 6, 5, 4]:
        sub = hts_str[:length]
        matches = mhdv_db[mhdv_db['Code'] == sub]
        if not matches.empty:
            duty = matches.iloc[0].get('Duty', 0.0)
            category = matches.iloc[0].get('Category', '')
            return sub, duty, category
    return None, 0.0, None

def get_wood_match(hts_8, wood_db):
    hts_str = str(hts_8).strip()
    for length in [10, 8, 7, 6, 5, 4]:
        sub = hts_str[:length]
        matches = wood_db[wood_db['Code'] == sub]
        if not matches.empty:
            duty = matches.iloc[0].get('Duty', 0.0)
            category = matches.iloc[0].get('Category', '')
            return sub, duty, category
    return None, 0.0, None

def get_semi_match(hts_code, semi_db):
    """Búsqueda jerárquica en semi.parquet (códigos a 6 dígitos).
    Cubre: match exacto, búsqueda hacia arriba (HTS → prefijo 6d) y
    búsqueda hacia abajo (código semi es prefijo del HTS)."""
    hts_str = str(hts_code).strip()
    # Exacto y hacia arriba (10 → 4 dígitos del HTS)
    for length in [10, 8, 7, 6, 5, 4]:
        sub = hts_str[:length]
        matches = semi_db[semi_db['Code'] == sub]
        if not matches.empty:
            return sub, float(matches.iloc[0].get('Duty', 0.0))
    # Hacia abajo: el código semi es más largo que el prefijo HTS ingresado
    for _, row in semi_db.iterrows():
        s_code = str(row['Code']).strip()
        if s_code.startswith(hts_str):
            return s_code, float(row.get('Duty', 0.0))
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

apply_mx = True
apply_us = True
target_country = "China"

# --- CARGA ---
try:
    ligie, hts, sec301, metals_db, tmec, rvc_db, part, aranceles, auxiliar, sec122, auto_db, mhdv_db, wood_db, semi_db = load_data(target_country)
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

# Consolidar bases de exención de la Sección 122 (0%) para búsqueda jerárquica
exc_list = []
for db in [auto_db, mhdv_db, wood_db, semi_db]:
    col_name = 'Code' if 'Code' in db.columns else 'code' if 'code' in db.columns else None
    if col_name:
        temp_df = db[[col_name]].copy()
        temp_df.rename(columns={col_name: 'Code'}, inplace=True)
        exc_list.append(temp_df)
if exc_list:
    exc_122_db = pd.concat(exc_list, ignore_index=True).drop_duplicates()
    exc_122_db['Duty'] = 0.0 # Columna auxiliar para que funcionen las funciones de metales
else:
    exc_122_db = pd.DataFrame(columns=['Code', 'Duty'])

# Variables de estado para sincronizar ambos buscadores
if 'current_hs6' not in st.session_state:
    st.session_state.current_hs6 = ""

# Generamos las pestañas, por default carga la primera ("Búsqueda Simple")
tab_simple, tab_avanzado = st.sidebar.tabs(["Búsqueda Simple", "Avanzada"])

with tab_simple:    
    # Preparamos los datos de LIGIE para los menús
    ligie_menu = ligie[['Código', 'Capítulo', 'Partida', 'Subpartida', 'Desdoblamiento']].copy()
    ligie_menu['Código'] = ligie_menu['Código'].astype(str).str.strip().str.zfill(8)
    ligie_menu['Cod_Cap'] = ligie_menu['Código'].str[:2]
    ligie_menu['Cod_Par'] = ligie_menu['Código'].str[:4]
    ligie_menu['Cod_Sub'] = ligie_menu['Código'].str[:6]

    # Vectorización ultra rápida para crear las etiquetas de búsqueda global
    ligie_menu['Opt_Cap'] = ligie_menu['Cod_Cap'] + " - " + ligie_menu['Capítulo'].fillna("").astype(str).str.strip()
    ligie_menu['Opt_Par'] = ligie_menu['Cod_Par'] + " - " + ligie_menu['Partida'].fillna("").astype(str).str.strip()
    
    ligie_menu['Opt_Sub'] = ligie_menu['Cod_Sub'] + " - " + ligie_menu['Subpartida'].fillna("").astype(str).str.strip()
    mask_desd = ligie_menu['Desdoblamiento'].notna() & (ligie_menu['Desdoblamiento'].astype(str).str.strip() != "") & (ligie_menu['Desdoblamiento'].astype(str).str.lower() != 'nan')
    ligie_menu.loc[mask_desd, 'Opt_Sub'] = ligie_menu.loc[mask_desd, 'Opt_Sub'] + " " + ligie_menu.loc[mask_desd, 'Desdoblamiento'].astype(str).str.strip()

    # Inicializamos el estado usando None para habilitar la 'X' de borrado nativo
    if 'scap' not in st.session_state: st.session_state.scap = None
    if 'spar' not in st.session_state: st.session_state.spar = None
    if 'ssub' not in st.session_state: st.session_state.ssub = None

    # Callbacks: Auto-completan hacia arriba o limpian hacia abajo según la selección
    def cb_cap():
        st.session_state.spar = None
        st.session_state.ssub = None
        
    def cb_par():
        if st.session_state.spar:
            cap_code = st.session_state.spar[:2]
            st.session_state.scap = ligie_menu[ligie_menu['Cod_Cap'] == cap_code]['Opt_Cap'].iloc[0]
        st.session_state.ssub = None
        
    def cb_sub():
        if st.session_state.ssub:
            cap_code = st.session_state.ssub[:2]
            par_code = st.session_state.ssub[:4]
            st.session_state.scap = ligie_menu[ligie_menu['Cod_Cap'] == cap_code]['Opt_Cap'].iloc[0]
            st.session_state.spar = ligie_menu[ligie_menu['Cod_Par'] == par_code]['Opt_Par'].iloc[0]
            
            # Disparar la consulta automáticamente al seleccionar (o dar Enter en el buscador)
            st.session_state.current_hs6 = st.session_state.ssub.split(" - ")[0]

    # 1. Lista de Capítulos (Quitamos el [""] manual porque usaremos index=None)
    all_caps = ligie_menu[['Cod_Cap', 'Opt_Cap']].drop_duplicates().sort_values('Cod_Cap')['Opt_Cap'].tolist()
    
    # 2. Lista de Partidas
    if st.session_state.scap:
        pars_df = ligie_menu[ligie_menu['Opt_Cap'] == st.session_state.scap]
    else:
        pars_df = ligie_menu
    all_pars = pars_df[['Cod_Par', 'Opt_Par']].drop_duplicates().sort_values('Cod_Par')['Opt_Par'].tolist()
    
    # 3. Lista de Subpartidas
    if st.session_state.spar:
        subs_df = ligie_menu[ligie_menu['Opt_Par'] == st.session_state.spar]
    elif st.session_state.scap:
        subs_df = ligie_menu[ligie_menu['Opt_Cap'] == st.session_state.scap]
    else:
        subs_df = ligie_menu
    all_subs = subs_df[['Cod_Sub', 'Opt_Sub']].drop_duplicates().sort_values('Cod_Sub')['Opt_Sub'].tolist()

    # Protecciones nativas
    if st.session_state.scap not in all_caps: st.session_state.scap = None
    if st.session_state.spar not in all_pars: st.session_state.spar = None
    if st.session_state.ssub not in all_subs: st.session_state.ssub = None

    # Interfaz con index=None para agregar la 'X' de borrado dentro de la caja
    st.selectbox("1. Capítulo:", all_caps, key='scap', on_change=cb_cap, index=None, placeholder="Seleccione o busque...")
    st.selectbox("2. Partida:", all_pars, key='spar', on_change=cb_par, index=None, placeholder="Seleccione o busque...")
    st.selectbox("3. Subpartida / Búsqueda libre:", all_subs, key='ssub', on_change=cb_sub, index=None, placeholder="Seleccione o busque...")
    
    # Lógica de botones Anterior/Siguiente para Búsqueda Simple
    if st.session_state.ssub:
        # Usamos la lista global para poder saltar entre diferentes partidas o capítulos
        global_subs = ligie_menu[['Cod_Sub', 'Opt_Sub']].drop_duplicates().sort_values('Cod_Sub')['Opt_Sub'].tolist()
        
        if st.session_state.ssub in global_subs:
            curr_idx = global_subs.index(st.session_state.ssub)
            
            def nav_simple_prev():
                st.session_state.ssub = global_subs[curr_idx - 1]
                cb_sub() # Actualiza Capítulo/Partida automáticamente y lanza búsqueda
                
            def nav_simple_next():
                st.session_state.ssub = global_subs[curr_idx + 1]
                cb_sub()
                
            c_prev, c_next = st.columns(2)
            with c_prev:
                if curr_idx > 0:
                    st.button("⬅️ Anterior", key="btn_simp_prev", on_click=nav_simple_prev, use_container_width=True)
            with c_next:
                if curr_idx < len(global_subs) - 1:
                    st.button("Siguiente ➡️", key="btn_simp_next", on_click=nav_simple_next, use_container_width=True)

    # Definimos el callback que se ejecutará ANTES de redibujar los widgets
    def clear_filters():
        st.session_state.scap = None
        st.session_state.spar = None
        st.session_state.ssub = None
        
        # Limpiar también la vista principal del dashboard
        st.session_state.current_hs6 = ""

    # Espaciado visual antes del botón
    st.markdown("<div style='margin-bottom: 0px;'></div>", unsafe_allow_html=True)

    # Botón pegado a las listas (sin espaciadores) y con color primario
    st.button("Limpiar Búsqueda", key="btn_clear", use_container_width=True, on_click=clear_filters, type="primary")

with tab_avanzado:
    st.markdown("<p style='font-size:0.85rem; color:#64748B; margin-top:-10px; margin-bottom: 10px;'>Ingreso directo de código a 6 dígitos.</p>", unsafe_allow_html=True)
    
    # Callback para que al dar Enter se dispare la búsqueda
    def trigger_adv_search():
        st.session_state.current_hs6 = st.session_state.adv_hs6_input
        
    st.text_input("Subpartida (6 Dígitos):", max_chars=6, placeholder="Ej: 722020", key="adv_hs6_input", on_change=trigger_adv_search)
    
    # Lógica de botones Anterior/Siguiente condicionada
    if st.session_state.current_hs6 and len(st.session_state.current_hs6) == 6:
        # Extraemos la lista ordenada de subpartidas a 6 dígitos
        all_subs = sorted(ligie['Código'].astype(str).str.strip().str.zfill(8).str[:6].unique().tolist())
        
        if st.session_state.current_hs6 in all_subs:
            curr_idx = all_subs.index(st.session_state.current_hs6)
            
            def nav_prev():
                st.session_state.current_hs6 = all_subs[curr_idx - 1]
                st.session_state.adv_hs6_input = all_subs[curr_idx - 1]
                
            def nav_next():
                st.session_state.current_hs6 = all_subs[curr_idx + 1]
                st.session_state.adv_hs6_input = all_subs[curr_idx + 1]
                
            col_prev, col_next = st.columns(2)
            with col_prev:
                if curr_idx > 0:
                    st.button("⬅️ Anterior", on_click=nav_prev, use_container_width=True)
            with col_next:
                if curr_idx < len(all_subs) - 1:
                    st.button("Siguiente ➡️", on_click=nav_next, use_container_width=True)

# Usamos HTML para forzar márgenes más pequeños en lugar de la línea "---" por defecto
st.sidebar.markdown("<hr style='margin-top: 0px; margin-bottom: 15px; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

# Variable unificada para el motor principal
hs6_input = st.session_state.current_hs6

# --- ESTADO WIZARD ---
if 'wizard_step' not in st.session_state: st.session_state.wizard_step = 0 
if 'user_metals_decisions' not in st.session_state: st.session_state.user_metals_decisions = {}
if 'user_tmec_metals_decisions' not in st.session_state: st.session_state.user_tmec_metals_decisions = {}
if 'user_sec122_decisions' not in st.session_state: st.session_state.user_sec122_decisions = {}
if 'user_auto_decisions' not in st.session_state: st.session_state.user_auto_decisions = {}
if 'user_tmec_auto_decisions' not in st.session_state: st.session_state.user_tmec_auto_decisions = {}
if 'user_mhdv_decisions' not in st.session_state: st.session_state.user_mhdv_decisions = {}
if 'user_tmec_mhdv_decisions' not in st.session_state: st.session_state.user_tmec_mhdv_decisions = {}
if 'user_wood_decisions' not in st.session_state: st.session_state.user_wood_decisions = {}
if 'user_semi_decisions' not in st.session_state: st.session_state.user_semi_decisions = {}
if 'last_search' not in st.session_state: st.session_state.last_search = ""
if 'wizard_expanded' not in st.session_state: st.session_state.wizard_expanded = True
if 'wizard_close_trigger' not in st.session_state: st.session_state.wizard_close_trigger = 0

if hs6_input != st.session_state.last_search:
    st.session_state.last_search = hs6_input
    st.session_state.wizard_step = 0
    st.session_state.user_metals_decisions = {}
    st.session_state.user_tmec_metals_decisions = {}
    st.session_state.user_sec122_decisions = {}
    st.session_state.user_auto_decisions = {}
    st.session_state.user_tmec_auto_decisions = {}
    st.session_state.user_mhdv_decisions = {}
    st.session_state.user_tmec_mhdv_decisions = {}
    st.session_state.user_wood_decisions = {}
    st.session_state.user_semi_decisions = {}
    st.session_state.wizard_expanded = True
    st.session_state.wizard_close_trigger = 0

# --- LÓGICA PRINCIPAL ---
if hs6_input:
    hs6_input = hs6_input.strip()
    
    if len(hs6_input) < 6:
        st.warning("Por favor ingresa 6 dígitos.")
    else:
        
        # =====================================================================
        # MÓDULO MÉXICO
        # =====================================================================
        if apply_mx:
            st.markdown("<h2 style='color: #0F172A;'><span class='bandera'>🇲🇽</span> Marco Arancelario de México</h2>", unsafe_allow_html=True)
            if 'Código' in ligie.columns:
                ligie_filtrado = ligie[ligie['Código'].str.startswith(hs6_input)].copy()
            else: ligie_filtrado = pd.DataFrame()

            if not ligie_filtrado.empty:
                try:
                    with st.expander("📂 Ley de Impuestos Generales de Importación y Exportación (LIGIE)", expanded=False):
                        row = ligie_filtrado.iloc[0]
                        show_hierarchy_item("Sección", row.get('Sección'))
                        show_hierarchy_item("Capítulo", row.get('Capítulo'))
                        show_hierarchy_item("Partida", row.get('Partida'))
                        show_hierarchy_item("Subpartida", row.get('Subpartida'))
                        show_hierarchy_item("Desdoblamiento", row.get('Desdoblamiento'))
                except: pass

                def format_ligie_arancel(val):
                    val_str = str(val).strip().lower()
                    if 'prohibida' in val_str:
                        return "Prohibida su Importación"
                    cleaned = clean_percentage(val)
                    return f"{cleaned:.2f}%"

                ligie_filtrado['Tasa General'] = ligie_filtrado['General'].apply(format_ligie_arancel)
                
                df_display_mx = ligie_filtrado[['Código', 'Fracción', 'Tasa General']].copy()
                df_display_mx.columns = ['Código', 'Descripción', 'Arancel']
                cols_to_center_mx = [c for c in df_display_mx.columns if c not in ['Código', 'Descripción']]

                html_mx = (
                    df_display_mx.style
                    .set_properties(subset=['Código'], **{'width': '15%'})
                    .set_properties(subset=['Descripción'], **{'width': '55%'})
                    .set_properties(subset=cols_to_center_mx, **{'text-align': 'center', 'width': '30%'})
                    .set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'center !important')]},
                        {'selector': 'th.col_heading.level0.col0', 'props': [('text-align', 'left !important')]},
                        {'selector': 'th.col_heading.level0.col1', 'props': [('text-align', 'left !important')]}
                    ])
                    .set_table_attributes('style="width: 100% !important; min-width: 100%;"')
                    .hide(axis='index')
                    .to_html(classes='tabla-aranceles', escape=False)
                )
                st.markdown(f"<div class='card-hover' style='padding: 10px 20px 0px 20px; margin-bottom: 10px; border-top: 4px solid #2596be;'>{html_mx}</div>", unsafe_allow_html=True)
            else:
                st.warning(f"No se encontró información en LIGIE para {hs6_input}")
            st.markdown("<hr style='margin: 0px 0 0px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # =====================================================================
        # MÓDULO ESTADOS UNIDOS
        # =====================================================================
        if apply_us:
            st.markdown("<h2 style='color: #0F172A;'><span class='bandera'>🇺🇸</span> Marco Arancelario de Estados Unidos</h2>", unsafe_allow_html=True)
            
            if 'Code' in hts.columns:
                hts_filtrado = hts[hts['Code'].str.startswith(hs6_input)].copy()
            else: hts_filtrado = pd.DataFrame()

            if not hts_filtrado.empty:
                try:
                    with st.expander("📂 Harmonized Tariff Schedule (HTS)", expanded=False):
                        row = hts_filtrado.iloc[0]
                        show_hierarchy_item("Section", row.get('Section'))
                        show_hierarchy_item("Chapter", row.get('Chapter'))
                        show_hierarchy_item("Heading", row.get('Heading'))
                        show_hierarchy_item("Breakdown", row.get('Breakdown'))
                        show_hierarchy_item("Subheading", row.get('Subheading'))
                except: pass

                # --- NUEVA LÓGICA DE PARSEO HTS ---
                parsed_duties = hts_filtrado['General'].apply(parse_hts_duties)
                hts_filtrado['Math Base'] = parsed_duties.apply(lambda x: x[0])
                hts_filtrado['General'] = parsed_duties.apply(lambda x: x[1])
                hts_filtrado['Fixed'] = parsed_duties.apply(lambda x: x[2])

                # Diccionario temporal para agrupar tareas por código
                wizard_queue_dict = {}
                unique_hts_codes = hts_filtrado['Code'].unique()
                has_metals_match = False  
                tmec_codes_clean_list = tmec['Code'].astype(str).str.strip().str.zfill(8).str[:8].tolist()
                rvc_codes_clean_list = rvc_db['Code'].astype(str).str.strip().str.zfill(8).str[:8].tolist() if not rvc_db.empty else []
                
                for code in unique_hts_codes:
                    # Inicializamos la estructura para cada código
                    wizard_queue_dict[code] = {'hts_8': code, 'metals_task': None, 'sec122_task': None, 'auto_task': None, 'tmec_auto_task': None, 'mhdv_task': None, 'tmec_mhdv_task': None, 'wood_task': None, 'semi_task': None}
                    
                    # --- LÓGICA COLA WIZARD PARA METALES ---
                    children = get_10digit_children(code, metals_db, auxiliar)
                    is_outside_ch = str(code)[:2] not in ['72', '73', '74', '76']
                    
                    if not children.empty:
                        has_metals_match = True
                        
                        # Simulamos y validamos jerárquicamente a todos los hijos
                        unique_metal_duties = set()
                        for c_code in children['Code']:
                            m_code, m_duty = get_direct_matches(c_code, metals_db)
                            unique_metal_duties.add(m_duty)
                            
                        if len(unique_metal_duties) == 1:
                            shared_duty = unique_metal_duties.pop()
                            if shared_duty in [50.0, 25.0, "Annex III", "Annex I-C"]:
                                wizard_queue_dict[code]['metals_task'] = {'type': 'annex', 'annex_type': shared_duty}
                            else:
                                if is_outside_ch and shared_duty not in [0.0, "0", "0.0"]:
                                    wizard_queue_dict[code]['metals_task'] = {'type': 'fixed_outside', 'duty': shared_duty}
                                else:
                                    st.session_state.user_metals_decisions[code] = shared_duty
                        else:
                            wizard_queue_dict[code]['metals_task'] = {'type': '10_digit', 'children_df': children}
                    else:
                        match_code, duty = get_direct_matches(code, metals_db)
                        if match_code:
                            has_metals_match = True
                            if duty in [50.0, 25.0, "Annex III", "Annex I-C"]:
                                wizard_queue_dict[code]['metals_task'] = {'type': 'annex', 'annex_type': duty}
                            else:
                                if is_outside_ch and duty not in [0.0, "0", "0.0"]:
                                    wizard_queue_dict[code]['metals_task'] = {'type': 'fixed_outside', 'duty': duty}
                                else:
                                    st.session_state.user_metals_decisions[code] = duty

                    # --- LÓGICA COLA WIZARD PARA SEC 122 ---
                    match_122 = sec122[sec122['code'] == code]
                    
                    scope_val = ""
                    desc_val = ""
                    if not match_122.empty:
                        scope_val = str(match_122.iloc[0].get('scope', '')).lower()
                        desc_val = str(match_122.iloc[0].get('description', ''))
                        
                    needs_wizard = False
                    task_dict = {'type': 'sec122', 'scope': scope_val, 'desc': desc_val, 'children_df': None}
                    
                    direct_exc_code, _ = get_direct_matches(code, exc_122_db)
                    
                    if direct_exc_code:
                        # Cualquier código exento por Auto, MHDV, Wood o Semi requiere ir al Wizard
                        # para poder reaccionar en vivo y aplicar el 10% si el usuario rechaza la exclusión
                        needs_wizard = True
                    else:
                        exc_children = get_10digit_children(code, exc_122_db, auxiliar)
                        if not exc_children.empty:
                            needs_wizard = True
                            task_dict['children_df'] = exc_children
                        else:
                            if 'ex' in scope_val or 'aircraft' in scope_val:
                                needs_wizard = True
                                
                    if needs_wizard:
                        wizard_queue_dict[code]['sec122_task'] = task_dict
                    else:
                        if code not in st.session_state.user_sec122_decisions:
                            st.session_state.user_sec122_decisions[code] = 0.0 if not match_122.empty else 10.0

                    # --- LÓGICA COLA WIZARD PARA AUTOS ---
                    is_code_tmec = code in tmec_codes_clean_list
                    auto_children = get_10digit_children(code, auto_db, auxiliar)
                    if not auto_children.empty:
                        # Simulamos y validamos jerárquicamente a todos los hijos
                        unique_auto_results = set()
                        for c_code in auto_children['Code']:
                            m_code, m_duty, m_cat = get_auto_match(c_code, auto_db)
                            unique_auto_results.add((m_duty, m_cat))
                            
                        if len(unique_auto_results) == 1:
                            shared_duty, shared_cat = unique_auto_results.pop()
                            # AHORA: Requerimos validación de la descripción en el Wizard
                            wizard_queue_dict[code]['auto_task'] = {'type': 'direct', 'duty': shared_duty, 'category': shared_cat}
                            if is_code_tmec and str(shared_cat).strip().lower() == 'autoparts':
                                wizard_queue_dict[code]['tmec_auto_task'] = {'duty': shared_duty, 'category': shared_cat}
                        else:
                            wizard_queue_dict[code]['auto_task'] = {'type': '10_digit', 'children_df': auto_children}
                    else:
                        match_auto_code, auto_duty, auto_cat = get_auto_match(code, auto_db)
                        if match_auto_code:
                            # AHORA: Requerimos validación de la descripción en el Wizard
                            wizard_queue_dict[code]['auto_task'] = {'type': 'direct', 'duty': auto_duty, 'category': auto_cat}
                            if is_code_tmec and str(auto_cat).strip().lower() == 'autoparts':
                                wizard_queue_dict[code]['tmec_auto_task'] = {'duty': auto_duty, 'category': auto_cat}
                
                # --- LÓGICA COLA WIZARD PARA MHDV ---
                    mhdv_children = get_10digit_children(code, mhdv_db, auxiliar)
                    if not mhdv_children.empty:
                        unique_mhdv_results = set()
                        for c_code in mhdv_children['Code']:
                            m_code, m_duty, m_cat = get_mhdv_match(c_code, mhdv_db)
                            unique_mhdv_results.add((m_duty, m_cat))
                        if len(unique_mhdv_results) == 1:
                            shared_duty, shared_cat = unique_mhdv_results.pop()
                            wizard_queue_dict[code]['mhdv_task'] = {'type': 'direct', 'duty': shared_duty, 'category': shared_cat}
                            if is_code_tmec and str(shared_cat).strip().lower() == 'parts':
                                wizard_queue_dict[code]['tmec_mhdv_task'] = {'duty': shared_duty, 'category': shared_cat}
                        else:
                            wizard_queue_dict[code]['mhdv_task'] = {'type': '10_digit', 'children_df': mhdv_children}
                    else:
                        match_mhdv_code, mhdv_duty, mhdv_cat = get_mhdv_match(code, mhdv_db)
                        if match_mhdv_code:
                            wizard_queue_dict[code]['mhdv_task'] = {'type': 'direct', 'duty': mhdv_duty, 'category': mhdv_cat}
                            if is_code_tmec and str(mhdv_cat).strip().lower() == 'parts':
                                wizard_queue_dict[code]['tmec_mhdv_task'] = {'duty': mhdv_duty, 'category': mhdv_cat}

                # --- LÓGICA COLA WIZARD PARA WOOD ---
                    wood_children = get_10digit_children(code, wood_db, auxiliar)
                    if not wood_children.empty:
                        unique_wood_results = set()
                        for c_code in wood_children['Code']:
                            m_code, m_duty, m_cat = get_wood_match(c_code, wood_db)
                            unique_wood_results.add((m_duty, m_cat))
                        if len(unique_wood_results) == 1:
                            shared_duty, shared_cat = unique_wood_results.pop()
                            if str(shared_cat).strip().lower() == 'kitchen cabinets and vanities':
                                wizard_queue_dict[code]['wood_task'] = {'type': 'direct', 'duty': shared_duty, 'category': shared_cat}
                            else:
                                st.session_state.user_wood_decisions[code] = {'duty': shared_duty, 'category': shared_cat}
                        else:
                            # Hijos mixtos: solo mandamos al wizard si alguno es kitchen cabinets
                            has_kitchen = any(
                                str(get_wood_match(c, wood_db)[2]).strip().lower() == 'kitchen cabinets and vanities'
                                for c in wood_children['Code']
                            )
                            if has_kitchen:
                                wizard_queue_dict[code]['wood_task'] = {'type': '10_digit', 'children_df': wood_children}
                            else:
                                # Guardamos el primero disponible o iteramos cada hijo directo
                                for c_code in wood_children['Code']:
                                    m_code, m_duty, m_cat = get_wood_match(c_code, wood_db)
                                    if m_code:
                                        st.session_state.user_wood_decisions[code] = {'duty': m_duty, 'category': m_cat}
                                        break
                    else:
                        match_wood_code, wood_duty, wood_cat = get_wood_match(code, wood_db)
                        if match_wood_code:
                            if str(wood_cat).strip().lower() == 'kitchen cabinets and vanities':
                                wizard_queue_dict[code]['wood_task'] = {'type': 'direct', 'duty': wood_duty, 'category': wood_cat}
                            else:
                                st.session_state.user_wood_decisions[code] = {'duty': wood_duty, 'category': wood_cat}

                # --- LÓGICA COLA WIZARD PARA SEMI (Semiconductors) ---
                    match_semi_code, semi_duty = get_semi_match(code, semi_db)
                    if match_semi_code:
                        wizard_queue_dict[code]['semi_task'] = {'type': 'direct', 'duty': semi_duty}

                # Construimos la cola final filtrando solo los códigos que requieran interacción
                wizard_queue = [v for v in wizard_queue_dict.values() if v['metals_task'] or v['sec122_task'] or v['auto_task'] or v['tmec_auto_task'] or v['mhdv_task'] or v['tmec_mhdv_task'] or v['wood_task'] or v['semi_task']]
                
                if wizard_queue:
                    if st.session_state.wizard_step >= len(wizard_queue):
                        st.session_state.wizard_step = len(wizard_queue) - 1
                    
                    current_item = wizard_queue[st.session_state.wizard_step]
                    current_hts = current_item['hts_8']
                    metals_task = current_item['metals_task']
                    sec122_task = current_item['sec122_task']
                    auto_task = current_item['auto_task']
                    tmec_auto_task = current_item['tmec_auto_task']
                    mhdv_task = current_item['mhdv_task']
                    tmec_mhdv_task = current_item['tmec_mhdv_task']
                    wood_task = current_item['wood_task']
                    semi_task = current_item['semi_task']
                    
                    trigger_spaces = " " * st.session_state.get('wizard_close_trigger', 0)
                    
                    # Títulos dinámicos basados en la concurrencia de tareas
                    tasks_count = sum([1 for t in [metals_task, sec122_task, auto_task, tmec_auto_task, mhdv_task, tmec_mhdv_task, wood_task, semi_task] if t])
                    if tasks_count > 1:
                        w_title_base = "⚠️ Clasificación Requerida: Múltiples Secciones"
                        w_msg = "Este producto requiere validación múltiple. Seleccione las características correspondientes."
                        w_color = "#3b82f6"
                    elif sec122_task:
                        w_title_base = "⚠️ Clasificación Requerida: Sección 122"
                        w_msg = "Seleccione las características del producto para determinar el arancel aplicable de la Section 122."
                        w_color = "#008889"
                    elif auto_task:
                        w_title_base = "⚠️ Clasificación Requerida: Sec 232 (Auto)"
                        w_msg = "Seleccione las características del producto para determinar el arancel de automóviles/autopartes."
                        w_color = "#f59e0b"
                    elif tmec_auto_task:
                        w_title_base = "⚠️ Clasificación Requerida: Autopartes TMEC"
                        w_msg = "Determine si su producto cumple con las reglas de origen específicas para autopartes TMEC."
                        w_color = "#10b981"
                    elif semi_task:
                        w_title_base = "⚠️ Clasificación Requerida: Sec 232 (Semiconductors)"
                        w_msg = "Determine si el semiconductor o sus derivados están sujetos al arancel de la Sección 232."
                        w_color = "#6366f1"
                    else:
                        w_title_base = "⚠️ Clasificación Requerida: Metales (Acero, Aluminio, Cobre)"
                        w_msg = "Seleccione las características del producto para determinar el arancel de metales aplicable."
                        w_color = "#2596be"
                        
                    w_title = w_title_base if st.session_state.wizard_expanded else f"✅ Clasificación Completada{trigger_spaces}"
                    
                    with st.expander(w_title, expanded=st.session_state.wizard_expanded):
                        st.markdown(f"""
                        <div style='padding: 15px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 5px solid {w_color}; border-radius: 6px; margin-bottom: 20px;'>
                            <p style='margin:0; font-size: 0.95rem; color: #0F172A;'>{w_msg}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        col_wiz_1, col_wiz_2 = st.columns([2.5, 1.5])
                        
                        duty_metals_result = "0"
                        duty_tmec_metals_result = 0.0
                        show_tmec_metals_card = False
                        duty_sec122_result = 10.0
                        duty_auto_result = 0.0
                        cat_auto_result = ""
                        duty_tmec_auto_result = 0.0
                        show_tmec_auto_card = False
                        duty_mhdv_result = 0.0
                        cat_mhdv_result = ""
                        duty_tmec_mhdv_result = 0.0
                        show_tmec_mhdv_card = False
                        duty_wood_result = 0.0
                        cat_wood_result = ""
                        duty_semi_result = 0.0
                        
                        with col_wiz_1:
                            has_previous_question = False
                            product_claimed_by = None # NUEVO: Controlador de jerarquía Sec 232
                            
                            # --- 1. PREGUNTA UNIFICADA A 10 DÍGITOS ---
                            shared_children_df = None
                            if metals_task and metals_task.get('type') == '10_digit' and not metals_task['children_df'].empty:
                                shared_children_df = metals_task['children_df']
                            elif sec122_task and sec122_task.get('children_df') is not None and not sec122_task['children_df'].empty:
                                shared_children_df = sec122_task['children_df']
                            elif auto_task and auto_task.get('type') == '10_digit' and not auto_task['children_df'].empty:
                                shared_children_df = auto_task['children_df']
                            elif mhdv_task and mhdv_task.get('type') == '10_digit' and not mhdv_task['children_df'].empty:
                                shared_children_df = mhdv_task['children_df']
                            elif wood_task and wood_task.get('type') == '10_digit' and not wood_task['children_df'].empty:
                                shared_children_df = wood_task['children_df']

                            shared_selected_desc = None
                            if shared_children_df is not None:
                                st.markdown(f"**Especificación (Fracción {current_hts}):** Seleccione el producto a 10 dígitos:")
                                descriptions = shared_children_df['Description'].tolist()
                                shared_selected_desc = st.radio("L_shared", descriptions, key=f"rad_shared_10_{current_hts}", label_visibility="collapsed")
                                has_previous_question = True

                            # --- 2. EVALUACIÓN DE SEMI (Jerarquía 1) ---
                            if semi_task:
                                temp_semi_duty = semi_task.get('duty', 0.0)
                                if has_previous_question: st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

                                st.markdown(
                                    f"**Sec 232 Semiconductors (Fracción {current_hts}):** "
                                    f"¿El semiconductor o sus derivados cumplen con alguna de las siguientes características?\n\n"
                                    f"&nbsp;&nbsp;&nbsp;**a.** TPP mayor a 14,000 y menor a 17,500, con DRAM mayor a 4,500 GB/s y menor a 5,000 GB/s.\n\n"
                                    f"&nbsp;&nbsp;&nbsp;**b.** TPP mayor a 20,800 y menor a 21,100, con DRAM mayor a 5,800 GB/s y menor a 6,200 GB/s."
                                )
                                ans_semi_specs = st.radio("semi_specs", ["Sí", "No"], key=f"rad_semi_specs_{current_hts}", label_visibility="collapsed")
                                has_previous_question = True

                                if ans_semi_specs == "Sí":
                                    product_claimed_by = 'Semi'
                                    st.markdown(
                                        f"**Sec 232 Semiconductors (Fracción {current_hts}):** "
                                        f"¿El producto será destinado a alguno de los siguientes usos en EUA?\n\n"
                                        f"&nbsp;&nbsp;&nbsp;**a.** Centros de datos.\n\n"
                                        f"&nbsp;&nbsp;&nbsp;**b.** Reemplazos o reparaciones.\n\n"
                                        f"&nbsp;&nbsp;&nbsp;**c.** Investigación y desarrollo.\n\n"
                                        f"&nbsp;&nbsp;&nbsp;**d.** Uso de startups.\n\n"
                                        f"&nbsp;&nbsp;&nbsp;**e.** Aplicaciones de consumo no destinadas a centros de datos.\n\n"
                                        f"&nbsp;&nbsp;&nbsp;**f.** Aplicaciones industriales civiles no destinadas a centros de datos.\n\n"
                                        f"&nbsp;&nbsp;&nbsp;**g.** Aplicaciones en el sector público."
                                    )
                                    ans_semi_use = st.radio("semi_use", ["No", "Sí"], key=f"rad_semi_use_{current_hts}", label_visibility="collapsed")
                                    if ans_semi_use == "Sí": duty_semi_result = 0.0
                                    else: duty_semi_result = temp_semi_duty
                                else:
                                    duty_semi_result = 0.0

                            # --- 3. EVALUACIÓN DE AUTOS & TMEC (Jerarquía 2) ---
                            if auto_task and not product_claimed_by:
                                temp_auto_duty = 0.0
                                temp_auto_cat = ""
                                if auto_task.get('type') == '10_digit':
                                    children_df = auto_task.get('children_df')
                                    if children_df is not None and not children_df.empty and shared_selected_desc:
                                        row_match = children_df[children_df['Description'] == shared_selected_desc]
                                        if not row_match.empty:
                                            selected_code = row_match.iloc[0]['Code']
                                            match_auto_code, auto_duty, auto_cat = get_auto_match(selected_code, auto_db)
                                            if match_auto_code:
                                                temp_auto_duty = auto_duty
                                                temp_auto_cat = auto_cat
                                else:
                                    temp_auto_duty = auto_task.get('duty', 0.0)
                                    temp_auto_cat = auto_task.get('category', '')

                                if temp_auto_cat:
                                    if has_previous_question: st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                    clean_cat = str(temp_auto_cat).strip().lower()
                                    if clean_cat == 'automobile':
                                        st.markdown(f"**Sec 232 Autos (Fracción {current_hts}):** ¿El artículo se identifica con la siguiente descripción?\n\n*Passenger vehicles (sedans, sport utility vehicles, crossover utility vehicles, minivans and cargo vans) and light trucks.*")
                                    else:
                                        st.markdown(f"**Sec 232 Autos (Fracción {current_hts}):** ¿El artículo es una parte de *\"passenger vehicles (sedans, sport utility vehicles, crossover utility vehicles, minivans and cargo vans) and light trucks\"*?")
                                    
                                    ans_auto_val = st.radio("auto_val", ["Sí", "No"], key=f"rad_auto_val_{current_hts}", label_visibility="collapsed")
                                    has_previous_question = True
                                    
                                    if ans_auto_val == "Sí":
                                        product_claimed_by = 'Auto'
                                        # Antigüedad solo si NO es autoparte
                                        if clean_cat == 'automobile':
                                            st.markdown(f"**Sec 232 Autos (Fracción {current_hts}):** ¿El vehículo es antiguo (25 años o más desde su año de fabricación)?")
                                            ans_auto_antiguo = st.radio("auto_antiguo", ["No", "Sí"], key=f"rad_auto_antiguo_{current_hts}", label_visibility="collapsed")
                                            if ans_auto_antiguo == "Sí":
                                                duty_auto_result = 0.0
                                                cat_auto_result = ""
                                            else:
                                                duty_auto_result = temp_auto_duty
                                                cat_auto_result = temp_auto_cat
                                        else:
                                            duty_auto_result = temp_auto_duty
                                            cat_auto_result = temp_auto_cat
                                            
                                            # Evaluación TMEC pegada a la confirmación de Autoparte
                                            is_code_tmec = current_hts in tmec_codes_clean_list
                                            if is_code_tmec:
                                                show_tmec_auto_card = True
                                                st.markdown(f"**Autopartes TMEC (Fracción {current_hts}):** ¿Su producto corresponde a *automobile knock-down kits or parts compilations*?")
                                                ans_kd = st.radio("kd_auto", ["No", "Sí"], key=f"rad_kd_{current_hts}", label_visibility="collapsed")
                                                if ans_kd == "Sí": duty_tmec_auto_result = duty_auto_result
                                                else: duty_tmec_auto_result = 0.0
                                    else:
                                        duty_auto_result = 0.0
                                        cat_auto_result = ""
                            elif auto_task:
                                duty_auto_result = 0.0
                                cat_auto_result = ""

                            # --- 4. EVALUACIÓN DE MHDV & TMEC (Jerarquía 3) ---
                            if mhdv_task and not product_claimed_by:
                                temp_mhdv_duty = 0.0
                                temp_mhdv_cat = ""
                                if mhdv_task.get('type') == '10_digit':
                                    children_df = mhdv_task.get('children_df')
                                    if children_df is not None and not children_df.empty and shared_selected_desc:
                                        row_match = children_df[children_df['Description'] == shared_selected_desc]
                                        if not row_match.empty:
                                            selected_code = row_match.iloc[0]['Code']
                                            match_mhdv_code, mhdv_duty, mhdv_cat = get_mhdv_match(selected_code, mhdv_db)
                                            if match_mhdv_code:
                                                temp_mhdv_duty = mhdv_duty
                                                temp_mhdv_cat = mhdv_cat
                                else:
                                    temp_mhdv_duty = mhdv_task.get('duty', 0.0)
                                    temp_mhdv_cat = mhdv_task.get('category', '')

                                if temp_mhdv_cat:
                                    if has_previous_question: st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                    clean_mhdv_cat = str(temp_mhdv_cat).strip().lower()

                                    if clean_mhdv_cat == 'mhdv':
                                        st.markdown(f"**Sec 232 MHDV (Fracción {current_hts}):** ¿El artículo se identifica con la siguiente descripción?\n\n*Medium- and heavy-duty vehicles.*")
                                    elif clean_mhdv_cat == 'buses':
                                        st.markdown(f"**Sec 232 MHDV (Fracción {current_hts}):** ¿El artículo se identifica con la siguiente descripción?\n\n*Buses or Other Vehicles.*")
                                    else:
                                        st.markdown(f"**Sec 232 MHDV (Fracción {current_hts}):** ¿El artículo es una parte de *medium- and heavy-duty vehicles o buses*?")

                                    ans_mhdv_val = st.radio("mhdv_val", ["Sí", "No"], key=f"rad_mhdv_val_{current_hts}", label_visibility="collapsed")
                                    has_previous_question = True

                                    if ans_mhdv_val == "Sí":
                                        product_claimed_by = 'MHDV'
                                        # Antigüedad solo si NO es parte
                                        if clean_mhdv_cat in ['mhdv', 'buses']:
                                            st.markdown(f"**Sec 232 MHDV (Fracción {current_hts}):** ¿El vehículo es antiguo (25 años o más desde su año de fabricación)?")
                                            ans_mhdv_antiguo = st.radio("mhdv_antiguo", ["No", "Sí"], key=f"rad_mhdv_antiguo_{current_hts}", label_visibility="collapsed")
                                            if ans_mhdv_antiguo == "Sí":
                                                duty_mhdv_result = 0.0
                                                cat_mhdv_result = ""
                                            else:
                                                duty_mhdv_result = temp_mhdv_duty
                                                cat_mhdv_result = temp_mhdv_cat
                                        else:
                                            duty_mhdv_result = temp_mhdv_duty
                                            cat_mhdv_result = temp_mhdv_cat
                                            
                                            # TMEC aplica a partes
                                            is_code_tmec = current_hts in tmec_codes_clean_list
                                            if is_code_tmec:
                                                show_tmec_mhdv_card = True
                                                st.markdown(f"**MHDV TMEC (Fracción {current_hts}):** ¿Su producto corresponde a *medium- and heavy-duty vehicle knock-down kits or parts compilations*?")
                                                ans_kd_mhdv = st.radio("kd_mhdv", ["No", "Sí"], key=f"rad_kd_mhdv_{current_hts}", label_visibility="collapsed")
                                                if ans_kd_mhdv == "Sí": duty_tmec_mhdv_result = duty_mhdv_result
                                                else: duty_tmec_mhdv_result = 0.0
                                    else:
                                        duty_mhdv_result = 0.0
                                        cat_mhdv_result = ""
                            elif mhdv_task:
                                duty_mhdv_result = 0.0
                                cat_mhdv_result = ""

                            # --- 5. EVALUACIÓN DE METALES (Jerarquía 4) ---
                            if metals_task and not product_claimed_by:
                                active_annex = None
                                pre_duty = None
                                
                                if metals_task['type'] == '10_digit':
                                    children_df = metals_task['children_df']
                                    row_match = children_df[children_df['Description'] == shared_selected_desc]
                                    if not row_match.empty:
                                        selected_code = row_match.iloc[0]['Code']
                                        match_code, duty_val = get_direct_matches(selected_code, metals_db)
                                        if match_code:
                                            if duty_val in [50.0, 25.0, "Annex III", "Annex I-C"]: active_annex = duty_val
                                            else: pre_duty = duty_val
                                elif metals_task['type'] == 'annex': active_annex = metals_task['annex_type']
                                elif metals_task.get('type') == 'fixed_outside': pre_duty = metals_task['duty']
                                    
                                is_outside_ch = str(current_hts)[:2] not in ['72', '73', '74', '76']
                                meets_15_pct = "Sí"
                                needs_15_pct_check = is_outside_ch and (active_annex is not None or (pre_duty is not None and pre_duty not in [0.0, "0", "0.0"]))
                                
                                if needs_15_pct_check:
                                    if has_previous_question: st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                    st.markdown(f"**Metales (Fracción {current_hts}):** ¿Cuál es el peso conjunto de Acero, Aluminio y/o Cobre en el producto?")
                                    meets_15_pct = st.radio("15pct", ["Igual o mayor al 15%", "Menor al 15%"], key=f"rad_15_{current_hts}", label_visibility="collapsed")
                                    has_previous_question = True
                                    
                                if meets_15_pct == "Menor al 15%":
                                    duty_metals_result = 0.0
                                else:
                                    product_claimed_by = 'Metals'
                                    if pre_duty is not None: duty_metals_result = pre_duty
                                        
                                    if active_annex is not None:
                                        if has_previous_question and not needs_15_pct_check: st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                        st.markdown(f"**Metales (Fracción {current_hts}):** ¿Qué porcentaje del metal fue fundido y moldeado en los Estados Unidos?")
                                        usa_melted = st.radio("Melted", ["Menos de 85%", "Igual o mayor a 85%"], key=f"rad_annex_{current_hts}", label_visibility="collapsed")
                                        has_previous_question = True
                                        
                                        base_duty = hts_filtrado[hts_filtrado['Code'] == current_hts]['Math Base'].iloc[0]
                                        
                                        if usa_melted == "Igual o mayor a 85%":
                                            if active_annex == "Annex III":
                                                calc_duty = max(0.0, 10.0 - base_duty)
                                            elif active_annex == "Annex I-C":
                                                calc_duty = max(0.0, 10.0 - base_duty)
                                            else:
                                                calc_duty = 10.0
                                        else:
                                            if active_annex == "Annex III":
                                                calc_duty = max(0.0, 15.0 - base_duty)
                                            elif active_annex == "Annex I-C":
                                                is_code_tmec = current_hts in tmec_codes_clean_list
                                                is_code_rvc = current_hts in rvc_codes_clean_list
                                                
                                                if is_code_tmec or is_code_rvc:
                                                    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                                    st.markdown(f"**Metales TMEC (Fracción {current_hts}):** ¿Su artículo cuenta con el umbral de \"Valor de Contenido Regional\"? Puede revisar más información en la <a href='https://hts.usitc.gov/reststop/file?release=currentRelease&filename=General%20Note%2011' target='_blank'>General Note 11</a>.", unsafe_allow_html=True)
                                                    ans_rvc = st.radio("RVC_IC", ["No", "Sí"], key=f"rad_rvc_ic_{current_hts}", label_visibility="collapsed")
                                                    
                                                    if ans_rvc == "Sí":
                                                        show_tmec_metals_card = True
                                                        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                                        st.markdown(f"**Metales TMEC (Fracción {current_hts}):** Seleccione el porcentaje de contenido estadounidense respecto al valor total del producto (valores >= 40% resultan en el mismo arancel):")
                                                        us_content = st.slider("US Content %", min_value=0, max_value=40, value=0, step=1, key=f"num_us_content_{current_hts}", label_visibility="collapsed")
                                                        
                                                        tmec_calc = 0.25 * (100.0 - us_content) + 0.25 * max(0.0, us_content - 40.0)
                                                        effective_floor = max(15.0, tmec_calc)
                                                        duty_tmec_metals_result = max(0.0, effective_floor - base_duty)
                                                
                                                calc_duty = 25.0
                                            elif active_annex == 50.0:
                                                calc_duty = 50.0
                                            elif active_annex == 25.0:
                                                is_motorcycle_eligible = str(current_hts)[:2] in ['84', '85', '87']
                                                
                                                if is_motorcycle_eligible:
                                                    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                                    st.markdown(f"**Metales (Fracción {current_hts}):** ¿El producto será usado exclusivamente en la manufactura de motocicletas?")
                                                    is_for_motorcycles = st.radio("Moto", ["No", "Sí"], key=f"rad_moto_{current_hts}", label_visibility="collapsed")
                                                    
                                                    if is_for_motorcycles == "Sí":
                                                        calc_duty = 0.0
                                                    else:
                                                        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                                        st.markdown(f"**Metales (Fracción {current_hts}):** ¿Esta parte tiene como uso final la manufactura de mobile industrial equipment listados en el <a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-I-C.pdf' target='_blank'>Annex I-C</a>, o agricultural/fixed industrial equipment listados en el <a href='https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-III.pdf' target='_blank'>Annex III</a>?", unsafe_allow_html=True)
                                                        is_for_machinery = st.radio("Mach", ["No", "Sí"], key=f"rad_mach_{current_hts}", label_visibility="collapsed")
                                                        calc_duty = max(0.0, 15.0 - base_duty) if is_for_machinery == "Sí" else 25.0
                                                else:
                                                    calc_duty = 25.0
                                                    
                                        duty_metals_result = calc_duty

                            # --- 6. EVALUACIÓN DE WOOD (Jerarquía 5) ---
                            if wood_task and not product_claimed_by:
                                temp_wood_duty = 0.0
                                temp_wood_cat = ""
                                if wood_task.get('type') == '10_digit':
                                    children_df = wood_task.get('children_df')
                                    if children_df is not None and not children_df.empty and shared_selected_desc:
                                        row_match = children_df[children_df['Description'] == shared_selected_desc]
                                        if not row_match.empty:
                                            selected_code = row_match.iloc[0]['Code']
                                            match_wood_code, wd, wc = get_wood_match(selected_code, wood_db)
                                            if match_wood_code:
                                                temp_wood_duty = wd
                                                temp_wood_cat = wc
                                else:
                                    temp_wood_duty = wood_task.get('duty', 0.0)
                                    temp_wood_cat = wood_task.get('category', '')

                                if temp_wood_cat:
                                    clean_wood_cat = str(temp_wood_cat).strip().lower()
                                    if has_previous_question: st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

                                    if clean_wood_cat == 'kitchen cabinets and vanities':
                                        st.markdown(f"**Sec 232 Wood (Fracción {current_hts}):** ¿El artículo es un gabinete o tocador de cocina, o una parte de estos?")
                                        ans_wood_val = st.radio("wood_val", ["Sí", "No"], key=f"rad_wood_val_{current_hts}", label_visibility="collapsed")
                                        has_previous_question = True
                                        if ans_wood_val == "Sí":
                                            product_claimed_by = 'Wood'
                                            duty_wood_result = temp_wood_duty
                                            cat_wood_result = temp_wood_cat
                                        else:
                                            duty_wood_result = 0.0
                                            cat_wood_result = ""
                                    else:
                                        if wood_task.get('type') == '10_digit' and shared_selected_desc:
                                            duty_wood_result = temp_wood_duty
                                            cat_wood_result = temp_wood_cat
                                        elif wood_task.get('type') == 'direct':
                                            duty_wood_result = temp_wood_duty
                                            cat_wood_result = temp_wood_cat
                                            
                                        if duty_wood_result > 0: product_claimed_by = 'Wood'

                            # --- 7. EVALUACIÓN DE SEC 122 (Dependiente de Exclusiones) ---
                            if sec122_task:
                                scope_val = sec122_task.get('scope', '')
                                desc_val = sec122_task.get('desc', '')
                                
                                # Verificamos si la jerarquía que reclamó el producto retuvo el arancel (no fue exento por antigüedad/uso)
                                duty_retained = False
                                if product_claimed_by == 'Auto' and duty_auto_result > 0: duty_retained = True
                                elif product_claimed_by == 'MHDV' and duty_mhdv_result > 0: duty_retained = True
                                elif product_claimed_by == 'Wood' and duty_wood_result > 0: duty_retained = True
                                elif product_claimed_by == 'Semi' and duty_semi_result > 0: duty_retained = True

                                # Si fue reclamado por jerarquías exentas (No-Metales) y conservó su arancel, la Sec 122 no aplica
                                if product_claimed_by in ['Auto', 'MHDV', 'Wood', 'Semi'] and duty_retained:
                                    duty_sec122_result = 0.0
                                else:
                                    if 'ex' in scope_val or 'aircraft' in scope_val:
                                        if has_previous_question: st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
                                        if 'ex' in scope_val:
                                            st.markdown(f"**Sec 122 (Fracción {current_hts}):** ¿Su producto corresponde **exactamente** a la siguiente descripción?")
                                            st.info(desc_val)
                                        else: 
                                            st.markdown(f"**Sec 122 (Fracción {current_hts}):** ¿El producto consiste en partes, componentes o ensamblajes de aeronaves civiles?")
                                            
                                        ans_scope = st.radio("sec122_air", ["No", "Sí"], key=f"rad_122_scope_{current_hts}", label_visibility="collapsed")
                                        if ans_scope == "Sí": duty_sec122_result = 0.0
                                        else: duty_sec122_result = 10.0
                                    else:
                                        duty_sec122_result = 10.0

                        with col_wiz_2:
                            # Renderizado dinámico ocultando tarjetas excluidas por jerarquía
                            if metals_task and product_claimed_by in [None, 'Metals']:
                                try:
                                    dm_val = float(duty_metals_result)
                                    val_m_str = f"{dm_val:.2f}%"
                                except: val_m_str = str(duty_metals_result)
                                st.markdown(f"""
                                <div class="metric-container" style="padding: 10px; border-top: 4px solid #2596be; text-align: center; margin-bottom: 10px;">
                                    <div class="metric-title" style="margin-bottom: 5px;">Arancel Metales</div>
                                    <div class="metric-value" style="font-size: 1.5rem;">{val_m_str}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if show_tmec_metals_card:
                                    try:
                                        dtm_val = float(duty_tmec_metals_result)
                                        val_tm_str = f"{dtm_val:.2f}%"
                                    except: val_tm_str = str(duty_tmec_metals_result)
                                    st.markdown(f"""
                                    <div class="metric-container" style="padding: 10px; border-top: 4px solid #166534; text-align: center; margin-bottom: 10px;">
                                        <div class="metric-title" style="margin-bottom: 5px;">Metales TMEC</div>
                                        <div class="metric-value" style="font-size: 1.5rem;">{val_tm_str}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                            if sec122_task and product_claimed_by in [None, 'Metals']:
                                try:
                                    ds_val = float(duty_sec122_result)
                                    val_s_str = f"{ds_val:.2f}%"
                                except: val_s_str = str(duty_sec122_result)
                                st.markdown(f"""
                                <div class="metric-container" style="padding: 10px; border-top: 4px solid #008889; text-align: center; margin-bottom: 15px;">
                                    <div class="metric-title" style="margin-bottom: 5px;">Arancel Sec 122</div>
                                    <div class="metric-value" style="font-size: 1.5rem;">{val_s_str}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            if auto_task and product_claimed_by in [None, 'Auto']:
                                try:
                                    da_val = float(duty_auto_result)
                                    val_a_str = f"{da_val:.2f}%"
                                except: val_a_str = str(duty_auto_result)
                                st.markdown(f"""
                                <div class="metric-container" style="padding: 10px; border-top: 4px solid #f59e0b; text-align: center; margin-bottom: 15px;">
                                    <div class="metric-title" style="margin-bottom: 5px;">Arancel Autos</div>
                                    <div class="metric-value" style="font-size: 1.5rem;">{val_a_str}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            if show_tmec_auto_card and product_claimed_by in [None, 'Auto']:
                                try:
                                    dta_val = float(duty_tmec_auto_result)
                                    val_ta_str = f"{dta_val:.2f}%"
                                except: val_ta_str = str(duty_tmec_auto_result)
                                st.markdown(f"""
                                <div class="metric-container" style="padding: 10px; border-top: 4px solid #10b981; text-align: center; margin-bottom: 15px;">
                                    <div class="metric-title" style="margin-bottom: 5px;">Autopartes TMEC</div>
                                    <div class="metric-value" style="font-size: 1.5rem;">{val_ta_str}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            if mhdv_task and product_claimed_by in [None, 'MHDV']:
                                try:
                                    dm_val = float(duty_mhdv_result)
                                    val_m_str = f"{dm_val:.2f}%"
                                except: val_m_str = str(duty_mhdv_result)
                                st.markdown(f"""
                                <div class="metric-container" style="padding: 10px; border-top: 4px solid #7c3aed; text-align: center; margin-bottom: 15px;">
                                    <div class="metric-title" style="margin-bottom: 5px;">Arancel MHDV</div>
                                    <div class="metric-value" style="font-size: 1.5rem;">{val_m_str}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            if show_tmec_mhdv_card and product_claimed_by in [None, 'MHDV']:
                                try:
                                    dtm_val = float(duty_tmec_mhdv_result)
                                    val_tm_str = f"{dtm_val:.2f}%"
                                except: val_tm_str = str(duty_tmec_mhdv_result)
                                st.markdown(f"""
                                <div class="metric-container" style="padding: 10px; border-top: 4px solid #a855f7; text-align: center; margin-bottom: 15px;">
                                    <div class="metric-title" style="margin-bottom: 5px;">Partes MHDV TMEC</div>
                                    <div class="metric-value" style="font-size: 1.5rem;">{val_tm_str}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            if wood_task and product_claimed_by in [None, 'Wood']:
                                try:
                                    dw_val = float(duty_wood_result)
                                    val_w_str = f"{dw_val:.2f}%"
                                except: val_w_str = str(duty_wood_result)
                                st.markdown(f"""
                                <div class="metric-container" style="padding: 10px; border-top: 4px solid #84cc16; text-align: center; margin-bottom: 15px;">
                                    <div class="metric-title" style="margin-bottom: 5px;">Arancel Wood</div>
                                    <div class="metric-value" style="font-size: 1.5rem;">{val_w_str}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            if semi_task and product_claimed_by in [None, 'Semi']:
                                try:
                                    dsemi_val = float(duty_semi_result)
                                    val_semi_str = f"{dsemi_val:.2f}%"
                                except: val_semi_str = str(duty_semi_result)
                                st.markdown(f"""
                                <div class="metric-container" style="padding: 10px; border-top: 4px solid #6366f1; text-align: center; margin-bottom: 15px;">
                                    <div class="metric-title" style="margin-bottom: 5px;">Arancel Semiconductors</div>
                                    <div class="metric-value" style="font-size: 1.5rem;">{val_semi_str}</div>
                                </div>
                                """, unsafe_allow_html=True)

                            c_prev, c_next = st.columns(2)
                            if st.session_state.wizard_step > 0:
                                if c_prev.button("Anterior", use_container_width=True):
                                    st.session_state.wizard_step -= 1
                                    st.rerun()
                            
                            is_last = (st.session_state.wizard_step == len(wizard_queue) - 1)
                            btn_label = "Listo" if is_last else "Siguiente"
                            
                            if c_next.button(btn_label, use_container_width=True, type="primary"):
                                
                                if metals_task:
                                    st.session_state.user_metals_decisions[current_hts] = duty_metals_result
                                    if show_tmec_metals_card:
                                        st.session_state.user_tmec_metals_decisions[current_hts] = duty_tmec_metals_result
                                if sec122_task:
                                    st.session_state.user_sec122_decisions[current_hts] = duty_sec122_result
                                if auto_task:
                                    st.session_state.user_auto_decisions[current_hts] = {'duty': duty_auto_result, 'category': cat_auto_result}
                                if show_tmec_auto_card:
                                    st.session_state.user_tmec_auto_decisions[current_hts] = duty_tmec_auto_result
                                if mhdv_task:
                                    st.session_state.user_mhdv_decisions[current_hts] = {'duty': duty_mhdv_result, 'category': cat_mhdv_result}
                                if show_tmec_mhdv_card:
                                    st.session_state.user_tmec_mhdv_decisions[current_hts] = duty_tmec_mhdv_result
                                if wood_task:
                                    st.session_state.user_wood_decisions[current_hts] = {'duty': duty_wood_result, 'category': cat_wood_result}
                                if semi_task:
                                    st.session_state.user_semi_decisions[current_hts] = duty_semi_result
                                
                                if not is_last:
                                    st.session_state.wizard_step += 1
                                else:
                                    st.session_state.wizard_expanded = False
                                    st.session_state.wizard_close_trigger += 1
                                st.rerun()
                            
                            st.markdown(f"<p style='text-align: center; color: #64748B; font-size: 0.85rem; margin-top: 10px;'>Fracción {st.session_state.wizard_step + 1} de {len(wizard_queue)}</p>", unsafe_allow_html=True)

                hts_filtrado = hts_filtrado.merge(sec301[['Code', 'Duty']], left_on='Code', right_on='Code', how='left')
                hts_filtrado.rename(columns={'Duty': 'Sec 301'}, inplace=True)
                hts_filtrado['Sec 301'] = hts_filtrado['Sec 301'].fillna(0.0)
                
                tmec_codes_clean = tmec['Code'].astype(str).str.strip().str.zfill(8).str[:8]
                rvc_codes_clean = rvc_db['Code'].astype(str).str.strip().str.zfill(8).str[:8] if not rvc_db.empty else pd.Series(dtype=str)
                hts_codes_clean = hts_filtrado['Code'].astype(str).str.strip().str.zfill(8).str[:8]
                hts_filtrado['is_tmec'] = hts_codes_clean.isin(tmec_codes_clean)
                hts_filtrado['is_rvc'] = hts_codes_clean.isin(rvc_codes_clean)

                def calculate_metals_row(row):
                    code = row['Code']
                    
                    # 1. Si es la fracción activa actual en el Wizard, mostramos el resultado en tiempo real
                    if wizard_queue and code == current_hts and metals_task:
                        return duty_metals_result
                        
                    # 2. Si el usuario ya tomó la decisión previamente, la respetamos
                    if code in st.session_state.user_metals_decisions:
                        return st.session_state.user_metals_decisions[code]
                    
                    # 3. Si la fracción está "en espera", proyectamos el arancel base lógico por defecto
                    match_code, duty = get_direct_matches(code, metals_db)
                    if match_code:
                        is_outside_ch = str(code)[:2] not in ['72', '73', '74', '76']
                        if is_outside_ch:
                            return 0.0
                            
                        if duty in [50.0, 25.0]:
                            return duty
                        elif duty == "Annex I-C":
                            return 25.0
                        elif duty == "Annex III":
                            base_duty = float(row.get('Math Base', 0.0))
                            return max(0.0, 15.0 - base_duty)
                        return duty
                        
                    return 0.0

                hts_filtrado['Sec 232 (Metals)'] = hts_filtrado.apply(calculate_metals_row, axis=1)
                
                def calculate_sec122_row(row):
                    code = row['Code']
                    
                    # 1. Si es la fracción activa actual en el Wizard, homologamos con la variable en vivo de las tarjetas
                    if wizard_queue and code == current_hts and sec122_task:
                        return duty_sec122_result
                        
                    # 2. Si ya se guardó la decisión permanente previamente, la respetamos
                    if code in st.session_state.user_sec122_decisions:
                        return st.session_state.user_sec122_decisions[code]
                                
                    # 3. Proyección por defecto para las fracciones en espera
                    direct_exc_code, _ = get_direct_matches(code, exc_122_db)
                    if direct_exc_code: return 0.0
                    
                    exc_children = get_10digit_children(code, exc_122_db, auxiliar)
                    if not exc_children.empty: return 10.0
                    
                    match_122 = sec122[sec122['code'] == code]
                    if not match_122.empty:
                        scope_val = str(match_122.iloc[0].get('scope', '')).lower()
                        if 'ex' in scope_val or 'aircraft' in scope_val:
                            return 10.0
                        return 0.0
                    return 10.0

                hts_filtrado['Sec 122'] = hts_filtrado.apply(calculate_sec122_row, axis=1)
                
                # --- LÓGICA Sec 232 (Auto) ---
                def calculate_autos_base(row):
                    code = row['Code']
                    # 1. Si es la fracción activa actual en el Wizard, homologamos con la variable en vivo de las tarjetas
                    if wizard_queue and code == current_hts and auto_task:
                        return pd.Series([duty_auto_result, cat_auto_result])
                        
                    # 2. Si ya se guardó la decisión permanente previamente, la respetamos
                    if code in st.session_state.user_auto_decisions:
                        dec = st.session_state.user_auto_decisions[code]
                        return pd.Series([dec['duty'], dec['category']])
                            
                    # 3. Proyección por defecto para las fracciones en espera
                    match_code, duty, category = get_auto_match(code, auto_db)
                    return pd.Series([duty, category])
                
                hts_filtrado[['Auto_Duty', 'Auto_Category']] = hts_filtrado.apply(calculate_autos_base, axis=1)

                def calculate_mhdv_base(row):
                    code = row['Code']
                    if wizard_queue and code == current_hts and mhdv_task:
                        return pd.Series([duty_mhdv_result, cat_mhdv_result])
                    if code in st.session_state.user_mhdv_decisions:
                        dec = st.session_state.user_mhdv_decisions[code]
                        return pd.Series([dec['duty'], dec['category']])
                    match_code, duty, category = get_mhdv_match(code, mhdv_db)
                    return pd.Series([duty, category])

                hts_filtrado[['MHDV_Duty', 'MHDV_Category']] = hts_filtrado.apply(calculate_mhdv_base, axis=1)

                def calculate_wood_base(row):
                    code = row['Code']
                    if wizard_queue and code == current_hts and wood_task:
                        # Si el task es 10_digit, el duty ya fue resuelto al hijo seleccionado
                        # y está en duty_wood_result (calculado en el wizard con shared_selected_desc)
                        return pd.Series([duty_wood_result, cat_wood_result])
                    if code in st.session_state.user_wood_decisions:
                        dec = st.session_state.user_wood_decisions[code]
                        return pd.Series([dec['duty'], dec['category']])
                    # Para códigos sin decisión y sin wood_task activo:
                    # Solo retornamos match si el código existe EXACTAMENTE en wood_db (sin herencia jerárquica hacia arriba)
                    hts_str = str(code).strip()
                    exact_match = wood_db[wood_db['Code'] == hts_str]
                    if not exact_match.empty:
                        duty = exact_match.iloc[0].get('Duty', 0.0)
                        category = exact_match.iloc[0].get('Category', '')
                        return pd.Series([duty, category])
                    return pd.Series([0.0, ""])

                hts_filtrado[['Wood_Duty', 'Wood_Category']] = hts_filtrado.apply(calculate_wood_base, axis=1)

                # --- LÓGICA Sec 232 (Semiconductors) ---
                def calculate_semi_row(row):
                    code = row['Code']
                    # 1. Fracción activa en el Wizard → valor en tiempo real
                    if wizard_queue and code == current_hts and semi_task:
                        return duty_semi_result
                    # 2. Decisión ya guardada por el usuario
                    if code in st.session_state.user_semi_decisions:
                        return st.session_state.user_semi_decisions[code]
                    # 3. Proyección por defecto (arancel base del parquet)
                    match_code, duty = get_semi_match(code, semi_db)
                    if match_code:
                        return duty
                    return 0.0

                hts_filtrado['Sec 232 (Semiconductors)'] = hts_filtrado.apply(calculate_semi_row, axis=1)
                
                # =====================================================================
                # NUEVA LÓGICA V5: TABLAS SEPARADAS PARA CHINA Y MÉXICO
                # =====================================================================
                
                # Función auxiliar de formateo
                def smart_pct(val):
                    try:
                        v = float(val)
                        return f"{v:.2f}%"
                    except: return str(val)
                    
                # Nueva función para la regla del 10% en la Sec 122 (Solo para códigos en metals.parquet)
                def format_sec122_duty_row(row):
                    val = row.get('Sec 122', 10.0)
                    code = str(row['Code']).strip()
                    try:
                        v = float(val)
                        if v == 10.0:
                            # 1. Verificamos si el código pertenece a los metales controlados y se le aplicó arancel
                            match_code, _ = get_direct_matches(code, metals_db)
                            children = get_10digit_children(code, metals_db, auxiliar)
                            metals_duty_applied = float(row.get('Sec 232 (Metals)', 0.0)) > 0
                            is_in_metals = (bool(match_code) or not children.empty) and metals_duty_applied
                            
                            # 2. Si está en metals_db y aplica arancel, aplicamos la regla de texto según su capítulo
                            if is_in_metals:
                                cap = code[:2]
                                if cap in ['72', '73']: return "10.00% sobre el contenido que no es de acero"
                                elif cap == '74': return "10.00% sobre el contenido que no es de cobre"
                                elif cap == '76': return "10.00% sobre el contenido que no es de aluminio"
                                else: return "10.00% sobre el contenido que no es de acero/cobre/aluminio"
                        return f"{v:.2f}%"
                    except: return str(val)

                # ---------------------------------------------------------------------
                # 1. PREPARACIÓN DE TABLA: CHINA
                # ---------------------------------------------------------------------
                hts_china = hts_filtrado.copy()

                def apply_hierarchy_china(row):
                    semi = float(row.get('Sec 232 (Semiconductors)', 0.0))
                    auto = float(row.get('Auto_Duty', 0.0))
                    mhdv = float(row.get('MHDV_Duty', 0.0))
                    metals = float(row.get('Sec 232 (Metals)', 0.0))
                    wood = float(row.get('Wood_Duty', 0.0))

                    if semi > 0: auto = mhdv = metals = wood = 0.0
                    elif auto > 0: mhdv = metals = wood = 0.0
                    elif mhdv > 0: metals = wood = 0.0
                    elif metals > 0: wood = 0.0

                    row['Sec 232 (Semiconductors)'] = semi
                    row['Auto_Duty'] = auto
                    row['MHDV_Duty'] = mhdv
                    row['Sec 232 (Metals)'] = metals
                    row['Wood_Duty'] = wood
                    return row

                hts_china = hts_china.apply(apply_hierarchy_china, axis=1)
                
                # 1. Aplicamos el formato de Sec 122 PRIMERO para poder leer el texto en el Total
                hts_china['Sec 122'] = hts_china.apply(format_sec122_duty_row, axis=1)
                
                def calc_total_row_china(row):
                    math_base = row['Math Base']
                    try: duty_metals = float(row['Sec 232 (Metals)'])
                    except: duty_metals = 0.0
                    try: sec301 = float(row['Sec 301'])
                    except: sec301 = 0.0
                    try: duty_autos = float(row['Auto_Duty'])
                    except: duty_autos = 0.0
                    try: duty_mhdv = float(row.get('MHDV_Duty', 0.0))
                    except: duty_mhdv = 0.0
                    try: duty_wood = float(row.get('Wood_Duty', 0.0))
                    except: duty_wood = 0.0
                    try: duty_semi = float(row.get('Sec 232 (Semiconductors)', 0.0))
                    except: duty_semi = 0.0
                    
                    # 2. Lógica para aislar el texto de la Sec 122 si existe
                    sec122_val = row.get('Sec 122', 10.0)
                    sec122_str_append = ""
                    duty_122 = 0.0
                    
                    if isinstance(sec122_val, str) and "sobre el contenido" in sec122_val:
                        sec122_str_append = f" + {sec122_val}"
                    else:
                        try: duty_122 = float(str(sec122_val).replace('%', ''))
                        except: duty_122 = 10.0
                            
                    sum_pct = math_base + duty_metals + sec301 + duty_122 + duty_autos + duty_mhdv + duty_wood + duty_semi
                    fixed = row['Fixed']
                    
                    # 3. Construcción del arancel base
                    if pd.notna(fixed) and fixed:
                        base_str = f"{fixed} + {sum_pct:.2f}%" if sum_pct > 0 else fixed
                    else:
                        if str(row['General']).lower() == 'free' and sum_pct == 0:
                            base_str = "Free"
                        else:
                            base_str = f"{sum_pct:.2f}%"
                            
                    # 4. Concatenación final
                    if sec122_str_append:
                        if base_str in ["Free", "0.00%"]:
                            return sec122_val
                        return f"{base_str}{sec122_str_append}"
                        
                    return base_str

                hts_china['Total'] = hts_china.apply(calc_total_row_china, axis=1)
                hts_china['General'] = hts_china['General'].fillna("")
                hts_china['Fixed'] = hts_china['Fixed'].fillna("")
                
                cols_china = ['Code', 'Description']
                format_dict_china = {'Sec 301': '{:.2f}%'}
                
                if hts_china['General'].astype(str).str.strip().ne("").any():
                    cols_china.append('General')
                if hts_china['Fixed'].astype(str).str.strip().ne("").any():
                    cols_china.append('Fixed')
                
                # Agregamos la columna Sec 122 directamente a la lista
                cols_china.append('Sec 122')
                
                if (hts_china['Sec 232 (Metals)'] > 0).any():
                    cols_china.append('Sec 232 (Metals)')
                    format_dict_china['Sec 232 (Metals)'] = smart_pct
                
                hts_china['Sec 232 (Auto)'] = hts_china['Auto_Duty']
                if (hts_china['Sec 232 (Auto)'] > 0).any():
                    cols_china.append('Sec 232 (Auto)')
                    format_dict_china['Sec 232 (Auto)'] = smart_pct

                hts_china['Sec 232 (mhdv)'] = hts_china['MHDV_Duty']
                if (hts_china['Sec 232 (mhdv)'] > 0).any():
                    cols_china.append('Sec 232 (mhdv)')
                    format_dict_china['Sec 232 (mhdv)'] = smart_pct

                hts_china['Sec 232 (Wood)'] = hts_china['Wood_Duty']
                if (hts_china['Sec 232 (Wood)'] > 0).any():
                    cols_china.append('Sec 232 (Wood)')
                    format_dict_china['Sec 232 (Wood)'] = smart_pct

                if (hts_china['Sec 232 (Semiconductors)'] > 0).any():
                    cols_china.append('Sec 232 (Semiconductors)')
                    format_dict_china['Sec 232 (Semiconductors)'] = smart_pct

                cols_china.append('Sec 301')
                cols_china.append('Total')

                # ---------------------------------------------------------------------
                # 2. PREPARACIÓN DE TABLA: MÉXICO
                # ---------------------------------------------------------------------
                hts_mexico = hts_filtrado.copy()
                
                # --- LÓGICA V5 CORREGIDA: EVITAR PÉRDIDA DE COLUMNA 'Code' ---
                tmec_temp = tmec[['Code', 'Duty']].copy()
                
                # Renombramos 'Duty' a 'Duty_TMEC' y 'Code' a 'Code_8' 
                # para que el merge use una llave única y no modifique el 'Code' original de hts_mexico
                tmec_temp = tmec_temp.rename(columns={'Duty': 'Duty_TMEC', 'Code': 'Code_8'})
                tmec_temp['Code_8'] = tmec_temp['Code_8'].astype(str).str.strip().str.zfill(8).str[:8]
                
                hts_mexico['Code_8'] = hts_mexico['Code'].astype(str).str.strip().str.zfill(8).str[:8]
                
                # Cruce de bases: Al usar 'on="Code_8"', la columna 'Code' original queda intacta
                hts_mexico = hts_mexico.merge(
                    tmec_temp.drop_duplicates('Code_8'), 
                    on='Code_8', 
                    how='left'
                )
                
                def apply_tmec_duty(row):
                    is_tmec = row.get('is_tmec', False)
                    duty_val = row.get('Duty_TMEC')
                    
                    # Si es TMEC y existe el dato en el parquet
                    if pd.notna(is_tmec) and is_tmec and pd.notna(duty_val):
                        raw_duty = str(duty_val).strip()
                        
                        # Escenario: Tasa Compleja (Link a HTS)
                        if "tasa compleja" in raw_duty.lower() or "revisar" in raw_duty.lower():
                            code_str = str(row['Code']).strip().zfill(8)
                            fmt_code = f"{code_str[:4]}.{code_str[4:6]}.{code_str[6:8]}"
                            if len(code_str) > 8:
                                fmt_code += f".{code_str[8:]}"
                                
                            # Cambiamos el Markdown por un link HTML embebido con salto de línea
                            row['General'] = f'<a href="https://hts.usitc.gov/search?query={fmt_code}" target="_blank" style="color: #2596be; text-decoration: none; font-weight: 600;">Tasa Compleja<br>(Revisar Aquí)</a>'
                            row['Math Base'] = 0.0
                            row['Fixed'] = None
                            row['is_complex'] = True
                            return row
                            
                        # Escenario: Tasas mixtas, fijas o Free
                        parts = [p.strip() for p in raw_duty.split('+')]
                        math_base = 0.0
                        fixed_str = None
                        
                        for part in parts:
                            if '%' in part:
                                try:
                                    math_base = float(''.join(c for c in part if c.isdigit() or c == '.'))
                                except: pass
                            else:
                                if part.lower() not in ['free', 'libre', 'ex.', 'ex', 'n/a', '-', '']:
                                    fixed_str = part
                                    
                        row['Math Base'] = math_base
                        row['Fixed'] = fixed_str
                        row['is_complex'] = False
                        
                        if raw_duty.lower() in ['free', 'libre', '0', '0%']:
                            row['General'] = "Free"
                            row['Math Base'] = 0.0 # Reset para asegurar suma limpia
                        else:
                            row['General'] = raw_duty
                            
                        return row
                        
                    row['is_complex'] = False
                    return row

                # Aplicamos la corrección a las filas
                hts_mexico = hts_mexico.apply(apply_tmec_duty, axis=1)
                
                def apply_122_mexico(row):
                    is_tmec = row.get('is_tmec', False)
                    raw_duty = str(row.get('Duty_TMEC', '')).lower()
                    if is_tmec and raw_duty in ['free', 'libre', '0', '0.0', '0%']:
                        return 0.0
                    # En caso contrario, aplicamos la tarifa calculada base 122
                    return row['Sec 122']
                    
                hts_mexico['Sec 122'] = hts_mexico.apply(apply_122_mexico, axis=1)

                def apply_autos_mexico(row):
                    is_tmec = row.get('is_tmec', False)
                    duty = row.get('Auto_Duty', 0.0)
                    category = str(row.get('Auto_Category', '')).strip().lower()
                    code = row['Code']
                    
                    if is_tmec and category == 'autoparts':
                        if wizard_queue and code == current_hts and show_tmec_auto_card:
                            return duty_tmec_auto_result
                        elif code in st.session_state.user_tmec_auto_decisions:
                            return st.session_state.user_tmec_auto_decisions[code]
                        else:
                            return duty
                    return duty
                
                hts_mexico['Sec 232 (Auto)'] = hts_mexico.apply(apply_autos_mexico, axis=1)

                def apply_mhdv_mexico(row):
                    is_tmec = row.get('is_tmec', False)
                    duty = row.get('MHDV_Duty', 0.0)
                    category = str(row.get('MHDV_Category', '')).strip().lower()
                    code = row['Code']
                    if is_tmec and category == 'parts':
                        if wizard_queue and code == current_hts and show_tmec_mhdv_card:
                            return duty_tmec_mhdv_result
                        elif code in st.session_state.user_tmec_mhdv_decisions:
                            return st.session_state.user_tmec_mhdv_decisions[code]
                        else:
                            return duty
                    return duty

                hts_mexico['Sec 232 (mhdv)'] = hts_mexico.apply(apply_mhdv_mexico, axis=1)

                def apply_metals_tmec_mexico(row):
                    is_tmec = row.get('is_tmec', False)
                    is_rvc = row.get('is_rvc', False)
                    duty = float(row.get('Sec 232 (Metals)', 0.0))
                    code = row['Code']
                    
                    if is_tmec or is_rvc:
                        if wizard_queue and code == current_hts and show_tmec_metals_card:
                            return duty_tmec_metals_result
                        elif 'user_tmec_metals_decisions' in st.session_state and code in st.session_state.user_tmec_metals_decisions:
                            return st.session_state.user_tmec_metals_decisions[code]
                    return duty

                hts_mexico['Sec 232 (Metals)'] = hts_mexico.apply(apply_metals_tmec_mexico, axis=1)

                def apply_hierarchy_mexico(row):
                    semi = float(row.get('Sec 232 (Semiconductors)', 0.0))
                    auto = float(row.get('Sec 232 (Auto)', 0.0))
                    mhdv = float(row.get('Sec 232 (mhdv)', 0.0))
                    metals = float(row.get('Sec 232 (Metals)', 0.0))
                    wood = float(row.get('Wood_Duty', 0.0))

                    if semi > 0: auto = mhdv = metals = wood = 0.0
                    elif auto > 0: mhdv = metals = wood = 0.0
                    elif mhdv > 0: metals = wood = 0.0
                    elif metals > 0: wood = 0.0

                    row['Sec 232 (Semiconductors)'] = semi
                    row['Sec 232 (Auto)'] = auto
                    row['Sec 232 (mhdv)'] = mhdv
                    row['Sec 232 (Metals)'] = metals
                    row['Wood_Duty'] = wood
                    return row

                hts_mexico = hts_mexico.apply(apply_hierarchy_mexico, axis=1)

                # 1. Aplicamos el formato de Sec 122 PRIMERO
                hts_mexico['Sec 122'] = hts_mexico.apply(format_sec122_duty_row, axis=1)

                def calc_total_row_mexico(row):
                    if row.get('is_complex', False):
                        return row['General']
                        
                    math_base = row['Math Base']
                    try: duty_metals = float(row['Sec 232 (Metals)'])
                    except: duty_metals = 0.0
                    try: duty_autos = float(row['Sec 232 (Auto)'])
                    except: duty_autos = 0.0
                    try: duty_mhdv = float(row.get('Sec 232 (mhdv)', 0.0))
                    except: duty_mhdv = 0.0
                    try: duty_wood = float(row.get('Wood_Duty', 0.0))
                    except: duty_wood = 0.0
                    try: duty_semi = float(row.get('Sec 232 (Semiconductors)', 0.0))
                    except: duty_semi = 0.0
                    
                    # 2. Lógica para aislar el texto de la Sec 122
                    sec122_val = row.get('Sec 122', 10.0)
                    sec122_str_append = ""
                    duty_122 = 0.0
                    
                    if isinstance(sec122_val, str) and "sobre el contenido" in sec122_val:
                        sec122_str_append = f" + {sec122_val}"
                    else:
                        try: duty_122 = float(str(sec122_val).replace('%', ''))
                        except: duty_122 = 10.0
                    
                    sum_pct = math_base + duty_metals + duty_122 + duty_autos + duty_mhdv + duty_wood + duty_semi
                    fixed = row['Fixed']
                    
                    if pd.notna(fixed) and fixed:
                        base_str = f"{fixed} + {sum_pct:.2f}%" if sum_pct > 0 else fixed
                    else:
                        if str(row['General']).lower() == 'free' and sum_pct == 0:
                            base_str = "Free"
                        else:
                            base_str = f"{sum_pct:.2f}%"

                    if sec122_str_append:
                        if base_str in ["Free", "0.00%"]:
                            return sec122_val
                        return f"{base_str}{sec122_str_append}"
                        
                    return base_str

                hts_mexico['Total'] = hts_mexico.apply(calc_total_row_mexico, axis=1)
                
                cols_mexico = ['Code', 'Description']
                format_dict_mexico = {}
                
                if hts_mexico['General'].astype(str).str.strip().ne("").any():
                    cols_mexico.append('General')
                
                cols_mexico.append('Sec 122')

                # Evaluamos dinámicamente qué columnas mostrar en México si su valor final es > 0
                if (hts_mexico['Sec 232 (Metals)'] > 0).any():
                    cols_mexico.append('Sec 232 (Metals)')
                    format_dict_mexico['Sec 232 (Metals)'] = smart_pct
                
                if (hts_mexico['Sec 232 (Auto)'] > 0).any():
                    cols_mexico.append('Sec 232 (Auto)')
                    format_dict_mexico['Sec 232 (Auto)'] = smart_pct

                if (hts_mexico['Sec 232 (mhdv)'] > 0).any():
                    cols_mexico.append('Sec 232 (mhdv)')
                    format_dict_mexico['Sec 232 (mhdv)'] = smart_pct

                hts_mexico['Sec 232 (Wood)'] = hts_mexico['Wood_Duty']
                if (hts_mexico['Sec 232 (Wood)'] > 0).any():
                    cols_mexico.append('Sec 232 (Wood)')
                    format_dict_mexico['Sec 232 (Wood)'] = smart_pct

                if (hts_mexico['Sec 232 (Semiconductors)'] > 0).any():
                    cols_mexico.append('Sec 232 (Semiconductors)')
                    format_dict_mexico['Sec 232 (Semiconductors)'] = smart_pct

                cols_mexico.append('Total')

                def highlight_preferential_row(row):
                    # Usamos row.name para acceder a las columnas ocultas en el DataFrame original
                    is_tmec = hts_mexico.loc[row.name, 'is_tmec']
                    is_rvc = hts_mexico.loc[row.name, 'is_rvc']
                    
                    if pd.notna(is_tmec) and is_tmec:
                        return ['background-color: #dcfce7; color: #166534'] * len(row)
                    elif pd.notna(is_rvc) and is_rvc:
                        return ['background-color: #e0f2fe; color: #0369a1'] * len(row)
                    return [''] * len(row)

                # ---------------------------------------------------------------------
                # 3. RENDERIZADO EN LA INTERFAZ
                # ---------------------------------------------------------------------
                
                st.markdown("<h3 style='color: #0F172A; margin-top: 0px; margin-bottom: 10px; font-size: 1.4rem;'>Aranceles a China <span class='bandera'>🇨🇳</span></h3>", unsafe_allow_html=True)
                
                # Tabla China: Sin highlight TMEC, con wraptext garantizado en 'Description'
                # --- RENDER TABLA CHINA 🇨🇳 ---
                cols_to_center_china = [c for c in cols_china if c not in ['Code', 'Description']]
                # Repartir matemáticamente el 45% restante de la tabla
                width_china_aranceles = f"{45 / len(cols_to_center_china):.1f}%" if cols_to_center_china else "45%"
                
                html_china = (
                    hts_china[cols_china].style
                    .format(format_dict_china)
                    .set_properties(subset=['Code'], **{'width': '15%'})
                    .set_properties(subset=['Description'], **{'width': '40%'})
                    .set_properties(subset=cols_to_center_china, **{'text-align': 'center', 'width': width_china_aranceles})
                    .set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'center !important')]},
                        {'selector': 'th.col_heading.level0.col0', 'props': [('text-align', 'left !important')]},
                        {'selector': 'th.col_heading.level0.col1', 'props': [('text-align', 'left !important')]}
                    ])
                    .set_table_attributes('style="width: 100% !important; min-width: 100%;"')
                    .hide(axis='index')
                    .to_html(classes='tabla-aranceles', escape=False)
                )
                
                st.markdown(f"<div class='card-hover' style='padding: 10px 20px 0px 20px; margin-bottom: 15px; border-top: 4px solid #008889;'>{html_china}</div>", unsafe_allow_html=True)

                # --- RENDER TABLA MÉXICO 🇲🇽 ---
                st.markdown("<h3 style='color: #0F172A; margin-top: 10px; margin-bottom: 5px; font-size: 1.4rem;'>Aranceles a México <span class='bandera'>🇲🇽</span></h3>", unsafe_allow_html=True)
                
                cols_to_center_mexico = [c for c in cols_mexico if c not in ['Code', 'Description']]
                width_mexico_aranceles = f"{45 / len(cols_to_center_mexico):.1f}%" if cols_to_center_mexico else "45%"

                html_mexico = (
                    hts_mexico[cols_mexico].style
                    .apply(highlight_preferential_row, axis=1)
                    .format(format_dict_mexico)
                    .set_properties(subset=['Code'], **{'width': '15%'})
                    .set_properties(subset=['Description'], **{'width': '40%'})
                    .set_properties(subset=cols_to_center_mexico, **{'text-align': 'center', 'width': width_mexico_aranceles})
                    .set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'center !important')]},
                        {'selector': 'th.col_heading.level0.col0', 'props': [('text-align', 'left !important')]},
                        {'selector': 'th.col_heading.level0.col1', 'props': [('text-align', 'left !important')]}
                    ])
                    .set_table_attributes('style="width: 100% !important; min-width: 100%;"')
                    .hide(axis='index')
                    .to_html(classes='tabla-aranceles', escape=False)
                )
                
                st.markdown(f"<div class='card-hover' style='padding: 10px 20px 0px 20px; margin-bottom: 5px; border-top: 4px solid #166534;'>{html_mexico}</div>", unsafe_allow_html=True)

                if hts_mexico['is_tmec'].any():
                    st.markdown("<p style='color: #0F172A; font-size: 0.85rem; margin-top: 0px; font-weight: 500; padding-left: 5px;'>📄 Los registros marcados en verde representan fracciones incluidas en el TMEC.</p>", unsafe_allow_html=True)
                
                if hts_mexico.get('is_rvc', pd.Series(False)).any():
                    st.markdown("<p style='color: #0F172A; font-size: 0.85rem; margin-top: 0px; font-weight: 500; padding-left: 5px;'>📄 Los registros marcados en azul representan fracciones con trato preferencial por Valor de Contenido Regional.</p>", unsafe_allow_html=True)

                # Evaluamos si hay alguna tasa compleja usando .get() para evitar errores si la columna no se creó
                if hts_mexico.get('is_complex', pd.Series(False)).any():
                    st.markdown("<p style='color: #0F172A; font-size: 0.85rem; margin-top: 0px; font-weight: 500; padding-left: 5px;'>⚠️ Para entender las tasas complejas es necesario ingresar al link, revisar la columna \"Special Rate\" y buscar la información para (S+).</p>", unsafe_allow_html=True)

                # --- ANÁLISIS HISTÓRICO ULTRA-RESILIENTE (Diseño NAFIN) ---
                st.markdown("<hr style='border-color: #E2E8F0; margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color: #0F172A; margin-top: 0px;'>Desempeño Histórico: México vs {target_country}</h3>", unsafe_allow_html=True)
                
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
                    <div class='card-hover' style='padding: 10px 20px 10px 20px; margin-bottom: 20px; border-top: 4px solid #2596be;'>
                        <style>
                            table.tabla-nafin {{ border: none !important; width: 100%; border-collapse: collapse; text-align: left; margin-bottom: 0px !important; }}
                            .tabla-nafin th {{ border-bottom: 2px solid #E2E8F0 !important; border-top: none !important; padding: 10px 15px; color: #64748B; font-size: 0.85rem; text-transform: uppercase; font-weight: 700; text-align: left !important; }}
                            .tabla-nafin td {{ border-bottom: 1px solid #E2E8F0 !important; border-top: none !important; padding: 12px 15px; color: #475569; font-size: 0.95rem; vertical-align: middle; }}
                        </style>
                        {html_table}
                    </div>
                    """, unsafe_allow_html=True)

                    # --- CONFIGURACIÓN GLOBAL DE PAÍSES Y SELECTOR PARA GRÁFICAS ---
                    MASTER_COUNTRIES = {
                        'México':  {'col_part': 'participacion_mexico', 'col_ara': 'Mexico',  'color': '#2596be'},
                        'China':   {'col_part': 'participacion_china',  'col_ara': 'China',   'color': '#008889'},
                        'Canadá':  {'col_part': 'participacion_canada', 'col_ara': 'Canada',  'color': '#dc2626'},
                        'Vietnam': {'col_part': 'participacion_vietnam','col_ara': 'Vietnam', 'color': '#d97706'},
                        'Taiwán':  {'col_part': 'participacion_taiwan', 'col_ara': 'Taiwán',  'color': '#7c3aed'}
                    }

                    selected_countries = st.multiselect(
                        "🌍 Seleccione los países a comparar en las gráficas:",
                        options=list(MASTER_COUNTRIES.keys()),
                        default=['México', 'China']
                    )
                    
                    # Hack CSS para forzar la reducción del espacio nativo de Streamlit
                    st.markdown("""
                    <style>
                        /* Ataca directamente el contenedor del multiselect para eliminar su margen base */
                        div[data-testid="stMultiSelect"] {
                            margin-bottom: -30px !important;
                        }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    col_chart1, col_chart2 = st.columns(2)
                    
                    def prepare_multi_chart_data(df, config_dict):
                        df_temp = df.copy()
                        df_temp['Date'] = pd.to_datetime(df_temp['Date'])
                        df_temp = df_temp.set_index('Date')
                        
                        if not df_temp.empty:
                            df_temp = df_temp.resample('MS').asfreq()
                            
                        data = pd.DataFrame(index=df_temp.index)
                        colors = []
                        
                        for col, (label, color) in config_dict.items():
                            if col in df_temp.columns and df_temp[col].notna().any():
                                data[label] = df_temp[col]
                                colors.append(color)
                                
                        return data, colors

                    def plot_altair_chart(chart_data, palette, y_title):
                        df_melted = chart_data.reset_index().melt('Date', var_name='País', value_name='Valor')
                        
                        chart = alt.Chart(df_melted).mark_line(
                            strokeWidth=3,
                            interpolate='linear'
                        ).encode(
                            x=alt.X('Date:T', title='', axis=alt.Axis(grid=False, labelColor='#64748B')),
                            y=alt.Y('Valor:Q', title=y_title, axis=alt.Axis(gridColor='#F1F5F9', labelColor='#94A3B8')),
                            
                            # AQUÍ ESTÁ EL CAMBIO: Se agregó offset=-10 para subir la leyenda
                            color=alt.Color(
                                'País:N', 
                                scale=alt.Scale(domain=chart_data.columns.tolist(), range=palette), 
                                legend=alt.Legend(title=None, orient="bottom", offset=-5) 
                            ),
                            
                            tooltip=[alt.Tooltip('Date:T', title='Fecha', format='%Y-%m'), alt.Tooltip('País:N'), alt.Tooltip('Valor:Q', format='.2f')]
                        ).properties(
                            height=350
                        ).configure_view(
                            strokeWidth=0
                        )
                        
                        st.altair_chart(chart, use_container_width=True)

                    st.markdown("""
                    <style>
                        /* Estilos genéricos para tarjetas de gráficas */
                        div:has(> div.element-container > div > div > div.chart-card) {
                            background-color: #ffffff;
                            border: 1px solid #E2E8F0;
                            border-top: 4px solid #0F172A !important;
                            padding: 24px;
                            border-radius: 12px;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
                            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
                        }
                        div:has(> div.element-container > div > div > div.chart-card):hover {
                            transform: translateY(-2px) !important;
                            box-shadow: 0 10px 25px rgba(0,0,0,0.06) !important;
                        }
                        
                        /* REPOSICIONAR EL MENÚ DE DESCARGA DE ALTAIR */
                        .vega-embed details {
                            position: absolute !important;
                            top: -32px !important;  /* Saca el botón hacia arriba, fuera de la gráfica */
                            right: 60px !important; /* Lo recorre a la izquierda para no encimarse con los botones nativos de Streamlit */
                            z-index: 1000 !important;
                        }
                        
                        /* Asegurar que el menú desplegable (PNG/SVG) se abra correctamente hacia abajo */
                        .vega-embed details .vega-actions {
                            top: 25px !important;
                            right: 0px !important;
                            left: auto !important;
                            background-color: #ffffff !important;
                            border: 1px solid #E2E8F0 !important;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
                        }
                    </style>
                    """, unsafe_allow_html=True)

                    with col_chart1:
                        with st.container():
                            st.markdown("<div class='chart-card'></div>", unsafe_allow_html=True)
                            st.markdown("<div style='color: #0F172A; font-weight: 800; font-size: 1.1rem; margin-bottom: 15px;'>Participación de Mercado (%)</div>", unsafe_allow_html=True)
                            
                            if rows_part and selected_countries:
                                # Filtramos dinámicamente el diccionario usando los países seleccionados
                                config_part = {MASTER_COUNTRIES[p]['col_part']: (p, MASTER_COUNTRIES[p]['color']) for p in selected_countries}
                                
                                chart_data, palette = prepare_multi_chart_data(df_part_sub, config_part)
                                if not chart_data.dropna(how='all').empty:
                                    plot_altair_chart(chart_data, palette, '% Participación')
                                else:
                                    st.info("Datos no disponibles para los países seleccionados.")
                            elif not selected_countries:
                                st.warning("Seleccione al menos un país arriba.")
                            else:
                                st.info("Sin datos de participación.")

                    with col_chart2:
                        with st.container():
                            st.markdown("<div class='chart-card'></div>", unsafe_allow_html=True)
                            st.markdown("<div style='color: #0F172A; font-weight: 800; font-size: 1.1rem; margin-bottom: 15px;'>Arancel Efectivo (%)</div>", unsafe_allow_html=True)
                            
                            if rows_ara and selected_countries:
                                # Filtramos dinámicamente el diccionario usando los países seleccionados
                                config_ara = {MASTER_COUNTRIES[p]['col_ara']: (p, MASTER_COUNTRIES[p]['color']) for p in selected_countries}
                                
                                chart_data, palette = prepare_multi_chart_data(df_aranceles_sub, config_ara)
                                if not chart_data.dropna(how='all').empty:
                                    plot_altair_chart(chart_data, palette, '% Arancel')
                                else:
                                    st.info("Datos no disponibles para los países seleccionados.")
                            elif not selected_countries:
                                st.warning("Seleccione al menos un país arriba.")
                            else:
                                st.info("Sin datos de aranceles.")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                else:
                    st.info(f"No hay registros históricos para la subpartida {hs6_input}.")

            else:
                st.warning(f"No se encontró información en HTS para {hs6_input}")

else:
    st.info("👈 Ingresa una subpartida para comenzar.")