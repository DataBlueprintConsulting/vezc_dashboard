import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import itertools
from io import BytesIO

# === PAGINA CONFIG ===
st.set_page_config(layout="wide", page_title="VEZC Urenadministratie", page_icon="✈️")

# === KLEURENPALET ===
colors = [
    '#005C9F', '#9F7400', '#2FAAD4', '#D4742F',
    '#0E73BB', '#BB4C0E', '#FFA07A', '#7A87FF',
    '#98FB98', '#9862FB', '#FFD700', '#007AFF',
    '#FF6347', '#477AFF', '#87CEEB', '#EB87CE'
]

# === FUNCTIES ===
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce', dayfirst=True)
    df['Vluchtduur'] = pd.to_timedelta(df['Vluchtduur'], errors='coerce').dt.total_seconds() / 3600
    return df

def filter_dataframe(df, veld, type_, registratie, startmethode, start, end):
    mask = pd.Series([True] * len(df))
    if veld: mask &= df['Veld'].isin(veld)
    if type_: mask &= df['Type'].isin(type_)
    if registratie: mask &= df['Registratie'].isin(registratie)
    if startmethode: mask &= df['Startmethode'].isin(startmethode)
    if start: mask &= df['Datum'] >= pd.to_datetime(start)
    if end: mask &= df['Datum'] <= pd.to_datetime(end)
    return df[mask]

def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# === COORDINATEN PER VELD ===
veld_coords = {
    'Venlo': (51.387, 6.156),
    'Eindhoven': (51.450, 5.374),
    'Malden': (51.778, 5.857),
    'Terlet': (52.051, 5.936),
    'Gilze': (51.567, 4.930),
    'Soesterberg': (52.123, 5.276),
    'Weert': (51.253, 5.705),
    'Schmallenberg': (51.1526, 8.2908),
    'Kamp Linfort': (51.4958, 6.5321),
    'Dahlemer-Binz (DE)': (50.40454, 6.52994),
    'LeBlanc (F)': (46.630, 1.060),
    'Sinsheim': (49.2489, 8.8885),
    'Terlet': (52.0603, 5.9386),
    'Stadlohn': (51.9921, 6.9138),
    'Stendal': (52.6041, 11.8518)
    # Voeg meer velden toe indien gewenst
}

# === HEADER ===
st.title("✈️ Venlo Eindhoven ZweefvliegClub Vluchtadministratie")
st.image("vezc.jpg", use_column_width=True)

with st.expander("ℹ️ Wat doet deze tool precies?"):
    st.write("""
        Ontdek hier een handige tool om je vluchtenregistratie overzichtelijk bij te houden. 
        Je kunt snel het totaal aantal vlieguren en starts per vliegtuigtype inzien en filteren op veld, type, datum en meer.
        Upload een Excel uit Startadministratie en bekijk direct visuele inzichten.
    """)

# === UPLOADEN ===
uploaded_file = st.file_uploader("📁 Upload hier je Startadministratie in Excel-formaat", type=['xlsx'])

if uploaded_file:
    df = load_data(uploaded_file)

    # VALIDATIE
    expected_columns = {'Datum', 'Veld', 'Type', 'Registratie', 'Startmethode', 'Vluchtduur'}
    missing = expected_columns - set(df.columns)
    if missing:
        st.error(f"❌ Ontbrekende kolommen: {', '.join(missing)}")
        st.stop()
else:
    st.warning("📄 Upload een bestand om te starten.")
    st.stop()

# === SIDEBAR ===
st.sidebar.title("📊 Filters")
selected_veld = st.sidebar.multiselect("Veld", df['Veld'].dropna().unique())
selected_type = st.sidebar.multiselect("Type", df['Type'].dropna().unique())
selected_registratie = st.sidebar.multiselect("Registratie", df['Registratie'].dropna().unique())
selected_startmethode = st.sidebar.multiselect("Startmethode", df['Startmethode'].dropna().unique())
selected_start_date = st.sidebar.date_input("Startdatum (van)", None)
selected_end_date = st.sidebar.date_input("Einddatum (t/m)", None)

# === FILTEREN ===
filtered_df = filter_dataframe(df, selected_veld, selected_type, selected_registratie, selected_startmethode, selected_start_date, selected_end_date)

st.info(f"🔎 {len(filtered_df)} vluchten gevonden.")

# === DOWNLOAD KNOP ===
st.download_button(
    label="⬇️ Download gefilterde data als Excel",
    data=to_excel_download(filtered_df),
    file_name="vezc_uren_filtered.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")

# === VISUALISATIES ===
col1, col2, col3 = st.columns(3)

if not filtered_df.empty:
    starts_per_type = filtered_df['Type'].value_counts()
    # hours_per_type = filtered_df.groupby('Type')['Vluchtduur'].sum()
    hours_per_type = filtered_df.groupby('Type')['Vluchtduur'].sum().sort_values(ascending=False)

    # === COL1: TABEL DATA ===
    with col1:
        st.subheader("🛫 Starts")
        st.dataframe(starts_per_type.rename("Aantal starts").reset_index().rename(columns={'index': 'Type'}), width=600, hide_index=True)
        st.markdown(f"**Totaal starts**: {int(starts_per_type.sum())} starts")
    with col1:
        st.subheader("🕒 Vlieguren")
        st.dataframe(hours_per_type.rename("Vlieguren").reset_index(), width=600, hide_index=True)
        st.markdown(f"**Totaal uren**: {round(hours_per_type.sum(), 2)} uur")

    # === COL2: BAR CHARTS ===
    with col2:
        fig1 = go.Figure([go.Bar(x=starts_per_type.index, y=starts_per_type.values,
                                 marker_color=[colors[i % len(colors)] for i in range(len(starts_per_type))])])
        fig1.update_layout(title="Aantal starts per vliegtuigtype", xaxis_title="Type", yaxis_title="Aantal")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = go.Figure([go.Bar(x=hours_per_type.index, y=hours_per_type.values,
                                 marker_color=[colors[i % len(colors)] for i in range(len(hours_per_type))])])
        fig2.update_layout(title="Aantal vlieguren per vliegtuigtype", xaxis_title="Type", yaxis_title="Uren")
        st.plotly_chart(fig2, use_container_width=True)

    # === COL3: PIE CHARTS ===
    with col3:
        fig3 = go.Figure(data=[go.Pie(labels=starts_per_type.index, values=starts_per_type.values,
                                      marker_colors=[colors[i % len(colors)] for i in range(len(starts_per_type))],
                                      textinfo='percent+label')])
        fig3.update_layout(title="Verdeling starts")
        st.plotly_chart(fig3, use_container_width=True)

        if not hours_per_type.empty:
            fig4 = go.Figure(data=[go.Pie(labels=hours_per_type.index, values=hours_per_type.values,
                                          marker_colors=[colors[i % len(colors)] for i in range(len(hours_per_type))],
                                          textinfo='percent+label')])
            fig4.update_layout(title="Verdeling vlieguren")
            st.plotly_chart(fig4, use_container_width=True)

    # === LAATSTE VLUCHTEN ===
    st.markdown("---")
    st.subheader("🛬 Laatste vluchten per vliegtuigtype")

    df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce')
    today = pd.Timestamp.now().normalize()
    last_flights = df.groupby('Type')['Datum'].max().reset_index()
    last_flights['Laatste vlucht'] = last_flights['Datum'].dt.strftime('%d-%m-%Y')
    last_flights['Dagen geleden'] = (today - last_flights['Datum']).dt.days
    st.dataframe(last_flights[['Type', 'Laatste vlucht', 'Dagen geleden']].sort_values("Dagen geleden"), hide_index=True)

    fig5 = go.Figure([go.Bar(x=last_flights['Type'], y=last_flights['Dagen geleden'],
                             marker_color=colors[0])])
    fig5.update_layout(title="Dagen geleden sinds laatste vlucht per type", xaxis_title="Type", yaxis_title="Dagen geleden")
    st.plotly_chart(fig5, use_container_width=True)

    # === KAART ===
    st.markdown("---")
    st.subheader("🗺️ Kaart: Starts per veld")

    veld_counts = filtered_df['Veld'].value_counts().reset_index()
    veld_counts.columns = ['Veld', 'Aantal starts']
    veld_counts['Latitude'] = veld_counts['Veld'].map(lambda x: veld_coords.get(x, (np.nan, np.nan))[0])
    veld_counts['Longitude'] = veld_counts['Veld'].map(lambda x: veld_coords.get(x, (np.nan, np.nan))[1])
    veld_counts = veld_counts.dropna(subset=['Latitude', 'Longitude'])

    st.map(veld_counts.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}))

    # === GEHELE DATA ===
    with st.expander("📋 Bekijk volledige gefilterde data"):
        st.dataframe(filtered_df, hide_index=True)

else:
    st.warning("⚠️ Geen resultaten met deze filters. Pas je selectie aan.")
