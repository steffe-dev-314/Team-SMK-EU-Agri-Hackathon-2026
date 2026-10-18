import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path

from CROPS import zwischenfruechte, kulturen
from FERTILIZERS import FERTILZER_VALUES
from calc_engine import (
    streamlit_bde_wrapper,
    get_duev_ertrag,
    get_n_bedarf,
    get_ertrag_correction,
    get_humus_correction,
)
from datetime import datetime


st.set_page_config(page_title="DBE - Nitrogen", layout="wide")
st.logo(".streamlit/logo.png", size="large")


# --------------------------------------------------
# FARM METADATA PERSISTENCE
# --------------------------------------------------

FARM_METADATA_PATH = Path("data/farm_metadata.json")


def load_farm_metadata():
    if FARM_METADATA_PATH.exists():
        try:
            with FARM_METADATA_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                return {
                    "duengejahr": str(data.get("duengejahr", "")),
                    "betriebsnr": str(data.get("betriebsnr", "")),
                    "betrieb": str(data.get("betrieb", "")),
                }

        except (OSError, json.JSONDecodeError):
            pass

    return {
        "duengejahr": "",
        "betriebsnr": "",
        "betrieb": "",
    }


def save_farm_metadata(metadata):
    with FARM_METADATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


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

    if "farm_metadata" not in st.session_state:
        st.session_state.farm_metadata = load_farm_metadata()

    # Restore farm data into the text-input widgets.
    for key in ("duengejahr", "betriebsnr", "betrieb"):
        if key not in st.session_state:
            st.session_state[key] = st.session_state.farm_metadata.get(
                key, ""
            )


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
    st.session_state.fert_collection = {}

    # Reset calculation flags.
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
    "General Information",
    "Nitrogen Requirement",
    "Nitrogen Fertilization Records",
])


# --------------------------------------------------
# GENERAL FARM INFORMATION
# --------------------------------------------------

with tab1:
    st.markdown("## General Information")

    # --------------------------------------------------
    # FARM INFORMATION
    # --------------------------------------------------

    st.markdown("### Farm Details")
    c1, c2, c3 = st.columns(3)

    with c1:
        duengejahr = st.text_input(
            "Fertilization Year",
            key="duengejahr",
        )

    with c2:
        betriebsnr = st.text_input(
            "Farm Registration Number",
            key="betriebsnr",
        )

    with c3:
        betrieb = st.text_input(
            "Farm Name",
            key="betrieb",
        )

    # Save the current values to session state and disk.
    st.session_state.farm_metadata = {
        "duengejahr": duengejahr,
        "betriebsnr": betriebsnr,
        "betrieb": betrieb,
    }

    try:
        save_farm_metadata(st.session_state.farm_metadata)
    except OSError as e:
        st.warning(
            f"Farm data could not be saved permanently: {e}"
        )

    st.divider()

    # --------------------------------------------------
    # CSV IMPORT
    # --------------------------------------------------

    st.markdown("### Import Parcels from CSV")
    st.caption(
        "Import multiple parcels at once. "
        "The CSV file must contain a header row with the following columns."
    )

    csv_template = pd.DataFrame(columns=[
        "Parcel Name",
        "Field Block Number",
        "Area in ha",
        "Previous Year's Crop",
        "Catch Crop",
    ])

    st.download_button(
        label="Download CSV Template",
        data=csv_template.to_csv(
            index=False,
            sep=";",
            encoding="utf-8-sig",
        ),
        file_name="parcels_template.csv",
        mime="text/csv",
    )

    uploaded_csv = st.file_uploader(
        "Select Parcel Data CSV",
        type=["csv"],
        key="schlag_csv_upload",
    )

    if uploaded_csv is not None:
        try:
            uploaded_csv.seek(0)

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

            # English CSV headers are mapped to the internal German keys.
            csv_columns = {
                "Parcel Name": "Schlag",
                "Field Block Number": "Feldblock-Nummer",
                "Area in ha": "Größe in ha",
                "Previous Year's Crop": "Vorjahreskultur",
                "Catch Crop": "Zwischenfrucht",
            }

            required_cols = list(csv_columns.keys())

            missing_cols = [
                col for col in required_cols
                if col not in csv_df.columns
            ]

            if missing_cols:
                st.error(
                    "The following columns are missing from the CSV: "
                    + ", ".join(missing_cols)
                )

            else:
                csv_df = csv_df[required_cols].copy()
                csv_df = csv_df.rename(columns=csv_columns)

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
                            f"Row {excel_row}: Parcel name is missing."
                        )
                        continue

                    feldblock = row["Feldblock-Nummer"]

                    if (
                        pd.isna(feldblock)
                        or feldblock < 0
                        or not float(feldblock).is_integer()
                    ):
                        errors.append(
                            f"Row {excel_row}: "
                            "Invalid field block number."
                        )
                        continue

                    area = row["Größe in ha"]

                    if pd.isna(area) or area <= 0:
                        errors.append(
                            f"Row {excel_row}: "
                            "Parcel area must be greater than 0."
                        )
                        continue

                    vj_kultur = row["Vorjahreskultur"]

                    if (
                        pd.isna(vj_kultur)
                        or vj_kultur not in kulturen
                    ):
                        errors.append(
                            f"Row {excel_row}: "
                            f"Unknown previous year's crop "
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
                            f"Row {excel_row}: "
                            f"Unknown catch crop "
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
                        "Some rows contain errors. "
                        "Please correct the CSV and upload it again."
                    )

                    for error in errors:
                        st.write(f"- {error}")

                if valid_rows:
                    st.markdown("#### Preview")
                    st.dataframe(
                        pd.DataFrame(valid_rows).rename(columns={
                            "Schlag": "Parcel Name",
                            "Feldblock-Nummer": "Field Block Number",
                            "Größe in ha": "Area in ha",
                            "Vorjahreskultur": "Previous Year's Crop",
                            "Zwischenfrucht": "Catch Crop",
                        }),
                        use_container_width=True,
                        hide_index=True,
                    )

                    if st.button(
                        "Import Parcels",
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
                                "These parcel IDs already exist "
                                "or occur multiple times in the CSV: "
                                + ", ".join(duplicate_ids)
                            )

                        if new_parcels:
                            st.session_state.schlag_collection.update(
                                new_parcels
                            )

                            st.success(
                                f"{len(new_parcels)} parcels "
                                "successfully imported."
                            )
                            st.rerun()

        except Exception as e:
            st.error(f"The CSV file could not be read: {e}")

    st.divider()

    # --------------------------------------------------
    # MANUAL PARCEL ENTRY
    # --------------------------------------------------

    st.markdown("### Parcel Details")
    st.caption(
        "Enter a parcel and assign its previous year's crop "
        "and catch crop. The current crop is selected "
        "during the nitrogen requirement calculation."
    )

    with st.form("Schlagdaten"):
        st.markdown("**1. Identification and Area**")
        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:
            schlag = st.text_input(
                "Parcel Name",
                key="schlag_in",
            )

        with c2:
            feldblock_nr = st.number_input(
                "Field Block Number",
                min_value=0,
                value=None,
                step=1,
                key="feldblock_nr_in",
            )

        with c3:
            schlag_gr = st.number_input(
                "Parcel Area (ha)",
                min_value=0.0,
                value=None,
                step=0.1,
                key="schlag_gr_in",
            )

        st.markdown("**2. Crop Rotation**")
        c1, c2 = st.columns(2)

        with c1:
            vj_kultur = st.selectbox(
                "Previous Year's Crop",
                options=kulturen,
                key="vj_kultur",
                placeholder="Select a crop",
            )

        with c2:
            zwischenfrucht = st.selectbox(
                "Catch Crop (optional)",
                options=["Keine"] + zwischenfruechte,
                key="zwischenfrucht",
                format_func=lambda x: (
                    "None" if x == "Keine" else x
                ),
            )

        st.divider()

        submit_schlag = st.form_submit_button(
            "Add Parcel",
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
            st.warning("This parcel has already been added.")
        else:
            st.session_state.schlag_collection[s_id] = schlag_data_new
            st.session_state.reset_schlag_data = True
            st.success(
                f"Parcel '{schlag.strip()}' has been added."
            )
            st.rerun()

    elif submit_schlag:
        st.warning(
            "Please complete all required fields "
            "and enter a parcel area greater than 0."
        )

    st.divider()
    st.markdown("### Registered Parcels")

    if st.session_state.schlag_collection:
        parcel_display = pd.DataFrame([
            {"Parcel ID": s_id, **data}
            for s_id, data in st.session_state.schlag_collection.items()
        ]).rename(columns={
            "Schlag": "Parcel Name",
            "Feldblock-Nummer": "Field Block Number",
            "Größe in ha": "Area (ha)",
            "Vorjahreskultur": "Previous Year's Crop",
            "Zwischenfrucht": "Catch Crop",
            "Kultur": "Current Crop",
            "Datum der Aussaat": "Sowing Date",
            "Datum der Aussaat Zwischenfrucht": "Catch Crop Sowing Date",
            "Stickstoffbedarf durch Dünger in kg / ha":
                "Nitrogen Fertilizer Requirement (kg N/ha)",
        })

        st.dataframe(
            parcel_display,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No parcels have been registered yet.")


# --------------------------------------------------
# DBE - NITROGEN
# --------------------------------------------------

with tab2:
    st.markdown("## Nitrogen Fertilizer Requirement Calculation")

    selected_schlag = None
    schlag_data = None
    crop_name = None
    seed_date = None

    show_data = False
    submit_dbe = False

    if st.session_state.schlag_collection:
        selected_schlag = st.selectbox(
            label="Select Parcel",
            options=list(st.session_state.schlag_collection.keys()),
            format_func=lambda s_id: (
                f"{st.session_state.schlag_collection[s_id].get('Schlag', 'Unnamed Parcel')} "
                f"({s_id})"
            ),
            key="selected_schlag_dbe",
        )
    else:
        st.warning(
            'Please add parcels under "General Information" first.'
        )

    if selected_schlag is not None:
        schlag_data = st.session_state.schlag_collection[selected_schlag]

        schlag_name = schlag_data["Schlag"]
        crop_name_vj = schlag_data["Vorjahreskultur"]
        zwischen_name = schlag_data["Zwischenfrucht"]

        saved_crop = schlag_data.get("Kultur")

        crop_index = (
            kulturen.index(saved_crop)
            if saved_crop in kulturen
            else None
        )

        crop_name = st.selectbox(
            "Current Crop for Nitrogen Requirement Calculation",
            options=kulturen,
            index=crop_index,
            placeholder="Select a crop",
            key=f"kultur_dbe_{selected_schlag}",
        )

        if crop_name is not None:
            schlag_data["Kultur"] = crop_name

            seed_date = st.date_input(
                f"Sowing Date for {crop_name}",
                key=f"seed_date_{selected_schlag}",
            )

            schlag_data["Datum der Aussaat"] = (
                seed_date.strftime("%d.%m.%Y")
            )

        if zwischen_name != "Keine":
            zwischen_date = st.date_input(
                f"Sowing Date for {zwischen_name}",
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
                f"A nitrogen requirement calculation already exists "
                f"for parcel {selected_schlag}!"
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "Recalculate",
                    key=f"recalc_button_{selected_schlag}",
                ):
                    st.session_state[recalc_key] = True
                    st.rerun()

            with c2:
                show_data = st.button(
                    "Show Parcel Data",
                    key=f"show_data_{selected_schlag}",
                )

            if show_data:
                st.write(schlag_data)

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
            st.markdown("### Soil Data")
            st.caption(
                "Information about the current condition of the parcel."
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                N_min = st.number_input(
                    f"Nmin / Reference Value · {schlag_name} (kg N/ha)",
                    min_value=0.0,
                    step=1.0,
                    key=f"N_min_{selected_schlag}",
                )

            with c2:
                humus = st.number_input(
                    "Humus Content (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key=f"humus_{selected_schlag}",
                ) / 100

            with c3:
                N_prev = st.number_input(
                    f"Previous Year's Fertilization: {crop_name_vj}",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    help=(
                        "Total nitrogen applied in organic and "
                        "organomineral fertilizers during the previous "
                        "year (kg N/ha)."
                    ),
                    key=f"N_prev_{selected_schlag}",
                )

            st.divider()
            st.markdown("### Yield Data")
            st.caption(
                f"Yield information for the current crop: {crop_name}"
            )

            Yield_5yr_mean = st.number_input(
                "Average Yield over the Last 5 Years (dt/ha)",
                min_value=0.0,
                step=1.0,
                key=f"yield_5yr_{selected_schlag}",
            )

            st.divider()
            st.markdown("### Crop Rotation")
            st.caption(
                "Nitrogen adjustments based on previous crops."
            )

            c1, c2 = st.columns(2)

            with c1:
                N_vor = st.number_input(
                    f"Deduction · Previous Year's Crop: {crop_name_vj} (kg N/ha)",
                    min_value=0.0,
                    step=1.0,
                    key=f"N_vor_{selected_schlag}",
                )

            with c2:
                if zwischen_name != "Keine":
                    N_zw = st.number_input(
                        f"Deduction · Catch Crop: {zwischen_name} (kg N/ha)",
                        min_value=0.0,
                        step=1.0,
                        key=f"N_zw_{selected_schlag}",
                    )
                else:
                    N_zw = 0.0
                    st.text_input(
                        "Catch Crop",
                        value="None",
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
                "Calculate Nitrogen Requirement",
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

            st.success(
                "Nitrogen requirement calculated and saved successfully."
            )
            st.rerun()

    if (
        selected_schlag is not None
        and "Stickstoffbedarf durch Dünger in kg / ha" in schlag_data
    ):
        st.divider()
        st.subheader(
            "Nitrogen Fertilizer Requirement Result"
        )

        st.metric(
            label=f"Calculated Nitrogen Requirement · {selected_schlag}",
            value=(
                f"{schlag_data['Stickstoffbedarf durch Dünger in kg / ha']:.2f} "
                "kg N/ha"
            ),
        )

        st.info(
            f"The calculated nitrogen requirement for parcel "
            f"**{selected_schlag}** is "
            f"**{schlag_data['Stickstoffbedarf durch Dünger in kg / ha']:.2f} kg N/ha**."
        )


# --------------------------------------------------
# FERTILIZATION DOCUMENTATION
# --------------------------------------------------

with tab3:
    st.markdown("## Nitrogen Fertilization Records")

    st.info(
        "Recording individual fertilization events "
        "will be implemented in the next step."
    )

    # Only show parcels with a completed nitrogen requirement calculation.
    dbe_schlaege = {
        s_id: parcel
        for s_id, parcel in st.session_state.schlag_collection.items()
        if parcel.get("Stickstoffbedarf durch Dünger in kg / ha")
        is not None
    }

    if not dbe_schlaege:
        st.info(
            "No parcel has a calculated nitrogen requirement yet. "
            "Please calculate the nitrogen requirement in the "
            '"Nitrogen Requirement" tab first. '
            "Fertilization records can only be entered afterwards."
        )

    else:
        selected_schlag = st.selectbox(
            label="Select Parcel",
            options=list(dbe_schlaege.keys()),
            format_func=lambda s_id: (
                f"{dbe_schlaege[s_id].get('Schlag', 'Unnamed Parcel')} "
                f"({s_id})"
            ),
            key="selected_schlag_duev_doc",
        )

        # Preserve existing fertilizer entries.
        if selected_schlag not in st.session_state.fert_collection:
            st.session_state.fert_collection[selected_schlag] = {}

        cc1, cc2 = st.columns(2)

        with cc1:
            if st.button(
                "Add Fertilization Event",
                key="add_fertilizer_event",
            ):
                st.session_state.fert_count += 1

        with cc2:
            if st.button(
                "Remove Fertilization Event",
                key="remove_fertilizer_event",
            ):
                if st.session_state.fert_count > 0:
                    st.session_state.fert_count -= 1

        for i in range(st.session_state.fert_count):
            d_id = f"{selected_schlag}_DG_{i + 1}"

            c1, c2, c3 = st.columns(3)

            with c1:
                date_fert = st.date_input(
                    "Fertilization Date",
                    key=f"date_fert_{selected_schlag}_{i}",
                )

            with c2:
                type_fert = st.selectbox(
                    label="Fertilizer Type",
                    options=FERTILZER_VALUES.keys(),
                    key=f"type_fert_{selected_schlag}_{i}",
                )

            unit_fert = FERTILZER_VALUES[type_fert]["einheit"]

            with c3:
                amt_fert = st.number_input(
                    f"Amount Applied ({unit_fert})",
                    min_value=0.0,
                    key=f"amt_fert_{selected_schlag}_{i}",
                )

            if date_fert and type_fert and unit_fert and amt_fert > 0:
                st.session_state.fert_collection[
                    selected_schlag
                ][d_id] = {
                    "Datum": date_fert,
                    "Düngetyp": type_fert,
                    "Einheit": unit_fert,
                    f"Düngemente in {unit_fert} / ha": amt_fert,
                    f"Stickstoff Gesamt in {unit_fert} / ha": (
                        amt_fert
                        * FERTILZER_VALUES[type_fert]["Nges pro Einheit"]
                    ),
                    f"Stickstoff Pflanzenverfügbar in {unit_fert} / ha": (
                        amt_fert
                        * FERTILZER_VALUES[type_fert]["Npfluer pro Einheit"]
                    ),
                }

        st.session_state.schlag_collection[
            selected_schlag
        ]["Düngeinformation"] = st.session_state.fert_collection[
            selected_schlag
        ]

        # st.write(
        #     st.session_state.schlag_collection[selected_schlag]
        # )