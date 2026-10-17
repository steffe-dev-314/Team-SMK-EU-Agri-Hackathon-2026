
import streamlit as st
import pandas as pd
import numpy as np

from CROPS import zwischenfruechte, kulturen
from FERTILIZERS import FERTILZER_VALUES
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

    if "fert_count" not in st.session_state:
        st.session_state.fert_count = 0

    if "fert_collection" not in st.session_state:
        st.session_state.fert_collection = {}

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

    st.session_state.fert_count = 0

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


tab1, tab2, tab3 , tab4 , tab5= st.tabs([
    "Allgemeine Angaben",
    "DBE - Stickstoff",
    "Dokumentation Stickstoffdüngung",
    "Zusammenfassung und Export",
    "TTT"
])


# --------------------------------------------------
# GENERAL FARM INFORMATION
# --------------------------------------------------

with tab1:
    st.markdown("## Allgemeine Angaben")

    # --------------------------------------------------
    # FARM INFORMATION
    # --------------------------------------------------

    st.markdown("### Betriebsdaten")
    c1, c2, c3 = st.columns(3)

    with c1:
        duengejahr = st.text_input("Düngejahr", key="duengejahr")

    with c2:
        betriebsnr = st.text_input("Betriebsnummer", key="betriebsnr")

    with c3:
        betrieb = st.text_input("Betrieb", key="betrieb")

    farm_metadata = {'Fert_Year' : duengejahr , 'farm_id' : betriebsnr , 'farm_name' : betrieb}

    st.divider()

    # --------------------------------------------------
    # CSV IMPORT
    # --------------------------------------------------

    st.markdown("### Schläge aus CSV importieren")
    st.caption(
        "Importiere mehrere Schläge auf einmal. "
        "Die CSV benötigt eine Kopfzeile mit den folgenden Spalten."
    )

    csv_template = pd.DataFrame(columns=[
        "Schlag",
        "Feldblock-Nummer",
        "Größe in ha",
        "Vorjahreskultur",
        "Zwischenfrucht",
    ])

    st.download_button(
        label="CSV-Vorlage herunterladen",
        data=csv_template.to_csv(
            index=False,
            sep=";",
            encoding="utf-8-sig",
        ),
        file_name="schlaege_vorlage.csv",
        mime="text/csv",
    )

    uploaded_csv = st.file_uploader(
        "Schlagdaten-CSV auswählen",
        type=["csv"],
        key="schlag_csv_upload",
    )

    if uploaded_csv is not None:
        try:
            uploaded_csv.seek(0)

            # Read semicolon-separated CSV first, then comma-separated.
            csv_df = pd.read_csv(
                uploaded_csv,
                sep=";",
                encoding="utf-8-sig",
            )

            if len(csv_df.columns) == 1:
                uploaded_csv.seek(0)
                csv_df = pd.read_csv(
                    uploaded_csv,
                    sep=",",
                    encoding="utf-8-sig",
                )

            csv_df.columns = csv_df.columns.str.strip()

            required_cols = [
                "Schlag",
                "Feldblock-Nummer",
                "Größe in ha",
                "Vorjahreskultur",
                "Zwischenfrucht",
            ]

            missing_cols = [
                col for col in required_cols
                if col not in csv_df.columns
            ]

            if missing_cols:
                st.error(
                    "Folgende Spalten fehlen in der CSV: "
                    + ", ".join(missing_cols)
                )

            else:
                csv_df = csv_df[required_cols].copy()

                for col in [
                    "Schlag",
                    "Vorjahreskultur",
                    "Zwischenfrucht",
                ]:
                    csv_df[col] = (
                        csv_df[col].astype("string").str.strip()
                    )

                csv_df["Feldblock-Nummer"] = pd.to_numeric(
                    csv_df["Feldblock-Nummer"],
                    errors="coerce",
                )

                csv_df["Größe in ha"] = pd.to_numeric(
                    csv_df["Größe in ha"]
                    .astype("string")
                    .str.replace(",", ".", regex=False),
                    errors="coerce",
                )

                valid_rows = []
                errors = []

                for idx, row in csv_df.iterrows():
                    excel_row = idx + 2

                    if pd.isna(row["Schlag"]) or not row["Schlag"]:
                        errors.append(
                            f"Zeile {excel_row}: Schlagname fehlt."
                        )
                        continue

                    feldblock = row["Feldblock-Nummer"]

                    if (
                        pd.isna(feldblock)
                        or feldblock < 0
                        or not float(feldblock).is_integer()
                    ):
                        errors.append(
                            f"Zeile {excel_row}: "
                            "Feldblock-Nummer ungültig."
                        )
                        continue

                    area = row["Größe in ha"]

                    if pd.isna(area) or area <= 0:
                        errors.append(
                            f"Zeile {excel_row}: "
                            "Schlaggröße muss größer als 0 sein."
                        )
                        continue

                    vj_kultur = row["Vorjahreskultur"]

                    if (
                        pd.isna(vj_kultur)
                        or vj_kultur not in kulturen
                    ):
                        errors.append(
                            f"Zeile {excel_row}: "
                            f"Unbekannte Vorjahreskultur "
                            f"'{vj_kultur}'."
                        )
                        continue

                    zwischenfrucht = row["Zwischenfrucht"]

                    if (
                        pd.isna(zwischenfrucht)
                        or zwischenfrucht == ""
                    ):
                        zwischenfrucht = "Keine"

                    if zwischenfrucht not in ["Keine"] + zwischenfruechte:
                        errors.append(
                            f"Zeile {excel_row}: "
                            f"Unbekannte Zwischenfrucht "
                            f"'{zwischenfrucht}'."
                        )
                        continue

                    valid_rows.append({
                        "Schlag": str(row["Schlag"]),
                        "Feldblock-Nummer": int(feldblock),
                        "Größe in ha": float(area),
                        "Vorjahreskultur": str(vj_kultur),
                        "Zwischenfrucht": str(zwischenfrucht),
                    })

                if errors:
                    st.warning(
                        "Einige Zeilen enthalten Fehler. "
                        "Bitte korrigiere die CSV und lade sie erneut hoch."
                    )

                    for error in errors:
                        st.write(f"- {error}")

                if valid_rows:
                    st.markdown("#### Vorschau")
                    st.dataframe(
                        pd.DataFrame(valid_rows),
                        use_container_width=True,
                        hide_index=True,
                    )

                    if st.button(
                        "Schläge importieren",
                        type="primary",
                        key="import_schlaege_csv",
                    ):
                        new_parcels = {}
                        duplicate_ids = []

                        existing_ids = set(
                            st.session_state.schlag_collection.keys()
                        )

                        for parcel in valid_rows:
                            s_id = (
                                f"S{parcel['Feldblock-Nummer']}_"
                                f"{int(parcel['Größe in ha'])}ha"
                            )

                            if (
                                s_id in existing_ids
                                or s_id in new_parcels
                            ):
                                duplicate_ids.append(s_id)
                            else:
                                new_parcels[s_id] = parcel

                        if duplicate_ids:
                            st.warning(
                                "Diese Schlag-IDs existieren bereits "
                                "oder kommen mehrfach in der CSV vor: "
                                + ", ".join(duplicate_ids)
                            )

                        if new_parcels:
                            st.session_state.schlag_collection.update(
                                new_parcels
                            )

                            st.success(
                                f"{len(new_parcels)} Schläge "
                                "erfolgreich importiert."
                            )
                            st.rerun()

        except Exception as e:
            st.error(f"Die CSV konnte nicht gelesen werden: {e}")

    st.divider()

    # --------------------------------------------------
    # MANUAL PARCEL ENTRY
    # --------------------------------------------------

    st.markdown("### Schlagdaten")
    st.caption(
        "Erfasse einen Schlag und ordne ihm die Vorjahres- "
        "und Zwischenfrucht zu. Die aktuelle Kultur wird in "
        "der DBE-Berechnung ausgewählt."
    )

    with st.form("Schlagdaten"):
        st.markdown("**1. Identifikation und Fläche**")
        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:
            schlag = st.text_input(
                "Schlagname",
                key="schlag_in",
            )

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
        c1, c2 = st.columns(2)

        with c1:
            vj_kultur = st.selectbox(
                "Vorjahreskultur",
                options=kulturen,
                key="vj_kultur",
                placeholder="Kultur auswählen",
            )

        with c2:
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
        and vj_kultur is not None
    )

    if submit_schlag and non_empty:
        schlag_data_new = {
            "Schlag": schlag.strip(),
            "Feldblock-Nummer": int(feldblock_nr),
            "Größe in ha": float(schlag_gr),
            "Vorjahreskultur": vj_kultur,
            "Zwischenfrucht": zwischenfrucht,
        }

        s_id = f"S{int(feldblock_nr)}_{int(schlag_gr)}ha"

        if s_id in st.session_state.schlag_collection:
            st.warning("Dieser Schlag wurde bereits eingetragen.")
        else:
            st.session_state.schlag_collection[s_id] = schlag_data_new
            st.session_state.reset_schlag_data = True
            st.success(
                f"Schlag '{schlag.strip()}' wurde eingetragen."
            )
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

    show_data = False
    submit_dbe = False

    if st.session_state.schlag_collection:
        selected_schlag = st.selectbox(
            label="Schlag auswählen",
            options=list(st.session_state.schlag_collection.keys()),
            key="selected_schlag_dbe",
        )
    else:
        st.warning(
            'Erstmal Schläge in "Allgemeine Angaben" eintragen!'
        )

    if selected_schlag is not None:
        schlag_data = st.session_state.schlag_collection[selected_schlag]

        schlag_name = schlag_data["Schlag"]
        crop_name_vj = schlag_data["Vorjahreskultur"]
        zwischen_name = schlag_data["Zwischenfrucht"]

        # Current crop is now selected in Tab 2.
        saved_crop = schlag_data.get("Kultur")

        crop_index = (
            kulturen.index(saved_crop)
            if saved_crop in kulturen
            else None
        )

        crop_name = st.selectbox(
            "Aktuelle Kultur für die DBE",
            options=kulturen,
            index=crop_index,
            placeholder="Kultur auswählen",
            key=f"kultur_dbe_{selected_schlag}",
        )

        if crop_name is not None:
            schlag_data["Kultur"] = crop_name

            seed_date = st.date_input(
                f"Datum der Aussaat von {crop_name}",
                key=f"seed_date_{selected_schlag}",
            )

            schlag_data["Datum der Aussaat"] = (
                seed_date.strftime("%d.%m.%Y")
            )

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

    # Show the form only if a current crop has been selected.
    if (
        selected_schlag is not None
        and crop_name is not None
        and (
            "Stickstoffbedarf durch Dünger in kg / ha" not in schlag_data
            or st.session_state.get(
                f"recalculate_{selected_schlag}", False
            )
        )
    ):
        with st.form(f"Eingabe Daten für DBE_{selected_schlag}"):
            st.markdown("### Bodendaten")
            st.caption(
                "Angaben zum aktuellen Zustand des Schlages."
            )

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
                "Hauptfrucht": {
                    "Datum": seed_date,
                    "Kultur": crop_name,
                    "Ertrag laut DüV": get_duev_ertrag(crop_name),
                    "Durchschnittsertrag 5 Jahre Betrieb": Yield_5yr_mean,
                    "N-Bedarfswert": get_n_bedarf(crop_name),
                    "Abschlag Ertragsdifferenz": get_ertrag_correction(
                        crop_name, Yield_5yr_mean
                    ),
                    "N_min Probe / Richtwert": N_min,
                    "Standort / Humus": get_humus_correction(humus),
                    "Abschlag Vorfrucht": N_vor,
                    "Abschlag Zwischenfrucht": N_zw,
                },
                "Zwischenfrucht": {
                    "N-Bedarf": (
                        get_n_bedarf(zwischen_name)
                        if zwischen_name != "Keine"
                        else "Keine"
                    )
                },
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

            schlag_data["Stickstoffbedarf durch Dünger in kg / ha"] = (
                round(dbe, 2)
            )
            schlag_data["DBE_Args"] = dbe_args
            st.session_state[recalc_key] = False

            st.success("DBE wurde berechnet und gespeichert.")
            st.rerun()

    # Always display the saved DBE.
    if (
        selected_schlag is not None
        and "Stickstoffbedarf durch Dünger in kg / ha" in schlag_data
    ):
        st.divider()
        st.subheader(
            "Ergebnis der Stickstoff-Düngebedarfsermittlung"
        )

        st.metric(
            label=f"Berechneter Stickstoffbedarf · {selected_schlag}",
            value=(
                f"{schlag_data['Stickstoffbedarf durch Dünger in kg / ha']:.2f} "
                "kg N/ha"
            ),
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

    if st.session_state.schlag_collection:
        selected_schlag = st.selectbox(
            label="Schlag auswählen",
            options=list(st.session_state.schlag_collection.keys()),
            key="selected_schlag_duev_doc",
        )

    if selected_schlag:

        st.session_state.fert_collection[selected_schlag] = {}

        cc1 , cc2 = st.columns(2)
        with cc1:
            if st.button("Düngung hinzufügen"):
                st.session_state.fert_count += 1

        with cc2: 
            if st.button("Düngung entfernen"):
                if st.session_state.fert_count >1: 
                    st.session_state.fert_count -= 1

        for i in range(st.session_state.fert_count):
            
            d_id = f'{selected_schlag}_DG_{i+1}'

            c1, c2, c3=  st.columns(3)

            with c1:
                date_fert = st.date_input(
                    "Datum der Düngung",
                    key=f"date_fert_{i}",
                )

            with c2:
                type_fert = st.selectbox(label = 'Art des Düngers' , options=FERTILZER_VALUES.keys() , key = f"type_fert_{i}")
            
            unit_fert = FERTILZER_VALUES[type_fert]['einheit']
            with c3:
                amt_fert = st.number_input(
                    f"Genutzte Menge in {unit_fert}",
                    min_value=0.0,
                    key=f"amt_fert_{i}",
                )
    
            if date_fert and type_fert and unit_fert and amt_fert:        

                st.session_state.fert_collection[selected_schlag][d_id] = {'Datum' : date_fert , 
                                                                           'Düngetyp' : type_fert ,
                                                                           'Einheit' : unit_fert , 
                                                                           f'Düngemente in {unit_fert} / ha' : amt_fert, 
                                                                           f'Stickstoff Gesamt in {unit_fert} / ha' : amt_fert*FERTILZER_VALUES[type_fert]['Nges pro Einheit'],
                                                                           f'Stickstoff Pflanzenverfügbar in {unit_fert} / ha' : amt_fert*FERTILZER_VALUES[type_fert]['Npfluer pro Einheit']}
            
        st.session_state.schlag_collection[selected_schlag]['Düngeinformation'] = st.session_state.fert_collection[selected_schlag]
        st.write(st.session_state.schlag_collection)


# --------------------------------------------------
# SUMMARY AND EXPORT
# --------------------------------------------------

with tab4:
    st.markdown("## Zusammenfassung und Export")

    if not st.session_state.schlag_collection:
        st.info("Bitte zunächst Schläge in 'Allgemeine Angaben' eintragen.")

    else:
        # Only include parcels with both DBE and fertilizer data
        eligible_schlaege = {
            s_id: schlag_data
            for s_id, schlag_data in st.session_state.schlag_collection.items()
            if (
                schlag_data.get(
                    "Stickstoffbedarf durch Dünger in kg / ha"
                ) is not None
                and bool(
                    st.session_state.fert_collection.get(s_id, {})
                )
            )
        }

        if not eligible_schlaege:
            st.info(
                "Es gibt noch keine Schläge mit abgeschlossener "
                "DBE und dokumentierten Düngungsereignissen."
            )

        else:
            # 1. Düngebedarfsermittlung
            st.markdown("### 1. Düngebedarfsermittlung")

            dbe_rows = []

            for s_id, schlag_data in eligible_schlaege.items():
                dbe_args = schlag_data.get("DBE_Args", {})
                hauptfrucht = dbe_args.get("Hauptfrucht", {})

                dbe_rows.append({
                    "Schlag-ID": s_id,
                    "Schlag": schlag_data.get("Schlag"),
                    "Feldblock-Nummer": schlag_data.get(
                        "Feldblock-Nummer"
                    ),
                    "Fläche (ha)": schlag_data.get("Größe in ha"),
                    "Hauptfrucht": hauptfrucht.get(
                        "Kultur", schlag_data.get("Kultur")
                    ),
                    "Aussaatdatum": hauptfrucht.get("Datum"),
                    "Zwischenfrucht": schlag_data.get("Zwischenfrucht"),
                    "Aussaat Zwischenfrucht": schlag_data.get(
                        "Datum der Aussaat Zwischenfrucht"
                    ),
                    "Ertrag laut DüV": hauptfrucht.get(
                        "Ertrag laut DüV"
                    ),
                    "Betrieblicher 5-Jahres-Ertrag": hauptfrucht.get(
                        "Durchschnittsertrag 5 Jahre Betrieb"
                    ),
                    "N-Bedarfswert (kg N/ha)": hauptfrucht.get(
                        "N-Bedarfswert"
                    ),
                    "Ertragskorrektur (kg N/ha)": hauptfrucht.get(
                        "Abschlag Ertragsdifferenz"
                    ),
                    "Nmin (kg N/ha)": hauptfrucht.get(
                        "N_min Probe / Richtwert"
                    ),
                    "Humuskorrektur (kg N/ha)": hauptfrucht.get(
                        "Standort / Humus"
                    ),
                    "Vorfruchtkorrektur (kg N/ha)": hauptfrucht.get(
                        "Abschlag Vorfrucht"
                    ),
                    "Zwischenfruchtkorrektur (kg N/ha)": hauptfrucht.get(
                        "Abschlag Zwischenfrucht"
                    ),
                    "Berechneter Düngebedarf (kg N/ha)": schlag_data.get(
                        "Stickstoffbedarf durch Dünger in kg / ha"
                    ),
                })

            dbe_df = pd.DataFrame(dbe_rows)
            st.dataframe(
                dbe_df,
                use_container_width=True,
                hide_index=True,
            )

            # 2. Dokumentation der Stickstoffdüngung
            st.markdown("### 2. Dokumentation der Stickstoffdüngung")

            fert_rows = []

            for s_id, schlag_data in eligible_schlaege.items():
                fert_events = st.session_state.fert_collection.get(
                    s_id, {}
                )

                for event_id, fert in fert_events.items():
                    einheit = fert.get("Einheit", "")

                    fert_rows.append({
                        "Schlag-ID": s_id,
                        "Schlag": schlag_data.get("Schlag"),
                        "Feldblock-Nummer": schlag_data.get(
                            "Feldblock-Nummer"
                        ),
                        "Düngungs-ID": event_id,
                        "Düngungsdatum": fert.get("Datum"),
                        "Düngemittel": fert.get("Düngetyp"),
                        "Einheit": einheit,
                        "Düngermenge": fert.get(
                            f"Düngemente in {einheit} / ha"
                        ),
                        "N gesamt": fert.get(
                            f"Stickstoff Gesamt in {einheit} / ha"
                        ),
                        "N pflanzenverfügbar": fert.get(
                            f"Stickstoff Pflanzenverfügbar in {einheit} / ha"
                        ),
                    })

            fert_df = pd.DataFrame(fert_rows)

            st.dataframe(
                fert_df,
                use_container_width=True,
                hide_index=True,
            )

            # 3. Vergleich: Düngebedarf vs. pflanzenverfügbarer Stickstoff
            st.markdown(
                "### 3. Vergleich: Düngebedarf und Stickstoffdüngung"
            )

            comparison_rows = []

            for s_id, schlag_data in eligible_schlaege.items():
                dbe_per_ha = schlag_data.get(
                    "Stickstoffbedarf durch Dünger in kg / ha"
                )
                area = schlag_data.get("Größe in ha")

                fert_events = st.session_state.fert_collection.get(
                    s_id, {}
                )

                n_available_per_ha = sum(
                    fert.get(
                        f"Stickstoff Pflanzenverfügbar in "
                        f"{fert.get('Einheit', '')} / ha",
                        0,
                    ) or 0
                    for fert in fert_events.values()
                )

                if dbe_per_ha is None or area is None:
                    continue

                dbe_total = dbe_per_ha * area
                n_available_total = n_available_per_ha * area

                comparison_rows.append({
                    "Schlag": schlag_data.get("Schlag"),
                    "Fläche (ha)": area,

                    # Hektarbezogen
                    "DBE (kg N/ha)": dbe_per_ha,
                    "Pflanzenverfügbares N (kg N/ha)": (
                        n_available_per_ha
                    ),
                    "Differenz (kg N/ha)": (
                        dbe_per_ha - n_available_per_ha
                    ),

                    # Flächenbezogen
                    "DBE gesamt (kg N)": dbe_total,
                    "Pflanzenverfügbares N gesamt (kg N)": (
                        n_available_total
                    ),
                    "Differenz gesamt (kg N)": (
                        dbe_total - n_available_total
                    ),
                })

            comparison_df = pd.DataFrame(comparison_rows)

            if comparison_df.empty:
                st.info(
                    "Für die ausgewählten Schläge konnte kein "
                    "Vergleich erstellt werden."
                )
            else:
                st.dataframe(
                    comparison_df.round(2),
                    use_container_width=True,
                    hide_index=True,
                )

# TAB 5 — EXPORT
# --------------------------------------------------

from form_to_csv import get_dbe_rows, get_fert_rows, add_rows , fill_top_rows

with tab5:
    st.markdown("## Export")

    if not st.session_state.schlag_collection:
        st.info("Bitte zunächst Schläge in 'Allgemeine Angaben' eintragen.")

    else:
        schlag_ids = list(st.session_state.schlag_collection.keys())

        selected_schlag = st.selectbox(
            "Schlag für den Export auswählen",
            options=schlag_ids,
            format_func=lambda s_id: (
                st.session_state.schlag_collection[s_id]["Schlag"]
            ),
            key="export_schlag",
        )

        if selected_schlag is not None:
            schlag_data = st.session_state.schlag_collection[selected_schlag]

            dbe_cols = get_dbe_rows(schlag_data)
            fert_cols = get_fert_rows(selected_schlag, schlag_data)

            top_rows = fill_top_rows(
                schlag_data,
                farm_metadata,
            )

            export_df = add_rows(
                dbe_cols=dbe_cols,
                fert_cols=fert_cols,
                top_rows=top_rows,
                area=schlag_data["Größe in ha"],
            )


            st.markdown("### Vorschau")
            st.dataframe(export_df, use_container_width=True)

            """
            csv = export_df.to_csv(
                index=False,
                header=False,
                sep=";",
                decimal=",",
                encoding="utf-8-sig",
            )

            st.download_button(
                label="CSV herunterladen",
                data=csv,
                file_name=f"{schlag_data['Schlag']}_export.csv",
                mime="text/csv",
            )   
            """