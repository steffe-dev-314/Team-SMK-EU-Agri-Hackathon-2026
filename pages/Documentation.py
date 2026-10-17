
import streamlit as st
from form_to_csv import build_dbe_excel, get_finished_parcels
from datetime import datetime


st.markdown("## Zusammenfassung und Export")

if not "schlag_collection" in st.session_state or not st.session_state.schlag_collection:
    st.info("Bitte zunächst Schläge eintragen.")

else:
    if not get_finished_parcels(st.session_state.schlag_collection):
        st.error(
            "Der Excel-Bericht kann nicht erstellt werden: "
            "Für keinen Schlag liegen sowohl eine berechnete DBE "
            "als auch eine Düngedokumentation vor. "
            "Bitte vervollständige zunächst die DBE und erfasse "
            "die zugehörigen Düngungsdaten."
        )

    else:
        st.markdown(
            "Erstelle einen formatierten Excel-Bericht "
            "mit DBE-Ergebnissen und Berechnungsdetails."
        )

        finished_parcels = get_finished_parcels(
            st.session_state.schlag_collection
        )

        metadata = [
            ("Betrieb", st.session_state.farm_metadata.get("betrieb", "")),
            ("Betriebsnummer", st.session_state.farm_metadata.get("betriebsnr", "")),
            ("Düngejahr", st.session_state.farm_metadata.get("duengejahr", "")),
            ("Erstellt am", datetime.now()),
        ]

        if len(finished_parcels) != len(st.session_state.schlag_collection):
            omitted_count = (
                len(st.session_state.schlag_collection)
                - len(finished_parcels)
            )

            st.warning(
                f"Der Excel-Bericht enthält nur "
                f"{len(finished_parcels)} von "
                f"{len(st.session_state.schlag_collection)} "
                f"erfassten Schlägen. "
                f"{omitted_count} "
                f"{'Schlag wird' if omitted_count == 1 else 'Schläge werden'} "
                "nicht berücksichtigt, da dafür noch keine vollständige "
                "DBE und Düngedokumentation vorliegt."
            )

            st.info("Excel wird nur für folgende Schläge erstellt:")

            for p in finished_parcels:
                st.info(
                    f"{p} : "
                    f"{st.session_state.schlag_collection[p]['Schlag']}"
                )

        finished_schlaege = {
            s_id: s
            for s_id, s in st.session_state.schlag_collection.items()
            if s_id in finished_parcels
        }

        excel_data = build_dbe_excel(
            schlag_collection=finished_schlaege,
            metadata=metadata,
        )

        st.download_button(
            label="Excel-Bericht herunterladen",
            data=excel_data,
            file_name=(
                f"DBE_Bericht_"
                f"{datetime.now():%Y%m%d_%H%M}.xlsx"
            ),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            type="primary",
            use_container_width=True,
        )
