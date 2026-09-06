import pandas as pd
import os


def calculate_data_quality(file_path):
    """
    Calculate a deterministic data quality score.

    Checks:
    - Missing values
    - Duplicate rows
    - Completely empty columns
    - Constant columns
    """

    if not file_path or not os.path.exists(file_path):
        return {
            "status": "error",
            "message": "Dataset file not found."
        }

    try:
        df = pd.read_csv(file_path)

        rows = len(df)
        columns = len(df.columns)

        if rows == 0 or columns == 0:
            return {
                "status": "error",
                "message": "Dataset is empty."
            }

        # -----------------------------
        # Missing values
        # -----------------------------
        missing_count = int(
            df.isnull().sum().sum()
        )

        total_cells = rows * columns

        missing_percentage = (
            missing_count / total_cells
        ) * 100 if total_cells else 0

        # -----------------------------
        # Duplicate rows
        # -----------------------------
        duplicate_count = int(
            df.duplicated().sum()
        )

        duplicate_percentage = (
            duplicate_count / rows
        ) * 100 if rows else 0

        # -----------------------------
        # Empty columns
        # -----------------------------
        empty_columns = [
            column
            for column in df.columns
            if df[column].isnull().all()
        ]

        # -----------------------------
        # Constant columns
        # -----------------------------
        constant_columns = [
            column
            for column in df.columns
            if df[column].nunique(dropna=True) <= 1
        ]

        # -----------------------------
        # Quality score
        # -----------------------------
        score = 100.0

        missing_penalty = min(
            40,
            missing_percentage * 0.6
        )

        duplicate_penalty = min(
            30,
            duplicate_percentage * 0.5
        )

        empty_column_penalty = (
            len(empty_columns) / columns
        ) * 20

        constant_column_penalty = (
            len(constant_columns) / columns
        ) * 10

        score -= (
            missing_penalty
            + duplicate_penalty
            + empty_column_penalty
            + constant_column_penalty
        )

        score = max(
            0,
            min(100, score)
        )

        score = round(score, 2)

        # -----------------------------
        # Grade
        # -----------------------------
        if score >= 90:
            grade = "Excellent"

        elif score >= 75:
            grade = "Good"

        elif score >= 60:
            grade = "Fair"

        else:
            grade = "Poor"

        return {
            "status": "success",

            "quality_score": score,

            "grade": grade,

            "rows": rows,

            "columns": columns,

            "missing_values": missing_count,

            "missing_percentage": round(
                missing_percentage,
                2
            ),

            "duplicate_rows": duplicate_count,

            "duplicate_percentage": round(
                duplicate_percentage,
                2
            ),

            "empty_columns": empty_columns,

            "constant_columns": constant_columns,

            "quality_issues": {
                "missing_values": (
                    missing_count > 0
                ),

                "duplicate_rows": (
                    duplicate_count > 0
                ),

                "empty_columns": (
                    len(empty_columns) > 0
                ),

                "constant_columns": (
                    len(constant_columns) > 0
                )
            }
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }