import streamlit as st



st.logo('.streamlit/logo.png' , size = 'large')

st.set_page_config(
    page_title="DBE - Startseite",
    page_icon="🌱",
    layout="wide",
)

st.title("Düngebedarfsermittlung")
st.write("Willkommen zur digitalen DBE-Anwendung.")

st.info(
    "Wähle eine Seite in der Navigation links, "
    "um die Angaben zum Schlag, die Düngebedarfsermittlung "
    "oder die Düngedokumentation zu bearbeiten."
)