import streamlit as st

st.set_page_config(
    page_title="SMK - Home",
    page_icon="🌱",
    layout="wide",
)

st.logo(".streamlit/logo.png", size="large")

st.title("SMK - Home")
st.write("Welcome to SMK's farmer-friendly dashboard!")

st.info(
    "Select a page from the navigation menu on the left "
    "to manage field information, the fertilizer requirement assessment, "
    "or fertilizer application records."
)
