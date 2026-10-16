
import streamlit as st
import pandas as pd 
from CROPS import zwischenfruechte , kulturen

st.set_page_config(page_title="DBE – Allgemeine Angaben", layout="wide")

# --------------------------------------------------
# SESSION STATE INITIALISATION
# --------------------------------------------------

def init_st():

    if "schlag_collection" not in st.session_state:
        st.session_state.schlag_collection = {}

    if "schlag_ids" not in st.session_state:
        st.session_state.schlag_ids = {}

    if "reset_schlag_data" not in st.session_state:
        st.session_state.reset_schlag_data = False

    if "reset_full" not in st.session_state:
        st.session_state.reset_full = False

init_st()

# --------------------------------------------------
# RESET HANDLING
# --------------------------------------------------

if st.session_state.reset_full:

    st.session_state.schlag_collection = {}
    st.session_state.schlag_ids = {}

    st.session_state.schlag_in = ""
    st.session_state.feldblock_nr_in = None
    st.session_state.schlag_gr_in = None
    st.session_state.vj_kultur = ""
    st.session_state.zwischenfrucht = ""

    st.session_state.reset_full = False

if st.session_state.reset_schlag_data:

    st.session_state.schlag_in = ""
    st.session_state.feldblock_nr_in = None
    st.session_state.schlag_gr_in = None
    st.session_state.vj_kultur = ""
    st.session_state.zwischenfrucht = ""

    st.session_state.reset_schlag_data = False


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    if st.button("RESET", type="secondary"):
        st.session_state.reset_full = True
        st.rerun()

    st.caption("ADMIN")


tab1 , tab2 , tab3 = st.tabs(['Allgemeine Angaben' , 'DBE - Stickstoff' , 'Dokumentation Stickstoffdüngung'])

# --------------------------------------------------
# GENERAL FARM INFORMATION
# --------------------------------------------------
with tab1:
    st.markdown("## Allgemeine Angaben")

    c1, c2, c3 = st.columns(3)

    with c1:
        duengejahr = st.date_input("Düngejahr", key="duengejahr")

    with c2:
        betriebsnr = st.text_input("Betriebsnr.", key="betriebsnr")

    with c3:
        betrieb = st.text_input("Betrieb", key="betrieb")



    # --------------------------------------------------
    # PARCEL INPUT FORM
    # --------------------------------------------------

    st.markdown("### Schlagdaten")

    with st.form("Schlagdaten"):

        c1, c2, c3 = st.columns(3)

        with c1:
            schlag = st.text_input(
                "Schlag",
                key="schlag_in",
            )

        # TODO : Warnung bei bereits existenter feldblock nr 
        with c2:
            feldblock_nr = st.number_input(
                "Feldblocknummer",
                min_value=0,
                value=None,
                step=1,
                key="feldblock_nr_in",
            )

        with c3:
            schlag_gr = st.number_input(
                "Schlaggröße in ha",
                min_value=0.0,
                value=None,
                step=1.0,
                key="schlag_gr_in",
            )

        cc1 , _ , cc3 = st.columns(3)

        with cc1: 
            vj_kultur = st.selectbox("Vorjahreskultur" ,options = kulturen, key = 'vj_kultur' , placeholder="")

        with cc3: 
            zwischenfrucht = st.selectbox("Zwischenfrucht (optional)" ,options=['Keine'] + zwischenfruechte, key = 'zwischenfrucht' , placeholder="")


        non_empty = (bool(schlag.strip())
            and feldblock_nr is not None
            and schlag_gr is not None
            and schlag_gr > 0
            and vj_kultur is not None)
        
        st.write(f'non_empty : {non_empty}')

        submit = st.form_submit_button("Submit")


    # --------------------------------------------------
    # VALIDATION AND STORAGE
    # --------------------------------------------------

    if submit and non_empty:

            schlag_data = {
                "Schlag": schlag.strip(),
                "Feldblock-Nummer": feldblock_nr,
                "Größe in ha": schlag_gr,
                "Vorjahreskultur" : vj_kultur ,
                "Zwischenfrucht" : zwischenfrucht if zwischenfrucht is not None else "KEINE"
            }

            s_id = f"S{feldblock_nr}_{int(schlag_gr)}ha"

            if s_id in st.session_state.schlag_collection:
                st.warning("Dieser Schlag wurde bereits eingetragen!")

            else:
                st.session_state.schlag_collection[s_id] = schlag_data
                st.session_state.reset_schlag_data = True
                st.success(f"Schlag '{schlag.strip()}' wurde eingetragen.")

                # Rerun so the reset flag is processed before widget creation
                st.rerun()
    if submit and not non_empty:
        st.warning("Bitte fülle alle Felder aus und gib eine Schlaggröße größer als 0 an.")

    # --------------------------------------------------
    # STORED PARCELS
    # --------------------------------------------------

    st.markdown("### Eingetragene Schläge")

    if st.session_state.schlag_collection:
        st.dataframe(
            [
                {"ID": s_id, **data}
                for s_id, data in st.session_state.schlag_collection.items()
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Noch keine Schläge eingetragen.")

with tab2: 
    st.markdown('## DBE Berechnung Stickstoff')

    if st.session_state.schlag_collection.keys():
        selected_schlag = st.selectbox(label = "Schlag auswählen" , options = st.session_state.schlag_collection.keys())    
    else:
        st.warning('Erstmal Schläge in "Allgemeine Angaben" eintragen!')

    if st.button("Schlagdaten anzeigen") and selected_schlag: 
        st.dataframe(st.session_state.schlag_collection[selected_schlag] , hide_index =False , column_config={'value' : f'Schlag : {selected_schlag}'})