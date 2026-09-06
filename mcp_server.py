import os
import pandas as pd
import numpy as np

from mcp.server.fastmcp import FastMCP


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP("Data Analysis MCP Server")


# ============================================================
# COMMON DATASET READER
# ============================================================

def read_dataset(file_path):
    """
    Read CSV or Excel dataset based on file extension.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    extension = os.path.splitext(
        file_path
    )[1].lower()

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
# PROFILE DATASET
# ============================================================

@mcp.tool()
def profile_dataset(file_path: str) -> dict:
    """
    Generate a complete profile of the dataset.
    Supports CSV and Excel files.
    """

    df = read_dataset(file_path)

    profile = {
        "file_name": os.path.basename(file_path),
        "file_type": os.path.splitext(file_path)[1].lower(),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "missing_values": {
            column: int(df[column].isnull().sum())
            for column in df.columns
        },
        "unique_values": {
            column: int(df[column].nunique())
            for column in df.columns
        },
        "duplicate_rows": int(
            df.duplicated().sum()
        )
    }

    return profile


# ============================================================
# CLEAN DATASET
# ============================================================

@mcp.tool()
def clean_dataset(file_path: str) -> dict:
    """
    Clean CSV or Excel dataset.

    Removes duplicate rows and fills missing values.
    """

    df = read_dataset(file_path)

    original_rows = len(df)

    original_columns = len(df.columns)

    missing_before = int(
        df.isnull().sum().sum()
    )

    duplicates_before = int(
        df.duplicated().sum()
    )

    actions = []

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    if duplicates_before > 0:

        df = df.drop_duplicates()

        actions.append(
            f"Removed {duplicates_before} duplicate rows."
        )

    # --------------------------------------------------------
    # Handle missing values
    # --------------------------------------------------------

    for column in df.columns:

        missing_count = int(
            df[column].isnull().sum()
        )

        if missing_count == 0:
            continue

        # Numeric column
        if pd.api.types.is_numeric_dtype(
            df[column]
        ):

            median_value = df[column].median()

            if pd.isna(median_value):

                df[column] = df[column].fillna(0)

                actions.append(
                    f"Filled {missing_count} missing values "
                    f"in '{column}' with 0."
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

        # Text / categorical column
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

    # --------------------------------------------------------
    # Save cleaned file in same format
    # --------------------------------------------------------

    directory = os.path.dirname(file_path)

    filename = os.path.basename(file_path)

    name, extension = os.path.splitext(
        filename
    )

    cleaned_path = os.path.join(
        directory,
        f"{name}_cleaned{extension}"
    )

    extension = extension.lower()

    if extension == ".csv":

        df.to_csv(
            cleaned_path,
            index=False
        )

    elif extension == ".xlsx":

        df.to_excel(
            cleaned_path,
            index=False,
            engine="openpyxl"
        )

    # --------------------------------------------------------
    # Final information
    # --------------------------------------------------------

    missing_after = int(
        df.isnull().sum().sum()
    )

    duplicates_after = int(
        df.duplicated().sum()
    )

    return {
        "status": "success",
        "original_rows": original_rows,
        "original_columns": original_columns,
        "missing_values_before": missing_before,
        "duplicates_before": duplicates_before,
        "missing_values_after": missing_after,
        "duplicates_after": duplicates_after,
        "actions": actions,
        "final_rows": int(len(df)),
        "final_columns": int(len(df.columns)),
        "cleaned_file": cleaned_path
    }


# ============================================================
# GET STATISTICS
# ============================================================

@mcp.tool()
def get_statistics(file_path: str) -> dict:
    """
    Calculate descriptive statistics for numeric columns.
    Supports CSV and Excel.
    """

    df = read_dataset(file_path)

    numeric_df = df.select_dtypes(
        include=np.number
    )

    if numeric_df.empty:

        return {
            "status": "success",
            "message": "No numeric columns found.",
            "statistics": {}
        }

    statistics = {}

    for column in numeric_df.columns:

        series = numeric_df[column].dropna()

        if series.empty:
            continue

        statistics[column] = {
            "count": int(series.count()),
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std())
            if len(series) > 1
            else 0.0,
            "min": float(series.min()),
            "max": float(series.max()),
            "sum": float(series.sum())
        }

    return {
        "status": "success",
        "statistics": statistics
    }


# ============================================================
# GET CORRELATIONS
# ============================================================

@mcp.tool()
def get_correlations(file_path: str) -> dict:
    """
    Calculate correlations between numeric columns.
    """

    df = read_dataset(file_path)

    numeric_df = df.select_dtypes(
        include=np.number
    )

    if numeric_df.shape[1] < 2:

        return {
            "status": "success",
            "message": (
                "At least two numeric columns "
                "are required for correlation analysis."
            ),
            "correlations": {}
        }

    correlation_df = numeric_df.corr()

    correlations = {}

    for column in correlation_df.columns:

        correlations[column] = {
            other_column: float(
                correlation_df.loc[
                    column,
                    other_column
                ]
            )
            for other_column in correlation_df.columns
            if not pd.isna(
                correlation_df.loc[
                    column,
                    other_column
                ]
            )
        }

    return {
        "status": "success",
        "correlations": correlations
    }


# ============================================================
# DETECT OUTLIERS
# ============================================================

@mcp.tool()
def detect_outliers(file_path: str) -> dict:
    """
    Detect numeric outliers using the IQR method.
    """

    df = read_dataset(file_path)

    numeric_df = df.select_dtypes(
        include=np.number
    )

    results = {}

    for column in numeric_df.columns:

        series = numeric_df[column].dropna()

        if series.empty:
            continue

        q1 = series.quantile(0.25)

        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr

        upper_bound = q3 + 1.5 * iqr

        outliers = series[
            (series < lower_bound)
            |
            (series > upper_bound)
        ]

        results[column] = {
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "outlier_count": int(
                len(outliers)
            ),
            "outlier_values": [
                float(value)
                for value in outliers.tolist()
            ]
        }

    return {
        "status": "success",
        "outliers": results
    }


# ============================================================
# CALCULATE KPIs
# ============================================================

@mcp.tool()
def calculate_kpis(file_path: str) -> dict:
    """
    Calculate common business KPIs when
    relevant columns are available.
    """

    df = read_dataset(file_path)

    kpis = {}

    # --------------------------------------------------------
    # Sales
    # --------------------------------------------------------

    sales_column = None

    for column in df.columns:

        if column.lower() in [
            "sales",
            "revenue",
            "total_sales",
            "total revenue"
        ]:

            sales_column = column
            break

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    profit_column = None

    for column in df.columns:

        if column.lower() in [
            "profit",
            "net_profit",
            "gross_profit"
        ]:

            profit_column = column
            break

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    quantity_column = None

    for column in df.columns:

        if column.lower() in [
            "quantity",
            "qty",
            "units",
            "units_sold"
        ]:

            quantity_column = column
            break

    # --------------------------------------------------------
    # Sales KPIs
    # --------------------------------------------------------

    if sales_column:

        total_sales = df[
            sales_column
        ].sum()

        average_sales = df[
            sales_column
        ].mean()

        kpis["total_sales"] = float(
            total_sales
        )

        kpis["average_sales"] = float(
            average_sales
        )

    # --------------------------------------------------------
    # Profit KPIs
    # --------------------------------------------------------

    if profit_column:

        total_profit = df[
            profit_column
        ].sum()

        average_profit = df[
            profit_column
        ].mean()

        kpis["total_profit"] = float(
            total_profit
        )

        kpis["average_profit"] = float(
            average_profit
        )

    # --------------------------------------------------------
    # Profit Margin
    # --------------------------------------------------------

    if sales_column and profit_column:

        total_sales = df[
            sales_column
        ].sum()

        total_profit = df[
            profit_column
        ].sum()

        if total_sales != 0:

            profit_margin = (
                total_profit
                /
                total_sales
            ) * 100

            kpis["profit_margin_percentage"] = float(
                profit_margin
            )

    # --------------------------------------------------------
    # Quantity KPIs
    # --------------------------------------------------------

    if quantity_column:

        kpis["total_quantity"] = float(
            df[quantity_column].sum()
        )

        kpis["average_quantity"] = float(
            df[quantity_column].mean()
        )

    # --------------------------------------------------------
    # Number of records
    # --------------------------------------------------------

    kpis["total_records"] = int(
        len(df)
    )

    return {
        "status": "success",
        "kpis": kpis
    }


# ============================================================
# GET TOP VALUES
# ============================================================

@mcp.tool()
def get_top_values(
    file_path: str,
    column: str,
    n: int = 5
) -> dict:
    """
    Get the most frequent values from a column.
    """

    df = read_dataset(file_path)

    if column not in df.columns:

        return {
            "status": "error",
            "message": (
                f"Column '{column}' not found."
            )
        }

    values = (
        df[column]
        .value_counts()
        .head(n)
    )

    result = {}

    for value, count in values.items():

        result[str(value)] = int(count)

    return {
        "status": "success",
        "column": column,
        "top_values": result
    }


# ============================================================
# ANALYZE DATETIME
# ============================================================

@mcp.tool()
def analyze_datetime(
    file_path: str,
    column: str
) -> dict:
    """
    Analyze a date/time column.
    """

    df = read_dataset(file_path)

    if column not in df.columns:

        return {
            "status": "error",
            "message": (
                f"Column '{column}' not found."
            )
        }

    dates = pd.to_datetime(
        df[column],
        errors="coerce"
    )

    valid_dates = dates.dropna()

    if valid_dates.empty:

        return {
            "status": "error",
            "message": (
                f"Column '{column}' does not contain "
                "valid date/time values."
            )
        }

    result = {
        "column": column,
        "valid_dates": int(
            len(valid_dates)
        ),
        "invalid_dates": int(
            len(dates) - len(valid_dates)
        ),
        "minimum_date": str(
            valid_dates.min()
        ),
        "maximum_date": str(
            valid_dates.max()
        ),
        "year_distribution": {
            str(year): int(count)
            for year, count in (
                valid_dates
                .dt.year
                .value_counts()
                .sort_index()
                .items()
            )
        },
        "month_distribution": {
            str(month): int(count)
            for month, count in (
                valid_dates
                .dt.month
                .value_counts()
                .sort_index()
                .items()
            )
        }
    }

    return {
        "status": "success",
        "datetime_analysis": result
    }


# ============================================================
# RUN MCP SERVER
# ============================================================

if __name__ == "__main__":

    mcp.run(
        transport="stdio"
    )