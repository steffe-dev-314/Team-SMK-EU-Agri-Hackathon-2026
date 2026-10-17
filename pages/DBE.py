
import streamlit as st
import pandas as pd
import numpy as np

from CROPS import zwischenfruechte, kulturen
from calc_engine import streamlit_bde_wrapper , get_duev_ertrag , get_n_bedarf , get_ertrag_correction , get_humus_correction
from datetime import datetime


st.set_page_config(page_title="DBE - Stickstoff", layout="wide")
st.logo(".streamlit/logo.png", size="large")


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
    st.session_state.kultur = None
    st.session_state.vj_kultur = None
    st.session_state.zwischenfrucht = "Keine"

    # recalc keys reset 
    for key in list(st.session_state.keys()):
        if key.startswith("recalculate_"):
            del st.session_state[key]

    st.session_state.reset_full = False


if st.session_state.reset_schlag_data:
    st.session_state.schlag_in = ""
    st.session_state.feldblock_nr_in = None
    st.session_state.schlag_gr_in = None
    st.session_state.vj_kultur = None
    st.session_state.kultur = None
    st.session_state.zwischenfrucht = "Keine"

    st.session_state.reset_schlag_data = False


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    if st.button("RESET", type="secondary"):
        st.session_state.reset_full = True
        st.rerun()

    st.caption("ADMIN")


tab1, tab2, tab3 = st.tabs([
    "Allgemeine Angaben",
    "DBE - Stickstoff",
    "Dokumentation Stickstoffdüngung",
])


# --------------------------------------------------
# GENERAL FARM INFORMATION
# --------------------------------------------------

with tab1:
    st.markdown("## Allgemeine Angaben")

    st.markdown("### Betriebsdaten")
    c1, c2, c3 = st.columns(3)

    with c1:
        duengejahr = st.date_input("Düngejahr", key="duengejahr")

    with c2:
        betriebsnr = st.text_input("Betriebsnummer", key="betriebsnr")

    with c3:
        betrieb = st.text_input("Betrieb", key="betrieb")

    st.divider()
    st.markdown("### Schlagdaten")
    st.caption("Erfasse einen Schlag und ordne ihm die Kulturen zu.")

    with st.form("Schlagdaten"):
        st.markdown("**1. Identifikation und Fläche**")
        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:
            schlag = st.text_input("Schlagname", key="schlag_in")

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
                "Schlaggröße (ha)",
                min_value=0.0,
                value=None,
                step=0.1,
                key="schlag_gr_in",
            )

        st.markdown("**2. Fruchtfolge**")
        c1, c2, c3 = st.columns(3)

        with c1:
            kultur = st.selectbox(
                "Aktuelle Kultur",
                options=kulturen,
                key="kultur",
                placeholder="Kultur auswählen",
            )

        with c2:
            vj_kultur = st.selectbox(
                "Vorjahreskultur",
                options=kulturen,
                key="vj_kultur",
                placeholder="Kultur auswählen",
            )

        with c3:
            zwischenfrucht = st.selectbox(
                "Zwischenfrucht (optional)",
                options=["Keine"] + zwischenfruechte,
                key="zwischenfrucht",
            )

        st.divider()
        submit_schlag = st.form_submit_button(
            "Schlag hinzufügen",
            type="primary",
            use_container_width=True,
        )

    non_empty = (
        bool(schlag.strip())
        and feldblock_nr is not None
        and schlag_gr is not None
        and schlag_gr > 0
        and kultur is not None
        and vj_kultur is not None
    )

    if submit_schlag and non_empty:
        schlag_data_new = {
            "Schlag": schlag.strip(),
            "Feldblock-Nummer": feldblock_nr,
            "Größe in ha": schlag_gr,
            "Kultur": kultur,
            "Vorjahreskultur": vj_kultur,
            "Zwischenfrucht": zwischenfrucht,
        }

        s_id = f"S{feldblock_nr}_{int(schlag_gr)}ha"

        if s_id in st.session_state.schlag_collection:
            st.warning("Dieser Schlag wurde bereits eingetragen.")
        else:
            st.session_state.schlag_collection[s_id] = schlag_data_new
            st.session_state.reset_schlag_data = True
            st.success(f"Schlag '{schlag.strip()}' wurde eingetragen.")
            st.rerun()

    elif submit_schlag:
        st.warning(
            "Bitte fülle alle Pflichtfelder aus "
            "und gib eine Schlaggröße größer als 0 an."
        )

    st.divider()
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


# --------------------------------------------------
# DBE - NITROGEN
# --------------------------------------------------

with tab2:
    st.markdown("## DBE Berechnung Stickstoff")

    selected_schlag = None
    schlag_data = None

    calc_new = False
    show_data = False
    submit_dbe = False

    if st.session_state.schlag_collection:
        selected_schlag = st.selectbox(
            label="Schlag auswählen",
            options=list(st.session_state.schlag_collection.keys()),
            key="selected_schlag_dbe",
        )
    else:
        st.warning('Erstmal Schläge in "Allgemeine Angaben" eintragen!')

    if selected_schlag is not None:
        schlag_data = st.session_state.schlag_collection[selected_schlag]

        crop_name = schlag_data["Kultur"]
        crop_name_vj = schlag_data["Vorjahreskultur"]
        schlag_name = schlag_data["Schlag"]
        zwischen_name = schlag_data["Zwischenfrucht"]

        # Dates are stored per parcel
        seed_date = st.date_input(
            f"Datum der Aussaat von {crop_name}",
            key=f"seed_date_{selected_schlag}",
        )
        schlag_data["Datum der Aussaat"] = seed_date.strftime("%d.%m.%Y")

        if zwischen_name != "Keine":
            zwischen_date = st.date_input(
                f"Datum der Aussaat von {zwischen_name}",
                key=f"seed_date_zwischen_{selected_schlag}",
            )
            schlag_data["Datum der Aussaat Zwischenfrucht"] = (
                zwischen_date.strftime("%d.%m.%Y")
            )
        else:
            schlag_data["Datum der Aussaat Zwischenfrucht"] = "Keine"

        recalc_key = f"recalculate_{selected_schlag}"

        if "Stickstoffbedarf durch Dünger in kg / ha" in schlag_data:
            st.warning(
                f"Für Schlag {selected_schlag} existiert bereits eine DBE!"
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "Neu berechnen",
                    key=f"recalc_button_{selected_schlag}",
                ):
                    st.session_state[recalc_key] = True
                    st.rerun()

            with c2:
                show_data = st.button(
                    "Schlagdaten anzeigen",
                    key=f"show_data_{selected_schlag}",
                )

            if show_data:
                st.write(schlag_data)

    # Show the form if no DBE exists or recalculation was requested
    if selected_schlag is not None and (
        "Stickstoffbedarf durch Dünger in kg / ha" not in schlag_data
        or st.session_state.get(f"recalculate_{selected_schlag}", False)
    ):
        with st.form(f"Eingabe Daten für DBE_{selected_schlag}"):
            st.markdown("### Bodendaten")
            st.caption("Angaben zum aktuellen Zustand des Schlages.")

            c1, c2, c3 = st.columns(3)

            with c1:
                N_min = st.number_input(
                    f"Nmin / Richtwert · {schlag_name} (kg N/ha)",
                    min_value=0.0,
                    step=1.0,
                    key=f"N_min_{selected_schlag}",
                )

            with c2:
                humus = st.number_input(
                    "Humusgehalt (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key=f"humus_{selected_schlag}",
                ) / 100

            with c3:
                N_prev = st.number_input(
                    f"Vorjahresdüngung: {crop_name_vj}",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    help=(
                        "Gesamte Stickstoffmenge aus organischen und "
                        "organisch-mineralischen Düngemitteln im Vorjahr "
                        "(kg N/ha)."
                    ),
                    key=f"N_prev_{selected_schlag}",
                )

            st.divider()
            st.markdown("### Ertragsdaten")
            st.caption(
                f"Ertragsinformationen für die aktuelle Kultur: {crop_name}"
            )

            Yield_5yr_mean = st.number_input(
                "Durchschnittlicher Ertrag der letzten 5 Jahre (dt/ha)",
                min_value=0.0,
                step=1.0,
                key=f"yield_5yr_{selected_schlag}",
            )

            st.divider()
            st.markdown("### Fruchtfolge")
            st.caption(
                "Stickstoffkorrekturen aus den vorangegangenen Kulturen."
            )

            c1, c2 = st.columns(2)

            with c1:
                N_vor = st.number_input(
                    f"Abschlag · Vorjahreskultur: {crop_name_vj} (kg N/ha)",
                    min_value=0.0,
                    step=1.0,
                    key=f"N_vor_{selected_schlag}",
                )

            with c2:
                if zwischen_name != "Keine":
                    N_zw = st.number_input(
                        f"Abschlag · Zwischenfrucht: {zwischen_name} (kg N/ha)",
                        min_value=0.0,
                        step=1.0,
                        key=f"N_zw_{selected_schlag}",
                    )
                else:
                    N_zw = 0.0
                    st.text_input(
                        "Zwischenfrucht",
                        value="Keine",
                        disabled=True,
                        key=f"zwischenfrucht_display_{selected_schlag}",
                    )

            dbe_args = {
                'Datum' : seed_date ,
                'Kultur' : crop_name ,
                'Ertrag laut DüV' : get_duev_ertrag(crop_name) , 
                'Durchschnittsertrag 5 Jahre Betrieb' : Yield_5yr_mean , 
                'N-Bedarfswert' : get_n_bedarf(crop_name),
                'Abschlag Ertragsdifferenz' : get_ertrag_correction(crop_name , Yield_5yr_mean), 
                'N_min Probe / Richtwert' : N_min , 
                'Standort / Humus' : get_humus_correction(humus) , 
                'Abschlag Vorfrucht' : N_vor , 
                'Abschlag Zwischenfrucht' : N_zw
                }

            st.divider()
            submit_dbe = st.form_submit_button(
                "DBE berechnen",
                type="primary",
                use_container_width=True,
            )


            

        if submit_dbe:
            

            dbe = streamlit_bde_wrapper(
                schlag=crop_name,
                mean_5_yrs=Yield_5yr_mean,
                N_min=N_min,
                humus=humus,
                N_prev=N_prev,
                N_vor=N_vor,
                N_zw=N_zw,
            )

            schlag_data["Stickstoffbedarf durch Dünger in kg / ha"] = round(dbe, 2)
            schlag_data['DBE_Args'] = dbe_args
            st.session_state[recalc_key] = False

            if "DBE_Args" in schlag_data:
                st.write(dbe_args)


            st.success("DBE wurde berechnet und gespeichert.")
            st.rerun()

    # Always display the saved DBE, including after a rerun
    if selected_schlag is not None and "Stickstoffbedarf durch Dünger in kg / ha" in schlag_data:
        st.divider()
        st.subheader("Ergebnis der Stickstoff-Düngebedarfsermittlung")

        st.metric(
            label=f"Berechneter Stickstoffbedarf · {selected_schlag}",
            value=f"{schlag_data['Stickstoffbedarf durch Dünger in kg / ha']:.2f} kg N/ha",
        )

        st.info(
            f"Der berechnete Stickstoffbedarf für Schlag "
            f"**{selected_schlag}** beträgt "
            f"**{schlag_data['Stickstoffbedarf durch Dünger in kg / ha']:.2f} kg N/ha**."
        )

# --------------------------------------------------
# FERTILISATION DOCUMENTATION
# --------------------------------------------------

with tab3:
    st.markdown("## Dokumentation Stickstoffdüngung")
    st.info(
        "Die Dokumentation der einzelnen Düngungsereignisse "
        "wird im nächsten Schritt implementiert."
    )
