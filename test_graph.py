from pathlib import Path

from graph import graph


# =========================================================
# DATASET
# =========================================================

BASE_DIR = Path(
    __file__
).resolve().parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "sales.csv"
)


# =========================================================
# CHECK FILE
# =========================================================

if not DATA_FILE.exists():

    print(
        f"Dataset not found:\n{DATA_FILE}"
    )

    raise SystemExit


# =========================================================
# QUESTIONS TO TEST
# =========================================================

questions = [

    "What are the most important business insights from this dataset?",

    "Are there any missing values, duplicates or data quality problems?",

    "Which categories are most important and what are the key statistics?",

    "Are there any unusual values or outliers?",

    "Are there relationships between the numerical variables?"
]


# =========================================================
# RUN QUESTIONS
# =========================================================

for question in questions:

    print(
        "\n" + "=" * 80
    )

    print(
        "USER QUESTION:"
    )

    print(
        question
    )

    print(
        "=" * 80
    )


    initial_state = {

        "file_path":
            str(DATA_FILE),

        "question":
            question
    }


    try:

        result = graph.invoke(
            initial_state
        )


        print(
            "\nSELECTED TASKS:"
        )

        print(
            result.get(
                "tasks",
                []
            )
        )


        print(
            "\nPLAN:"
        )

        print(
            result.get(
                "plan",
                ""
            )
        )


        print(
            "\nFINAL ANSWER:"
        )

        print(
            result.get(
                "final_answer",
                "No answer generated."
            )
        )


    except Exception as e:

        print(
            "\nWORKFLOW ERROR:"
        )

        print(
            str(e)
        )