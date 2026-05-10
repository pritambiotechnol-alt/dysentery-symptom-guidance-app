import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Dysentery Symptom Guidance App",
    page_icon="🧫",
    layout="centered"
)

st.title("🧫 Dysentery Symptom Guidance App")

st.warning(
    "This app is for education and research only. "
    "It does not diagnose disease or prescribe medicine. "
    "Consult a registered medical practitioner for diagnosis and treatment."
)


def get_openai_client():
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        return None


def classify_case(
    age_group,
    duration_days,
    stools_per_day,
    blood,
    mucus,
    fever,
    vomiting,
    dehydration,
    abdominal_pain,
    stool_test
):
    red_flags = []

    if dehydration == "Yes":
        red_flags.append("Signs of dehydration")

    if blood == "Yes" and fever == "Yes":
        red_flags.append("Blood in stool with fever")

    if vomiting == "Yes" and stools_per_day >= 6:
        red_flags.append("Frequent stools with vomiting")

    if duration_days >= 3 and blood == "Yes":
        red_flags.append("Bloody diarrhoea persisting for 3 days or more")

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

    if red_flags:
        risk_level = "High risk / medical review recommended"
    elif blood == "Yes":
        risk_level = "Moderate risk / stool testing and clinician review recommended"
    else:
        risk_level = "Lower risk, but symptoms should be monitored"

    return probable_type, risk_level, red_flags


def guidance_for_type(probable_type):
    if "bacillary" in probable_type or "shigellosis" in probable_type:
        return {
            "supportive": (
                "Use oral rehydration solution (ORS), take adequate fluids, rest, "
                "and monitor for dehydration."
            ),
            "medical": (
                "Antibiotics may be required in severe disease or high-risk patients, "
                "but treatment choice must be decided by a registered medical practitioner "
                "and should consider stool testing and local antimicrobial susceptibility."
            ),
            "caution": (
                "Avoid gut-slowing medicines such as loperamide in suspected shigellosis "
                "or bloody diarrhoea unless advised by a doctor."
            )
        }

    if "amoebic" in probable_type or "amoebiasis" in probable_type:
        return {
            "supportive": (
                "Use ORS and fluids to prevent dehydration."
            ),
            "medical": (
                "Amoebiasis requires clinician-directed anti-amoebic therapy after appropriate "
                "diagnostic evaluation. Do not self-medicate."
            ),
            "caution": (
                "Do not assume amoebiasis from symptoms alone. Stool testing or other diagnostic "
                "confirmation is important."
            )
        }

    if "bloody diarrhoea" in probable_type:
        return {
            "supportive": (
                "Use ORS and fluids immediately and monitor for dehydration."
            ),
            "medical": (
                "Bloody diarrhoea requires medical review and stool testing to identify the cause."
            ),
            "caution": (
                "Avoid self-medication with antibiotics or antimotility drugs."
            )
        }

    return {
        "supportive": (
            "Maintain hydration with ORS and fluids. Continue feeding as tolerated."
        ),
        "medical": (
            "Seek medical advice if symptoms worsen, persist, or if blood, fever, dehydration, "
            "or severe pain appears."
        ),
        "caution": (
            "This app cannot diagnose the exact cause of diarrhoea."
        )
    }


def generate_ai_explanation(
    probable_type,
    risk_level,
    red_flags,
    age_group,
    duration_days,
    stools_per_day,
    blood,
    mucus,
    fever,
    vomiting,
    dehydration,
    abdominal_pain,
    stool_test
):
    client = get_openai_client()

    if client is None:
        return (
            "AI explanation is unavailable because the OpenAI API key is not configured. "
            "Add OPENAI_API_KEY to Streamlit secrets."
        )

    prompt = f"""
You are an educational medical guidance assistant.

Very important safety rules:
- Do not diagnose the patient.
- Do not prescribe medicines.
- Do not suggest antibiotic names, anti-amoebic drug names, doses, or treatment duration.
- Do not say that medical care is unnecessary.
- Recommend medical review when red flags are present.
- Emphasize oral rehydration solution, hydration, stool testing, and clinician consultation.
- Use clear, simple, patient-friendly language.

Patient symptom summary:
Age group: {age_group}
Duration of diarrhoea: {duration_days} days
Number of stools per day: {stools_per_day}
Blood in stool: {blood}
Mucus in stool: {mucus}
Fever: {fever}
Vomiting: {vomiting}
Signs of dehydration: {dehydration}
Abdominal pain/cramps: {abdominal_pain}
Known stool test result: {stool_test}

Rule-based app result:
Probable category: {probable_type}
Risk level: {risk_level}
Detected red flags: {", ".join(red_flags) if red_flags else "None"}

Write a concise patient-friendly explanation in 120–180 words.
Include:
1. What the symptom pattern may suggest
2. Why hydration is important
3. Whether medical review is recommended
4. What warning signs need urgent care
5. A caution against self-medication
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return response.output_text

    except Exception as error:
        return f"AI explanation could not be generated. Error: {error}"


st.header("Enter symptoms")

age_group = st.selectbox(
    "Age group",
    ["Adult", "Child", "Elderly"]
)

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

blood = st.radio(
    "Blood in stool?",
    ["No", "Yes"],
    horizontal=True
)

mucus = st.radio(
    "Mucus in stool?",
    ["No", "Yes"],
    horizontal=True
)

fever = st.radio(
    "Fever?",
    ["No", "Yes"],
    horizontal=True
)

vomiting = st.radio(
    "Vomiting?",
    ["No", "Yes"],
    horizontal=True
)

dehydration = st.radio(
    "Signs of dehydration?",
    ["No", "Yes"],
    horizontal=True
)

abdominal_pain = st.selectbox(
    "Abdominal pain/cramps",
    ["None", "Mild", "Moderate", "Severe"]
)

stool_test = st.selectbox(
    "Known stool test result",
    ["Unknown", "Shigella", "Entamoeba histolytica", "Salmonella", "Other"]
)

if st.button("Analyse symptoms"):

    probable_type, risk_level, red_flags = classify_case(
        age_group=age_group,
        duration_days=duration_days,
        stools_per_day=stools_per_day,
        blood=blood,
        mucus=mucus,
        fever=fever,
        vomiting=vomiting,
        dehydration=dehydration,
        abdominal_pain=abdominal_pain,
        stool_test=stool_test
    )

    guidance = guidance_for_type(probable_type)

    st.header("Result")

    st.subheader("Probable category")
    st.info(probable_type)

    st.subheader("Risk level")
    if "High" in risk_level:
        st.error(risk_level)
    elif "Moderate" in risk_level:
        st.warning(risk_level)
    else:
        st.success(risk_level)

    if red_flags:
        st.subheader("Detected warning signs")
        for item in red_flags:
            st.write(f"- {item}")

    st.subheader("Immediate supportive guidance")
    st.write(guidance["supportive"])

    st.subheader("Medical review guidance")
    st.write(guidance["medical"])

    st.subheader("Caution")
    st.warning(guidance["caution"])

    st.subheader("Generative AI-assisted explanation")

    ai_text = generate_ai_explanation(
        probable_type=probable_type,
        risk_level=risk_level,
        red_flags=red_flags,
        age_group=age_group,
        duration_days=duration_days,
        stools_per_day=stools_per_day,
        blood=blood,
        mucus=mucus,
        fever=fever,
        vomiting=vomiting,
        dehydration=dehydration,
        abdominal_pain=abdominal_pain,
        stool_test=stool_test
    )

    st.write(ai_text)

st.divider()

st.caption(
    "Educational prototype only. This app does not provide diagnosis, prescription, "
    "or emergency medical care."
)
