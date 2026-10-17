import streamlit as st



st.logo('.streamlit/logo.png' , size = 'large')

st.set_page_config(
    page_title="SMK - Startseite",
    page_icon="🌱",
    layout="wide",
)

st.title("SMK - Startseite")
st.write("Willkommen zum Farmer-friendly dashboard von SMK!.")

st.info(
    "Wähle eine Seite in der Navigation links, "
    "um die Angaben zum Schlag, die Düngebedarfsermittlung "
    "oder die Düngedokumentation zu bearbeiten."
)