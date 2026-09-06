import os
import pandas as pd


# ============================================================
# READ DATASET
# ============================================================

def read_dataset(file_path):
    """
    Read CSV or Excel dataset based on file extension.
    """

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":

        return pd.read_csv(file_path)

    elif extension == ".xlsx":

        return pd.read_excel(
            file_path,
            engine="openpyxl"
        )

    else:

        raise ValueError(
            "Unsupported file format. "
            "Only CSV and Excel (.xlsx) files are supported."
        )


# ============================================================
# SAVE DATASET
# ============================================================

def save_dataset(df, original_file_path):
    """
    Save cleaned dataset in the same format as the original file.
    """

    directory = os.path.dirname(
        original_file_path
    )

    filename = os.path.basename(
        original_file_path
    )

    name, extension = os.path.splitext(
        filename
    )

    extension = extension.lower()

    cleaned_filename = (
        f"{name}_cleaned{extension}"
    )

    cleaned_file_path = os.path.join(
        directory,
        cleaned_filename
    )

    # --------------------------------------------------------
    # Save CSV
    # --------------------------------------------------------

    if extension == ".csv":

        df.to_csv(
            cleaned_file_path,
            index=False
        )

    # --------------------------------------------------------
    # Save Excel
    # --------------------------------------------------------

    elif extension == ".xlsx":

        df.to_excel(
            cleaned_file_path,
            index=False,
            engine="openpyxl"
        )

    else:

        raise ValueError(
            "Unsupported file format."
        )

    return cleaned_file_path


# ============================================================
# CLEAN DATASET
# ============================================================

def clean_dataset(file_path):
    """
    Clean a CSV or Excel dataset.

    Cleaning operations:
    1. Remove duplicate rows.
    2. Fill missing numeric values using median.
    3. Fill missing categorical/text values using mode.
    4. Save the cleaned dataset in the same format.
    """

    # --------------------------------------------------------
    # Read dataset
    # --------------------------------------------------------

    df = read_dataset(
        file_path
    )

    # --------------------------------------------------------
    # Original information
    # --------------------------------------------------------

    original_rows = len(df)

    original_columns = len(df.columns)

    missing_values_before = int(
        df.isnull().sum().sum()
    )

    duplicates_before = int(
        df.duplicated().sum()
    )

    actions = []

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    if duplicates_before > 0:

        df = df.drop_duplicates()

        actions.append(
            f"Removed {duplicates_before} duplicate rows."
        )

    # ========================================================
    # HANDLE MISSING VALUES
    # ========================================================

    for column in df.columns:

        missing_count = int(
            df[column].isnull().sum()
        )

        if missing_count == 0:
            continue

        # ----------------------------------------------------
        # Numeric columns
        # ----------------------------------------------------

        if pd.api.types.is_numeric_dtype(
            df[column]
        ):

            median_value = df[column].median()

            # If the entire numeric column is missing,
            # median will also be NaN.
            if pd.isna(median_value):

                df[column] = df[column].fillna(0)

                actions.append(
                    f"Filled {missing_count} missing values "
                    f"in '{column}' with 0 because no "
                    f"valid numeric values were available."
                )

            else:

                df[column] = df[column].fillna(
                    median_value
                )

                actions.append(
                    f"Filled {missing_count} missing values "
                    f"in '{column}' using median "
                    f"({median_value})."
                )

        # ----------------------------------------------------
        # Categorical / text columns
        # ----------------------------------------------------

        else:

            mode_values = df[column].mode(
                dropna=True
            )

            if not mode_values.empty:

                mode_value = mode_values.iloc[0]

                df[column] = df[column].fillna(
                    mode_value
                )

                actions.append(
                    f"Filled {missing_count} missing values "
                    f"in '{column}' using mode "
                    f"('{mode_value}')."
                )

            else:

                df[column] = df[column].fillna(
                    "Unknown"
                )

                actions.append(
                    f"Filled {missing_count} missing values "
                    f"in '{column}' with 'Unknown'."
                )

    # ========================================================
    # FINAL INFORMATION
    # ========================================================

    missing_values_after = int(
        df.isnull().sum().sum()
    )

    duplicates_after = int(
        df.duplicated().sum()
    )

    final_rows = len(df)

    final_columns = len(df.columns)

    # ========================================================
    # SAVE CLEANED DATASET
    # ========================================================

    cleaned_file_path = save_dataset(
        df,
        file_path
    )

    # ========================================================
    # RETURN CLEANING REPORT
    # ========================================================

    return {
        "status": "success",

        "original_rows": original_rows,

        "original_columns": original_columns,

        "missing_values_before": missing_values_before,

        "duplicates_before": duplicates_before,

        "missing_values_after": missing_values_after,

        "duplicates_after": duplicates_after,

        "actions": actions,

        "final_rows": final_rows,

        "final_columns": final_columns,

        "cleaned_file": cleaned_file_path
    }


# ============================================================
# MAIN FUNCTION
# ============================================================

if __name__ == "__main__":

    print(
        "Data Cleaner supports CSV and Excel (.xlsx) files."
    )