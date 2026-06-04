def route_question(question):
    question_lower = question.lower()

    sql_keywords = [
        "how many",
        "count",
        "most",
        "highest",
        "top",
        "distribution",
        "by hospital",
        "by manufacturer",
        "by modality",
        "by body part",
        "rank",
        "average",
        "total",
    ]

    for keyword in sql_keywords:
        if keyword in question_lower:
            return "sql"

    return "rag"