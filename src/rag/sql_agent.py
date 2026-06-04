import os
import re

import pandas as pd
import requests
from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://meduser:medpassword@localhost:5432/medimageops",
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


SCHEMA_DESCRIPTION = """
Table: dicom_metadata

Columns:
- file_path
- patient_id
- modality
- study_date
- manufacturer
- body_part
- study_description
- series_description
- hospital
"""


BLOCKED_SQL_WORDS = [
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "grant",
    "revoke",
]


def call_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()
    return response.json()["response"].strip()


def rule_based_sql(question):
    q = question.lower()

    if "how many" in q and "ct" in q and "chest" in q:
        return """
        SELECT COUNT(*) AS record_count
        FROM dicom_metadata
        WHERE modality = 'CT'
          AND body_part = 'CHEST';
        """

    if "how many" in q and "ct" in q:
        return """
        SELECT COUNT(*) AS record_count
        FROM dicom_metadata
        WHERE modality = 'CT';
        """

    if "how many" in q and "mr" in q:
        return """
        SELECT COUNT(*) AS record_count
        FROM dicom_metadata
        WHERE modality = 'MR';
        """

    if "how many" in q and "x-ray" in q:
        return """
        SELECT COUNT(*) AS record_count
        FROM dicom_metadata
        WHERE modality = 'XR';
        """

    if "how many" in q and "ultrasound" in q:
        return """
        SELECT COUNT(*) AS record_count
        FROM dicom_metadata
        WHERE modality = 'US';
        """

    if "which hospital" in q and ("most" in q or "highest" in q or "top" in q):
        return """
        SELECT hospital,
               COUNT(*) AS record_count
        FROM dicom_metadata
        GROUP BY hospital
        ORDER BY record_count DESC
        LIMIT 1;
        """

    if "which manufacturer" in q and ("most" in q or "highest" in q or "top" in q):
        return """
        SELECT manufacturer,
               COUNT(*) AS record_count
        FROM dicom_metadata
        GROUP BY manufacturer
        ORDER BY record_count DESC
        LIMIT 1;
        """

    if "which body part" in q and ("most" in q or "highest" in q or "top" in q):
        return """
        SELECT body_part,
               COUNT(*) AS record_count
        FROM dicom_metadata
        GROUP BY body_part
        ORDER BY record_count DESC
        LIMIT 1;
        """

    if "modality distribution" in q or "modalities" in q:
        return """
        SELECT modality,
               COUNT(*) AS record_count
        FROM dicom_metadata
        GROUP BY modality
        ORDER BY record_count DESC;
        """

    if "hospital distribution" in q or "by hospital" in q:
        return """
        SELECT hospital,
               COUNT(*) AS record_count
        FROM dicom_metadata
        GROUP BY hospital
        ORDER BY record_count DESC;
        """

    return None


def clean_sql(sql):
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    matches = re.findall(
        r"select[\s\S]*?(?:;|$)",
        sql,
        flags=re.IGNORECASE,
    )

    if len(matches) == 0:
        raise ValueError(f"No SELECT query found: {sql}")

    if len(matches) > 1:
        raise ValueError(f"Multiple SELECT queries generated. Refusing to execute: {sql}")

    cleaned_sql = matches[0].strip()

    if not cleaned_sql.endswith(";"):
        cleaned_sql += ";"

    return cleaned_sql


def validate_sql(sql):
    lowered = sql.lower().strip()

    if not lowered.startswith("select"):
        raise ValueError(f"Only SELECT queries are allowed. Generated SQL: {sql}")

    if lowered.count("select") > 1:
        raise ValueError(f"Multiple SELECT statements are not allowed: {sql}")

    for word in BLOCKED_SQL_WORDS:
        if word in lowered:
            raise ValueError(f"Unsafe SQL detected: {word}")

    return True


def generate_sql_with_llm(question):
    prompt = f"""
You are a PostgreSQL SQL expert.

Database schema:

{SCHEMA_DESCRIPTION}

Rules:
1. Generate ONLY ONE SQL SELECT query.
2. Do not generate multiple queries.
3. Do not include markdown.
4. Do not explain the query.
5. Table name is dicom_metadata.
6. For ranking questions, include COUNT(*) AS record_count.
7. For "CT", use modality = 'CT'.
8. For "MR" or "MRI", use modality = 'MR'.
9. For "X-Ray", use modality = 'XR'.
10. For "Ultrasound", use modality = 'US'.

Question:
{question}

SQL:
"""

    raw_sql = call_ollama(prompt)
    sql = clean_sql(raw_sql)
    validate_sql(sql)

    return sql


def generate_sql(question):
    sql = rule_based_sql(question)

    if sql is None:
        sql = generate_sql_with_llm(question)

    sql = clean_sql(sql)
    validate_sql(sql)

    return sql


def run_sql(sql):
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        result = connection.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()

    return pd.DataFrame(rows, columns=columns)


def generate_final_answer(question, sql, result_df):
    result_text = result_df.to_string(index=False)

    prompt = f"""
You are a healthcare analytics assistant.

Question:
{question}

SQL:
{sql}

Result:
{result_text}

Answer the question in plain English.
Mention exact counts when available.
Be concise.
Do not add assumptions.
"""

    return call_ollama(prompt)


def answer_sql_question(question):
    sql = generate_sql(question)
    result_df = run_sql(sql)
    answer = generate_final_answer(question, sql, result_df)

    return {
        "question": question,
        "sql": sql,
        "result": result_df,
        "answer": answer,
    }


def main():
    test_questions = [
        "Which hospital has the most studies?",
        "How many CT scans exist?",
        "How many chest CT scans are there?",
        "Which manufacturer appears most often?",
    ]

    for question in test_questions:
        response = answer_sql_question(question)

        print("\n" + "=" * 80)
        print("Question:")
        print(response["question"])

        print("\nGenerated SQL:")
        print(response["sql"])

        print("\nSQL Result:")
        print(response["result"])

        print("\nAnswer:")
        print(response["answer"])


if __name__ == "__main__":
    main()