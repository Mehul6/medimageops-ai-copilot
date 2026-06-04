import os
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

from src.rag.question_router import route_question
from src.rag.rag_answer import answer_question
from src.rag.sql_agent import answer_sql_question


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://meduser:medpassword@localhost:5432/medimageops",
)

QUALITY_REPORT_PATH = Path("data/reports/quality_report.csv")


st.set_page_config(
    page_title="MedImageOps AI Copilot",
    layout="wide",
)

st.title("MedImageOps: Medical Imaging AI Data Copilot")

engine = create_engine(DATABASE_URL)
df = pd.read_sql("SELECT * FROM dicom_metadata", engine)

st.sidebar.header("Filters")

modalities = ["All"] + sorted(df["modality"].dropna().unique().tolist())
selected_modality = st.sidebar.selectbox("Modality", modalities)

body_parts = ["All"] + sorted(df["body_part"].dropna().unique().tolist())
selected_body_part = st.sidebar.selectbox("Body Part", body_parts)

manufacturers = ["All"] + sorted(df["manufacturer"].dropna().unique().tolist())
selected_manufacturer = st.sidebar.selectbox("Manufacturer", manufacturers)

hospitals = ["All"] + sorted(df["hospital"].dropna().unique().tolist())
selected_hospital = st.sidebar.selectbox("Hospital", hospitals)

filtered_df = df.copy()

if selected_modality != "All":
    filtered_df = filtered_df[filtered_df["modality"] == selected_modality]

if selected_body_part != "All":
    filtered_df = filtered_df[filtered_df["body_part"] == selected_body_part]

if selected_manufacturer != "All":
    filtered_df = filtered_df[filtered_df["manufacturer"] == selected_manufacturer]

if selected_hospital != "All":
    filtered_df = filtered_df[filtered_df["hospital"] == selected_hospital]


total_scans = len(filtered_df)
unique_patients = filtered_df["patient_id"].nunique()
unique_modalities = filtered_df["modality"].nunique()
missing_patient_ids = filtered_df["patient_id"].isna().sum()

top_manufacturer = (
    filtered_df["manufacturer"].mode().iloc[0]
    if not filtered_df.empty and not filtered_df["manufacturer"].dropna().empty
    else "N/A"
)

top_body_part = (
    filtered_df["body_part"].mode().iloc[0]
    if not filtered_df.empty and not filtered_df["body_part"].dropna().empty
    else "N/A"
)

top_hospital = (
    filtered_df["hospital"].mode().iloc[0]
    if not filtered_df.empty and not filtered_df["hospital"].dropna().empty
    else "N/A"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Scans", total_scans)
col2.metric("Unique Patients", unique_patients)
col3.metric("Modalities", unique_modalities)
col4.metric("Missing Patient IDs", missing_patient_ids)

col5, col6, col7 = st.columns(3)

col5.metric("Top Manufacturer", top_manufacturer)
col6.metric("Top Body Part", top_body_part)
col7.metric("Top Hospital", top_hospital)

st.divider()

st.subheader("Unified AI Copilot")

st.caption(
    "Ask one question. The router automatically chooses SQL Agent for analytics questions "
    "or RAG Assistant for metadata/context questions."
)

example_questions = [
    "Which hospital has the most studies?",
    "How many CT scans exist?",
    "How many chest CT scans are there?",
    "Which manufacturer appears most often?",
    "What body part was scanned?",
    "Summarize the retrieved imaging metadata.",
]

selected_question = st.selectbox(
    "Example questions",
    [""] + example_questions,
)

user_question = st.text_input(
    "Ask MedImageOps Copilot",
    value=selected_question,
    placeholder="Example: Which hospital has the most studies?",
)

if st.button("Ask Copilot"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        route = route_question(user_question)

        st.info(f"Router selected: {route.upper()}")

        if route == "sql":
            with st.spinner("Generating SQL, querying PostgreSQL, and answering..."):
                response = answer_sql_question(user_question)

            st.markdown("### Answer")
            st.write(response["answer"])

            with st.expander("Generated SQL"):
                st.code(response["sql"], language="sql")

            with st.expander("SQL Result"):
                st.dataframe(response["result"], use_container_width=True)

        else:
            with st.spinner("Retrieving context and generating grounded answer..."):
                response = answer_question(user_question)

            st.markdown("### Answer")
            st.write(response["answer"])

            with st.expander("Retrieved Context"):
                st.write(response["context"])

            with st.expander("Sources"):
                sources_df = pd.DataFrame(response["sources"])
                st.dataframe(sources_df, use_container_width=True)

st.divider()

st.subheader("Modality Distribution")
st.bar_chart(filtered_df["modality"].value_counts())

st.subheader("Body Part Distribution")
st.bar_chart(filtered_df["body_part"].fillna("Unknown").value_counts())

st.subheader("Manufacturer Distribution")
st.bar_chart(filtered_df["manufacturer"].fillna("Unknown").value_counts())

st.subheader("Hospital Distribution")
st.bar_chart(filtered_df["hospital"].fillna("Unknown").value_counts())

st.subheader("Study Description Distribution")
st.bar_chart(filtered_df["study_description"].fillna("Unknown").value_counts())

st.subheader("Automated Quality Report")

if QUALITY_REPORT_PATH.exists():
    quality_report = pd.read_csv(QUALITY_REPORT_PATH)
    st.dataframe(quality_report, use_container_width=True)
else:
    st.warning("Quality report not found. Run the Airflow DAG first.")

st.subheader("Scan Metadata Table")
st.dataframe(filtered_df, use_container_width=True)