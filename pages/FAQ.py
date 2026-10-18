import streamlit as st

st.set_page_config(page_title="FAQ", layout="wide")

st.logo(".streamlit/logo.png", size="large")

st.title("Frequently Asked Questions (FAQ) – SMK Fertilizer Requirement Assessment (DBE)")

# 1. Legal Framework and Practical Aspects of the DBE

st.header("1. Legal Framework and Practical Aspects of the Fertilizer Requirement Assessment (DBE)")

with st.expander("What is the fertilizer requirement assessment (DBE), and why do I need to carry it out?"):
    st.markdown("""
    The fertilizer requirement assessment is the legally required calculation of how much nitrogen fertilizer your crops actually need on a particular field. Before you begin fertilizing, you must determine and document this requirement to comply with the applicable legal regulations.
    """)

with st.expander("Do I need to calculate fertilizer requirements for my entire farm at once, or separately for each field?"):
    st.markdown("""
    You must prepare a DBE separately for each field or management unit. Each field has its own area, previous-year crops, specific soil analysis results, and different average yields.
    """)

with st.expander("What specific information do I need to complete a DBE for a field?"):
    st.markdown("""
    Much of this information may already be available on your farm, for example in the form of soil analyses. To complete a nitrogen fertilizer requirement assessment, such as one based on the requirements of the North Rhine-Westphalia Chamber of Agriculture, you need the following information:

    - **Field information:** The name of the field or management unit, the field block number, and the field area in hectares.
    - **Crop and crop rotation:** The planned main crop (e.g. winter wheat), the previous year's crop, and any catch crops.
    - **Yield level:** Your farm's average yield over the past five years compared with the yield specified in the German Fertilizer Ordinance (DüV), in order to calculate any additions or deductions based on the yield difference.
    - **Soil values:** Soil analysis results, as well as information about the location and humus content, where relevant for the applicable deductions.
    - **Nutrient carryover from the previous year:** Information about organic fertilizer applications in the previous year, as a corresponding deduction must be taken into account.
    """)

with st.expander("What is the difference between the fertilizer requirement assessment (DBE) and fertilization records?"):
    st.markdown("""
    - **Before fertilizing (requirement assessment):** You calculate the maximum permitted nitrogen fertilizer requirement in kilograms per hectare, based on the nitrogen requirement value and the legally prescribed additions and deductions.
    - **After fertilizing (documentation):** Once you have applied fertilizer, you record the exact date, the fertilizer used (e.g. dairy cattle slurry), the quantity applied, and the amount of nitrogen applied per hectare and across the field.
    """)

# 2. Using the SMK DBE Calculator

st.header("2. Using the SMK DBE Calculator in Everyday Farm Operations")

with st.expander("Why should I switch from pen and paper or Excel spreadsheets to SMK?"):
    st.markdown("""
    Currently, 51% of farms still use paper for documentation, while 57% rely on spreadsheets or scanned documents. This results in manual processes, duplicate forms, and wasted time that could otherwise be spent on farming. SMK provides an integrated workflow: you enter your farm data just once, reuse it when needed, and generate the required documentation.
    """)

with st.expander("I'm not an IT expert—is the program difficult to use?"):
    st.markdown("""
    No. Many farmers want a straightforward application without a steep learning curve. Our platform brings your fertilizer documentation together in a single, intuitive dashboard. This can also help you save on expensive external consulting services, which 78% of farms currently rely on.
    """)

with st.expander("Can I reuse my existing farm data?"):
    st.markdown("""
    Yes. Many farms currently use separate systems that do not communicate with one another. Our approach is based on a shared platform for all your data, together with interoperability with existing open-source platforms, so that information you already have, such as soil analysis results, can be used directly.
    """)

# 3. Costs, Data Protection, and Open Source

st.header("3. Costs, Data Protection, and Open Source")

with st.expander("How much does the SMK DBE calculator cost? Are there any hidden subscription fees?"):
    st.markdown("""
    The software is completely free and has no expensive license fees. We believe that digitalization in agriculture should not come with a high price tag or make you dependent on a single provider (vendor lock-in). To keep the tool permanently free for farmers, we rely on funding programs, such as NOSTRADAMUS or the BMDS funding program, as well as accompanying training sessions and workshops.
    """)

with st.expander("What does 'open source' mean for me as a farmer?"):
    st.markdown("""
    Open source means that the source code of our software is publicly available for inspection. This offers two key advantages:

    - **Adaptability:** The publicly available source code can be modified to meet individual requirements.
    - **Independence:** You get a powerful tool without high software costs or dependence on a particular vendor.
    """)

with st.expander("What happens to my sensitive farm and soil data?"):
    st.markdown("""
    We understand that many farmers have serious concerns about data security and want to keep their farm data private. Our solution aligns with EU objectives and puts your digital sovereignty at the center. Because the source code is open, how your data is processed can be transparently inspected.
    """)
