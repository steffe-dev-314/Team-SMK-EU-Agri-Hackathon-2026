import streamlit as st

st.set_page_config(
    page_title="DBE App",
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