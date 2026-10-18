import streamlit as st
from form_to_csv import build_dbe_excel, get_finished_parcels
from datetime import datetime


st.markdown("## Summary and Export")

if (
    "schlag_collection" not in st.session_state
    or not st.session_state.schlag_collection
):
    st.info("Please add parcels first.")

else:
    if not get_finished_parcels(st.session_state.schlag_collection):
        st.error(
            "The Excel report cannot be generated: "
            "No parcel has both a completed nitrogen requirement "
            "calculation and fertilization records. "
            "Please complete the nitrogen requirement calculation "
            "and enter the corresponding fertilization data first."
        )

    else:
        st.markdown(
            "Generate a formatted Excel report "
            "containing nitrogen requirement results and calculation details."
        )

        finished_parcels = get_finished_parcels(
            st.session_state.schlag_collection
        )

        metadata = [
            ("Farm Name", st.session_state.farm_metadata.get("betrieb", "")),
            ("Farm Registration Number", st.session_state.farm_metadata.get("betriebsnr", "")),
            ("Fertilization Year", st.session_state.farm_metadata.get("duengejahr", "")),
            ("Generated On", datetime.now()),
        ]

        if len(finished_parcels) != len(st.session_state.schlag_collection):
            omitted_count = (
                len(st.session_state.schlag_collection)
                - len(finished_parcels)
            )

            st.warning(
                f"The Excel report includes only "
                f"{len(finished_parcels)} of "
                f"{len(st.session_state.schlag_collection)} "
                f"registered parcels. "
                f"{omitted_count} "
                f"{'parcel has' if omitted_count == 1 else 'parcels have'} "
                "been excluded because the required nitrogen requirement "
                "calculation and fertilization records are not yet complete."
            )

            st.info("The Excel report will be generated only for the following parcels:")

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
            label="Download Excel Report",
            data=excel_data,
            file_name=(
                f"DBE_Report_"
                f"{datetime.now():%Y%m%d_%H%M}.xlsx"
            ),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            type="primary",
            use_container_width=True,
        )