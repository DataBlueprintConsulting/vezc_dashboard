# import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import itertools
from io import BytesIO
import locale

# === LOCALE CONFIGURATION ===
try:
    locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
except locale.Error:
    st.warning("Dutch locale niet beschikbaar. Getallen worden in standaardformaat weergegeven.")

def format_number(number):
    """Format number with Dutch locale and 1 decimal"""
    try:
        return locale.format_string('%.1f', number, grouping=True)
    except:
        # Fallback if locale not available
        return f"{round(number, 1):,.1f}".replace('.', ',').replace(',', '.', 1)

# === PAGE CONFIG ===
st.set_page_config(layout="wide", page_title="VEZC Urenadministratie", page_icon="✈️")

# === COLOR PALETTE ===
colors = [
    '#005C9F', '#9F7400', '#2FAAD4', '#D4742F',
    '#0E73BB', '#BB4C0E', '#FFA07A', '#7A87FF',
    '#98FB98', '#9862FB', '#FFD700', '#007AFF',
    '#FF6347', '#477AFF', '#87CEEB', '#EB87CE'
]

# === FUNCTIONS ===
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

# === FIELD COORDINATES ===
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
}

# === HEADER ===
st.title("✈️ Venlo Eindhoven ZweefvliegClub Vluchtadministratie")
st.markdown(
    """
    <style>
        .responsive-image {
            max-width: 500px;
            width: 100%;
            height: auto;
        }
    </style>
    <div style="text-align: center;">
        <img class="responsive-image" src="https://raw.githubusercontent.com/DataBlueprintConsulting/vezc_dashboard/main/vezc.jpg" alt="VEZC logo">
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("ℹ️ Wat doet deze tool precies?"):
    st.write("""
        Ontdek hier een handige tool om je vluchtenregistratie overzichtelijk bij te houden. 
        Je kunt snel het totaal aantal vlieguren en starts per vliegtuigtype inzien en filteren op veld, type, datum en meer.
        Upload een Excel uit Startadministratie en bekijk direct visuele inzichten.
    """)

# === FILE UPLOAD ===
uploaded_file = st.file_uploader("📁 Upload hier je Startadministratie in Excel-formaat", type=['xlsx'])

if uploaded_file:
    df = load_data(uploaded_file)
    expected_columns = {'Datum', 'Veld', 'Type', 'Registratie', 'Startmethode', 'Vluchtduur'}
    if missing := expected_columns - set(df.columns):
        st.error(f"❌ Ontbrekende kolommen: {', '.join(missing)}")
        st.stop()
else:
    st.warning("📄 Upload een bestand om te starten.")
    st.stop()

# === SIDEBAR FILTERS ===
st.sidebar.title("📊 Filters")
selected_veld = st.sidebar.multiselect("Veld", df['Veld'].dropna().unique())
selected_type = st.sidebar.multiselect("Type", df['Type'].dropna().unique())
selected_registratie = st.sidebar.multiselect("Registratie", df['Registratie'].dropna().unique())
selected_startmethode = st.sidebar.multiselect("Startmethode", df['Startmethode'].dropna().unique())
selected_start_date = st.sidebar.date_input("Startdatum (van)", None)
selected_end_date = st.sidebar.date_input("Einddatum (t/m)", None)

# === DATA FILTERING ===
filtered_df = filter_dataframe(df, selected_veld, selected_type, selected_registratie, selected_startmethode, selected_start_date, selected_end_date)
st.info(f"🔎 {len(filtered_df)} vluchten gevonden.")

# === DOWNLOAD BUTTON ===
st.download_button(
    label="⬇️ Download gefilterde data als Excel",
    data=to_excel_download(filtered_df),
    file_name="vezc_uren_filtered.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")

# === VISUALIZATIONS ===
col1, col2, col3 = st.columns(3)

if not filtered_df.empty:
    # Data calculations
    starts_per_type = filtered_df['Type'].value_counts()
    hours_per_type = filtered_df.groupby('Type')['Vluchtduur'].sum().sort_values(ascending=False)
    
    # === COLUMN 1: DATA TABLES ===
    with col1:
        # Starts table
        st.subheader("🛫 Starts")
        starts_df = pd.DataFrame({
            'Type': starts_per_type.index,
            'Aantal starts': [format_number(x) for x in starts_per_type.values]
        })
        st.dataframe(starts_df, width=600, hide_index=True)
        st.markdown(f"**Totaal starts**: {format_number(starts_per_type.sum())} starts")
        
        # Hours table
        st.subheader("🕒 Vlieguren")
        hours_df = pd.DataFrame({
            'Type': hours_per_type.index,
            'Vlieguren': [format_number(x) for x in hours_per_type.values]
        })
        st.dataframe(hours_df, width=600, hide_index=True)
        st.markdown(f"**Totaal uren**: {format_number(hours_per_type.sum())} uur")

    # === COLUMN 2: BAR CHARTS ===
    with col2:
        # Starts bar chart
        fig1 = go.Figure(go.Bar(
            x=starts_per_type.index,
            y=starts_per_type.values,
            marker_color=[colors[i % len(colors)] for i in range(len(starts_per_type))],
            text=[format_number(x) for x in starts_per_type.values],
            textposition='auto'
        ))
        fig1.update_layout(
            title="Aantal starts per vliegtuigtype",
            xaxis_title="Type",
            yaxis_title="Aantal",
            hovermode="x unified",
            locale='nl-NL'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Hours bar chart
        fig2 = go.Figure(go.Bar(
            x=hours_per_type.index,
            y=hours_per_type.values,
            marker_color=[colors[i % len(colors)] for i in range(len(hours_per_type))],
            text=[format_number(x) for x in hours_per_type.values],
            textposition='auto'
        ))
        fig2.update_layout(
            title="Aantal vlieguren per vliegtuigtype",
            xaxis_title="Type",
            yaxis_title="Uren",
            hovermode="x unified",
            locale='nl-NL'
        )
        st.plotly_chart(fig2, use_container_width=True)

    # === COLUMN 3: PIE CHARTS ===
    with col3:
        # Starts pie chart
        fig3 = go.Figure(go.Pie(
            labels=starts_per_type.index,
            values=starts_per_type.values,
            marker_colors=[colors[i % len(colors)] for i in range(len(starts_per_type))],
            textinfo='percent+label',
            hovertemplate="%{label}: %{value} starts (%{percent})"
        ))
        fig3.update_layout(title="Verdeling starts")
        st.plotly_chart(fig3, use_container_width=True)
        
        # Hours pie chart
        fig4 = go.Figure(go.Pie(
            labels=hours_per_type.index,
            values=hours_per_type.values,
            marker_colors=[colors[i % len(colors)] for i in range(len(hours_per_type))],
            textinfo='percent+label',
            hovertemplate="%{label}: %{value} uur (%{percent})"
        ))
        fig4.update_layout(title="Verdeling vlieguren")
        st.plotly_chart(fig4, use_container_width=True)

    # === LAST FLIGHTS ===
    st.markdown("---")
    st.subheader("🛬 Laatste vluchten per vliegtuigtype")
    
    last_flights = filtered_df.groupby('Type')['Datum'].max().reset_index()
    last_flights['Laatste vlucht'] = last_flights['Datum'].dt.strftime('%d-%m-%Y')
    last_flights['Dagen geleden'] = (pd.Timestamp.now().normalize() - last_flights['Datum']).dt.days
    last_flights['Dagen geleden'] = last_flights['Dagen geleden'].apply(format_number)
    
    st.dataframe(last_flights[['Type', 'Laatste vlucht', 'Dagen geleden']].sort_values("Dagen geleden"), hide_index=True)

    # Days since last flight chart
    fig5 = go.Figure(go.Bar(
        x=last_flights['Type'],
        y=last_flights['Dagen geleden'].astype(float),
        marker_color=colors[0],
        text=[format_number(x) for x in last_flights['Dagen geleden'].astype(float)],
        textposition='auto'
    ))
    fig5.update_layout(
        title="Dagen geleden sinds laatste vlucht per type",
        xaxis_title="Type",
        yaxis_title="Dagen geleden",
        locale='nl-NL'
    )
    st.plotly_chart(fig5, use_container_width=True)

    # === MAP ===
    st.markdown("---")
    st.subheader("🗺️ Kaart: Starts per veld")
    
    veld_counts = filtered_df['Veld'].value_counts().reset_index()
    veld_counts.columns = ['Veld', 'Aantal starts']
    veld_counts['Latitude'] = veld_counts['Veld'].map(lambda x: veld_coords.get(x, (np.nan, np.nan))[0])
    veld_counts['Longitude'] = veld_counts['Veld'].map(lambda x: veld_coords.get(x, (np.nan, np.nan))[1])
    veld_counts = veld_counts.dropna(subset=['Latitude', 'Longitude'])
    
    st.map(veld_counts.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}))

    # === FULL DATA ===
    with st.expander("📋 Bekijk volledige gefilterde data"):
        st.dataframe(filtered_df, hide_index=True)

else:
    st.warning("⚠️ Geen resultaten met deze filters. Pas je selectie aan.")
