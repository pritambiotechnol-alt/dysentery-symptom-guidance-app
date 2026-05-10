from openai import OpenAI

def get_openai_client():
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        return None

import streamlit as st

st.set_page_config(
    page_title="Dysentery Symptom Guidance App",
    page_icon="🧫",
    layout="centered"
)

st.title("🧫 Dysentery Symptom Guidance App")

st.warning(
    "This app is for education and research only. "
    "It does not diagnose disease or prescribe medicine."
)

st.header("Enter symptoms")

age_group = st.selectbox("Age group", ["Adult", "Child", "Elderly"])

duration_days = st.number_input(
    "Duration of diarrhoea in days",
    min_value=0,
    max_value=30,
    value=1
)

stools_per_day = st.number_input(
    "Number of stools per day",
    min_value=0,
    max_value=50,
    value=3
)

blood = st.radio("Blood in stool?", ["No", "Yes"], horizontal=True)
mucus = st.radio("Mucus in stool?", ["No", "Yes"], horizontal=True)
fever = st.radio("Fever?", ["No", "Yes"], horizontal=True)
vomiting = st.radio("Vomiting?", ["No", "Yes"], horizontal=True)
dehydration = st.radio("Signs of dehydration?", ["No", "Yes"], horizontal=True)

abdominal_pain = st.selectbox(
    "Abdominal pain/cramps",
    ["None", "Mild", "Moderate", "Severe"]
)

stool_test = st.selectbox(
    "Known stool test result",
    ["Unknown", "Shigella", "Entamoeba histolytica", "Salmonella", "Other"]
)

if st.button("Analyse symptoms"):

    red_flags = []

    if dehydration == "Yes":
        red_flags.append("Signs of dehydration")
    if blood == "Yes" and fever == "Yes":
        red_flags.append("Blood in stool with fever")
    if vomiting == "Yes" and stools_per_day >= 6:
        red_flags.append("Frequent stool with vomiting")
    if age_group in ["Child", "Elderly"]:
        red_flags.append(f"High-risk age group: {age_group}")
    if abdominal_pain == "Severe":
        red_flags.append("Severe abdominal pain")

    if stool_test == "Shigella":
        probable_type = "Probable bacillary dysentery / shigellosis"
    elif stool_test == "Entamoeba histolytica":
        probable_type = "Probable amoebic dysentery / amoebiasis"
    elif stool_test == "Salmonella":
        probable_type = "Other infectious bloody diarrhoea"
    elif blood == "Yes" and fever == "Yes":
        probable_type = "Probable bacillary dysentery-like illness"
    elif blood == "Yes" and mucus == "Yes":
        probable_type = "Possible amoebic or other dysentery-like illness"
    elif blood == "Yes":
        probable_type = "Bloody diarrhoea requiring stool testing"
    else:
        probable_type = "Unclassified diarrhoeal illness"

def generate_ai_explanation(probable_type, red_flags, blood, mucus, fever, vomiting, dehydration, abdominal_pain):
    client = get_openai_client()

    if client is None:
        return "AI explanation is unavailable because the OpenAI API key is not configured."

    prompt = f"""
You are an educational medical assistant.

Important rules:
- Do not diagnose.
- Do not prescribe medicines.
- Do not suggest antibiotic names or doses.
- Recommend medical review for red flags.
- Emphasize ORS, hydration, stool testing, and clinician consultation.

Patient symptom summary:
Blood in stool: {blood}
Mucus in stool: {mucus}
Fever: {fever}
Vomiting: {vomiting}
Dehydration: {dehydration}
Abdominal pain: {abdominal_pain}

Rule-based app result:
Probable category: {probable_type}
Detected red flags: {", ".join(red_flags) if red_flags else "None"}

Write a short patient-friendly explanation in 120–180 words.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text
    
    st.header("Result")

    st.subheader("Probable category")
    st.info(probable_type)

    if red_flags:
        st.subheader("Risk level")
        st.error("Medical review is recommended.")
        st.subheader("Detected warning signs")
        for item in red_flags:
            st.write(f"- {item}")
    elif blood == "Yes":
        st.warning("Moderate risk: stool testing and medical review are recommended.")
    else:
        st.success("Lower risk, but symptoms should be monitored.")

    st.subheader("Immediate supportive guidance")
    st.write(
        "Use oral rehydration solution (ORS), take adequate fluids, rest, "
        "and monitor for dehydration."
    )

    st.subheader("Medical review guidance")
    st.write(
        "Consult a registered medical practitioner for diagnosis, stool testing, "
        "and treatment decisions."
    )

    st.subheader("Caution")
    st.warning(
        "Do not self-medicate with antibiotics or gut-slowing medicines such as "
        "loperamide in bloody diarrhoea unless advised by a doctor."
    )

st.caption(
    "Educational prototype only. Not for emergency diagnosis or prescription."
)
