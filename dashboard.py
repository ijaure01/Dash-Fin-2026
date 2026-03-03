import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. KONFIGURAZIOA ETA ESTILO ELITE ---
st.set_page_config(layout="wide", page_title="Finantza Dashboard Elite")

st.markdown("""
    <style>
        /* 1. OROKORRA: Goiko tarte zuria eta marjinak kentzeko */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }
        header {visibility: hidden;}
        
        /* Orrialdeko fondo ilun dotorea */
        .stApp {
            background-color: #262C38 !important;
            color: #FFFFFF !important;
        }
        
        /* 2. SIDEBAR: Beltzagoa eta iragazki pertsonalizatuak */
        [data-testid="stSidebar"] {
            background-color: #313B45 !important;
        }
                
        /* Iragazkien gaineko testua (Labels) zuriz */
        [data-testid="stWidgetLabel"] p { 
                color: #FFFFFF !important; 
                font-weight: bold !important; 
        }

        /* Selectbox eta Multiselect koadro nagusia */
        div[data-baseweb="select"] > div {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #4d5866 !important;
        }

        /* Multiselect-eko etiketa hautatuak (pills) */
        span[data-baseweb="tag"] {
            background-color: #1b2129 !important; /* Beltz-grisaxka pixka bat bereizteko */
            border: 1px solid #4d5866 !important;
        }

        /* Testu guztiak zuriz iragazkietan */
        span[data-baseweb="tag"] span, div[data-baseweb="select"] div {
            color: #FFFFFF !important;
        }

        /* Zerrenda zabaldua (Dropdown) */
        div[data-baseweb="popover"] ul {
            background-color: #000000 !important;
        }
        div[data-baseweb="popover"] li {
            color: #FFFFFF !important;
        }
                
        div[data-baseweb="popover"] li:hover {
            background-color: #313B45 !important;
        }

        /* 3. METRIKA KOADROAK (KPIs): Fondo argiagoa eta testu itzala */
        div[data-testid="stMetric"] {
            background-color: #7A8D9C !important;
            padding: 25px !important;
            border-radius: 12px !important;
            border: 1px solid #4d5866 !important;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        }

        [data-testid="stMetricValue"] {
            color: #c9a050 !important;
            font-size: 48px !important;
            text-shadow: 1px 1px 2px black;
        }
        
        [data-testid="stMetricLabel"] {
            color: #ffffff !important;
            font-weight: bold !important;
            letter-spacing: 1px;
        }

        /* 4. TAULA ESTILOA: Beltza eta testu zuria */
        .stDataFrame {
            border: 1px solid #3d4654 !important;
            border-radius: 8px !important;
            background-color: #0b0e14 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PLOTLY ESTILOA (URREA ETA MUTED COLOURS) ---
PALETA_ELITE = ["#3d5a80", "#c9a050", "#98c1d9", "#566d7e", "#293241"]

def style_fig_elite(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white", size=12),
        legend = dict (
            title = None,
            font = dict(color = "#FFFFFF", size = 14)
        ),
        margin=dict(t=30, b=10, l=10, r=10),
        colorway=PALETA_ELITE
    )
    # X ARDATZA (Datak, Kategoriak...)
    fig.update_xaxes(
        title = None,
        tickfont=dict(color="#FFFFFF", size=11), # Zenbaki/Testu guztiak zuriz
        #titlefont=dict(color="#FFFFFF"),
        gridcolor='#3d4654', 
        zeroline=False,
        showgrid=True
    )
    
    # Y ARDATZA (Diru kopuruak...)
    fig.update_yaxes(
        title = None,
        tickfont=dict(color="#FFFFFF", size=11), # Zenbaki guztiak zuriz
        #titlefont=dict(color="#FFFFFF"),
        gridcolor='#3d4654', 
        zeroline=False,
        showgrid=True
    )
    return fig


# --- 2. HIZKUNTZA ETA HIZTEGIA ---
hiztegiak = {
    "Euskara": {
        "titulua": "FINANTZA ANALISIA", "guztira": "GASTUA GUZTIRA", "batezbestekoa": "EGUNEKO BATEZ BESTEKOA", 
        "garestiena": "KATEGORIA GARESTIENA", "top5": "TOP 5 GASTUAK KATEGORIAZ", "bilakaera": "Gastuen Bilakaera",
        "banaketa": "Gastuen Banaketa", "aukeratu_kat": "Aukeratu kategoria:", "xehetasuna": "Xehetasuna",
        "urla_label": "Sartu Google Sheets URLa (Hutsik hirea ikusteko):", "errore_urla": "Ezin izan dira datuak kargatu. Begiratu URLa."
    },
    "Español": {
        "titulua": "ANÁLISIS FINANCIERO", "guztira": "GASTO TOTAL", "batezbestekoa": "PROMEDIO DIARIO", 
        "garestiena": "CATEGORÍA MÁS CARA", "top5": "TOP 5 GASTOS POR CATEGORÍA", "bilakaera": "Evolución de Gastos",
        "banaketa": "Distribución de Gastos", "aukeratu_kat": "Selecciona categoría:", "xehetasuna": "Detalle",
        "urla_label": "Introduce URL de Google Sheets (Vacio para ver el mio):", "errore_urla": "No se han podido cargar los datos. Revisa la URL."
    },
    "English": {
        "titulua": "FINANCIAL ANALYSIS", "guztira": "TOTAL EXPENSE", "batezbestekoa": "DAILY AVERAGE", 
        "garestiena": "MOST EXPENSIVE CATEGORY", "top5": "TOP 5 EXPENSES BY CATEGORY", "bilakaera": "Expense Evolution",
        "banaketa": "Expense Distribution", "aukeratu_kat": "Select category:", "xehetasuna": "Details",
        "urla_label": "Enter Google Sheets URL (Empty for default):", "errore_urla": "Could not load data. Check the URL."
    }
}

lang = st.sidebar.selectbox("Language / Hizkuntza", ["Euskara", "Español", "English"])
t = hiztegiak[lang]

# --- 3. DATUAK KARGATZEKO LOGIKA (DINAMIKOA ETA MALGUA) ---
NIRE_SHEET_ID = '183PzIo747C4MHQcE0homP49avMonmuXytIvECZ7qrYM'

url_input = st.sidebar.text_input(t['urla_label'], placeholder="https://docs.google.com/...")

def get_url(input_val):
    if input_val and "/d/" in input_val:
        sid = input_val.split("/d/")[1].split("/")[0]
        return f'https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv'
    return f'https://docs.google.com/spreadsheets/d/{NIRE_SHEET_ID}/gviz/tq?tqx=out:csv'

@st.cache_data(ttl=300)
def load_data(url_to_load):
    try:
        raw_df = pd.read_csv(url_to_load)
        # ZUTABEAK BERRIZENDATU ORDENAREN ARABERA (Malgutasuna lagunarentzat)
        # Ordena: 0=Data, 1=Kategoria, 2=Deskribapena, 3=Kopurua
        new_cols = ['Data', 'Kategoria', 'Deskribapena', 'Kopurua']
        raw_df.columns = new_cols + list(raw_df.columns[len(new_cols):])
        
        raw_df['Data'] = pd.to_datetime(raw_df['Data'], dayfirst=True, errors='coerce')
        if raw_df['Kopurua'].dtype == object:
            raw_df['Kopurua'] = raw_df['Kopurua'].str.replace('$', '').str.replace(',', '.').str.strip()
        raw_df['Kopurua'] = pd.to_numeric(raw_df['Kopurua'], errors='coerce').fillna(0)
        return raw_df.dropna(subset=['Data'])
    except:
        return None

final_url = get_url(url_input)
df = load_data(final_url)

if df is not None:
    # --- 4. SIDEBAR ETA FILTROAK ---
    urteak = sorted(df['Data'].dt.year.unique(), reverse=True)
    urte_aukera = st.sidebar.selectbox("Year", urteak)
    
    # Hilabeteak hizkuntza orokorrean (zenbakiz barnean, izenez kanpoan)
    df['Month_Name'] = df['Data'].dt.month_name()
    hilabete_guztiak = df[df['Data'].dt.year == urte_aukera]['Month_Name'].unique().tolist()
    hila_aukerak = st.sidebar.multiselect("Months", options=hilabete_guztiak, default=hilabete_guztiak)

    df_filtratua = df[(df['Data'].dt.year == urte_aukera) & (df['Month_Name'].isin(hila_aukerak))]

    # --- 5. GRAFIKOAK (LEHENGO ESTILOA) ---
    def style_fig_elite(fig):
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color="white"), margin=dict(t=30, b=10, l=10, r=10))
        fig.update_xaxes(showgrid=True, gridcolor='#3d4654', title=None)
        fig.update_yaxes(showgrid=True, gridcolor='#3d4654', title=None)
        return fig

    st.title(f"{t['titulua']}: {urte_aukera}")
    
    # KPI-ak
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(t['guztira'], f"$ {df_filtratua['Kopurua'].sum():,.2f}")
    with c2:
        egun_kop = len(df_filtratua['Data'].dt.date.unique()) if not df_filtratua.empty else 1
        st.metric(t['batezbestekoa'], f"$ {(df_filtratua['Kopurua'].sum()/egun_kop):,.2f}")
    with c3:
        if not df_filtratua.empty:
            garestiena = df_filtratua.groupby('Kategoria')['Kopurua'].sum().idxmax()
            st.metric(t['garestiena'], garestiena)

    # Grafiko nagusiak
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader(t['banaketa'])
        fig_pie = px.pie(df_filtratua, values='Kopurua', names='Kategoria', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textinfo='none')
        st.plotly_chart(style_fig_elite(fig_pie), use_container_width=True)

    with col_right:
        st.subheader(t['bilakaera'])
        df_daily = df_filtratua.groupby('Data')['Kopurua'].sum().reset_index()
        fig_line = px.line(df_daily, x='Data', y='Kopurua', markers=True)
        fig_line.update_traces(line_color='#c9a050', fill='tozeroy', fillcolor='rgba(201, 160, 80, 0.1)')
        st.plotly_chart(style_fig_elite(fig_line), use_container_width=True)

    # Top 5 atala
    st.markdown(f"### {t['top5']}")
    if not df_filtratua.empty:
        kategoriak = df_filtratua['Kategoria'].unique()
        kat_aukera = st.selectbox(t['aukeratu_kat'], kategoriak)
        top5 = df_filtratua[df_filtratua['Kategoria'] == kat_aukera].nlargest(5, 'Kopurua')

        col_table, col_bar = st.columns([1, 1]) # Taula 1, Grafika 2
        with col_table:
            st.write(f"**{t['xehetasuna']}**")
            # Taula estilo ilunarekin erakutsi
            st.dataframe(top5[['Data', 'Deskribapena', 'Kopurua']].style.set_properties(**{'background-color': "#1b2129", 'color': 'white'}), use_container_width=True, hide_index=True)
            
        with col_bar:
            # Grafika kolore urdin/gris dotoreekin
            fig_top = px.bar(top5, x='Kopurua', y='Deskribapena', orientation='h')
            fig_top.update_traces(
                marker_color='#738496',
                width = 0.5,
                texttemplate='%{text:.1s} $',
                textposition='outside',
                textfont=dict(color="white")
            ) # Urdin pro hori
            st.plotly_chart(style_fig_elite(fig_top), use_container_width=True)
else:
    st.error(t['errore_urla'])