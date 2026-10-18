import streamlit as st

st.set_page_config(page_title="FAQ - Easy", layout="wide")

st.logo(".streamlit/logo.png", size="large")

st.title("Frequently Asked Questions about the SMK Fertilizer Calculator (DBE)")

# 1. Rules and Practical Aspects of Fertilizer Requirement Calculations

st.header("1. Rules and Practical Aspects of Fertilizer Requirement Calculations")

with st.expander("What is the fertilizer requirement assessment (DBE), and why do I need to do it?"):
    st.markdown("""
    The law requires you to calculate in advance exactly how much fertilizer your crops actually need. This is called a fertilizer requirement assessment (Düngebedarfsermittlung, or DBE for short). You must calculate and document this before applying fertilizer to your fields. This helps you comply with legal requirements and avoid penalties.
    """)

with st.expander("Do I need to calculate fertilizer requirements for the entire farm at once, or separately for each field?"):
    st.markdown("""
    You must calculate the requirements for each individual field (called a *Schlag* in German). Every field is different: it may have a different size and soil type, and different crops may have been grown there in the previous year.
    """)

with st.expander("What information do I need to complete a DBE for a field?"):
    st.markdown("""
    You probably already have much of the required information, for example from previous soil analyses. You will need the following details:

    - **Field information:** What is the field called, what is its identification number, and how large is it?
    - **Crops:** What do you plan to grow there (for example, wheat)? And what was grown there last year?
    - **Yield:** What was the average yield from this field over the past five years?
    - **Soil values:** What do your soil analyses show? What is the humus content?
    - **Previous fertilizer applications:** Did you apply organic fertilizer (such as slurry) to the field last year? This must be taken into account in the new calculation.
    """)

with st.expander("What is the difference between the assessment (DBE) and fertilization records?"):
    st.markdown("""
    - **Before fertilizing (assessment):** You calculate the maximum amount of fertilizer that may be applied to the field.
    - **After fertilizing (documentation):** You record exactly what you applied. You note the date, fertilizer type, quantity, and the total amount of nitrogen applied to the field.
    """)

# 2. Using the SMK Program in Everyday Farm Operations

st.header("2. Using the SMK Program in Everyday Farm Operations")

with st.expander("Why should I switch from pen and paper or Excel to SMK?"):
    st.markdown("""
    Many farms still use paper records or simple spreadsheets for these tasks. This creates extra work: information has to be entered more than once, and valuable time is lost. SMK makes the process easier. You enter your data just once. The program saves your information, performs the calculations, and automatically generates the completed document for you.
    """)

with st.expander("I'm not very good with computers. Is the program complicated?"):
    st.markdown("""
    No, it is designed to be easy to use. We know that many farmers want straightforward solutions without unnecessary complexity. All the essential functions are collected in one clear, easy-to-navigate interface. No prior technical knowledge is required. This can also help you reduce your reliance on expensive external consultants, whom many farms currently turn to for support.
    """)

with st.expander("Can I reuse data I already have?"):
    st.markdown("""
    Yes. Different programs used on farms often do not work well together. SMK aims to make this easier. If you already have data, such as a soil analysis, in another program, SMK can import that information where a compatible import option is available. This helps you avoid entering the same information twice.
    """)

# 3. Costs, Data Protection, and Open Technology

st.header("3. Costs, Data Protection, and Open-Source Technology")

with st.expander("How much does SMK cost? Are there any hidden fees?"):
    st.markdown("""
    The program is free to use. There are no expensive licenses or subscription contracts. We believe that good technology should be accessible to farmers, without making them dependent on a single large software company. Our work is funded through public grants and voluntary training sessions that we offer.
    """)

with st.expander("What does 'open source' mean for me as a farmer?"):
    st.markdown("""
    "Open source" means that the program's source code is publicly available. This allows qualified developers to inspect how the software works. There are two main advantages for you:

    - **Easy to adapt:** The program can be modified to meet the specific needs of your farm.
    - **Independence:** You get a useful tool for your farm without having to pay large software companies for access.
    """)

with st.expander("What happens to my farm's private data?"):
    st.markdown("""
    We know that your farm data is valuable and should not be shared without your permission. Your data belongs to you. Because the program is open source, its code can be inspected for transparency. However, open-source software alone does not guarantee that data is stored securely or never transmitted online. How your data is handled also depends on how the program is hosted and configured.
    """)
