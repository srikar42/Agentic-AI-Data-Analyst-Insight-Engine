import json
import logging
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from mcp.server.fastmcp import FastMCP


# =========================================================
# LOGGING
# =========================================================

# IMPORTANT:
# MCP stdio uses stdout for protocol communication.
# Therefore debugging must go to stderr.
logging.basicConfig(
    level=logging.ERROR,
    stream=sys.stderr
)


# =========================================================
# CREATE MCP SERVER
# =========================================================

mcp = FastMCP(
    "Agentic AI Data Analyst MCP Server"
)


# =========================================================
# HELPER: LOAD CSV
# =========================================================

def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load CSV using automatic delimiter detection.

    This makes the application more flexible than
    assuming every file uses a comma.
    """

    return pd.read_csv(
        file_path,
        sep=None,
        engine="python"
    )


# =========================================================
# HELPER: IDENTIFY NUMERIC BUSINESS COLUMNS
# =========================================================

def get_numeric_columns(
    df: pd.DataFrame
) -> list:

    numeric_columns = (
        df.select_dtypes(
            include=np.number
        ).columns.tolist()
    )

    # Remove ID-like numeric columns where possible.
    business_columns = []

    for column in numeric_columns:

        unique_ratio = (
            df[column].nunique(dropna=True)
            / max(len(df), 1)
        )

        column_name = column.lower()

        looks_like_id = (
            "id" in column_name
            or column_name.endswith("_key")
            or column_name.endswith("key")
        )

        if (
            looks_like_id
            and unique_ratio > 0.80
        ):
            continue

        business_columns.append(column)

    # If everything was removed, return original numeric columns.
    if not business_columns:
        return numeric_columns

    return business_columns


# =========================================================
# HELPER: DETECT DATE COLUMNS
# =========================================================

def detect_date_columns(
    df: pd.DataFrame
) -> list:

    date_columns = []

    for column in df.columns:

        # Already datetime
        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            date_columns.append(column)
            continue

        # Only try parsing object/string columns
        if (
            df[column].dtype == "object"
            or pd.api.types.is_string_dtype(
                df[column]
            )
        ):

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_ratio = (
                converted.notna().mean()
            )

            if valid_ratio >= 0.80:

                date_columns.append(column)

    return date_columns


# =========================================================
# TOOL 1: PROFILE DATASET
# =========================================================

@mcp.tool()
def profile_dataset(
    file_path: str
) -> str:
    """
    Complete dataset profiling.

    Detects:
    - rows
    - columns
    - data types
    - missing values
    - duplicates
    - numeric columns
    - categorical columns
    - date columns
    - data quality score
    """

    try:

        df = load_csv(file_path)

        rows = len(df)
        columns = len(df.columns)

        # Missing values
        missing = (
            df.isnull()
            .sum()
            .to_dict()
        )

        missing = {
            str(k): int(v)
            for k, v in missing.items()
            if v > 0
        }

        total_missing = (
            df.isnull()
            .sum()
            .sum()
        )

        total_cells = max(
            rows * columns,
            1
        )

        missing_percentage = (
            total_missing
            / total_cells
            * 100
        )

        # Duplicate rows
        duplicate_count = int(
            df.duplicated().sum()
        )

        duplicate_percentage = (
            duplicate_count
            / max(rows, 1)
            * 100
        )

        # Column groups
        numeric_columns = (
            get_numeric_columns(df)
        )

        date_columns = (
            detect_date_columns(df)
        )

        categorical_columns = [
            column
            for column in df.columns
            if (
                column not in numeric_columns
                and column not in date_columns
            )
        ]

        # Data quality score
        score = (
            100
            - (missing_percentage * 0.5)
            - (duplicate_percentage * 0.5)
        )

        score = max(
            0,
            min(100, score)
        )

        result = {

            "rows": rows,

            "columns": columns,

            "column_names":
                df.columns.tolist(),

            "data_types": {
                column: str(dtype)
                for column, dtype
                in df.dtypes.items()
            },

            "numeric_columns":
                numeric_columns,

            "categorical_columns":
                categorical_columns,

            "date_columns":
                date_columns,

            "missing_values":
                missing,

            "total_missing_values":
                int(total_missing),

            "missing_percentage":
                round(
                    missing_percentage,
                    2
                ),

            "duplicate_rows":
                duplicate_count,

            "duplicate_percentage":
                round(
                    duplicate_percentage,
                    2
                ),

            "data_quality_score":
                round(score, 2)
        }

        return json.dumps(
            result,
            indent=2,
            default=str
        )

    except Exception as e:

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# TOOL 2: CLEAN DATASET
# =========================================================

@mcp.tool()
def clean_dataset(
    file_path: str,
    output_path: str = ""
) -> str:
    """
    Clean dataset without modifying the original file.

    Operations:
    - Remove duplicate rows
    - Fill numerical missing values using median
    - Fill categorical missing values using mode
    - Fill remaining categorical missing values with Unknown
    """

    try:

        df = load_csv(file_path)

        original_rows = len(df)

        # -------------------------------------------------
        # REMOVE DUPLICATES
        # -------------------------------------------------

        duplicates_removed = int(
            df.duplicated().sum()
        )

        df = df.drop_duplicates()


        # -------------------------------------------------
        # HANDLE MISSING VALUES
        # -------------------------------------------------

        numeric_filled = {}

        categorical_filled = {}

        for column in df.columns:

            missing_count = int(
                df[column].isnull().sum()
            )

            if missing_count == 0:
                continue


            # Numerical column
            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                median_value = (
                    df[column].median()
                )

                if pd.notna(
                    median_value
                ):

                    df[column] = (
                        df[column]
                        .fillna(median_value)
                    )

                    numeric_filled[column] = {
                        "missing_values": missing_count,
                        "method": "median",
                        "value": float(
                            median_value
                        )
                    }


            # Categorical / text column
            else:

                mode_values = (
                    df[column]
                    .mode(
                        dropna=True
                    )
                )

                if not mode_values.empty:

                    fill_value = mode_values.iloc[0]

                else:

                    fill_value = "Unknown"

                df[column] = (
                    df[column]
                    .fillna(fill_value)
                )

                categorical_filled[column] = {
                    "missing_values": missing_count,
                    "method": "mode",
                    "value": str(
                        fill_value
                    )
                }


        # -------------------------------------------------
        # OUTPUT PATH
        # -------------------------------------------------

        if not output_path:

            source = Path(
                file_path
            )

            output_path = str(
                source.with_name(
                    source.stem
                    + "_cleaned.csv"
                )
            )


        # -------------------------------------------------
        # SAVE CLEAN DATA
        # -------------------------------------------------

        df.to_csv(
            output_path,
            index=False
        )


        result = {

            "original_rows":
                original_rows,

            "final_rows":
                len(df),

            "duplicates_removed":
                duplicates_removed,

            "numeric_missing_values_filled":
                numeric_filled,

            "categorical_missing_values_filled":
                categorical_filled,

            "remaining_missing_values":
                int(
                    df.isnull()
                    .sum()
                    .sum()
                ),

            "cleaned_file":
                output_path
        }

        return json.dumps(
            result,
            indent=2,
            default=str
        )

    except Exception as e:

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# TOOL 3: STATISTICS
# =========================================================

@mcp.tool()
def get_statistics(
    file_path: str
) -> str:
    """
    Generate descriptive statistics
    for numerical business columns.
    """

    try:

        df = load_csv(file_path)

        numeric_columns = (
            get_numeric_columns(df)
        )

        if not numeric_columns:

            return json.dumps({
                "message":
                    "No numerical columns found."
            })


        statistics = (
            df[numeric_columns]
            .describe()
            .round(2)
            .to_dict()
        )

        return json.dumps(
            statistics,
            indent=2
        )

    except Exception as e:

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# TOOL 4: TOP VALUES
# =========================================================

@mcp.tool()
def get_top_values(
    file_path: str,
    column: str,
    top_n: int = 10
) -> str:
    """
    Find the most frequent values in any column.
    """

    try:

        df = load_csv(file_path)

        if column not in df.columns:

            return json.dumps({
                "error":
                    f"Column '{column}' does not exist.",
                "available_columns":
                    df.columns.tolist()
            })


        values = (
            df[column]
            .value_counts(
                dropna=False
            )
            .head(top_n)
            .to_dict()
        )

        return json.dumps(
            values,
            indent=2,
            default=str
        )

    except Exception as e:

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# TOOL 5: CORRELATIONS
# =========================================================

@mcp.tool()
def get_correlations(
    file_path: str
) -> str:
    """
    Calculate correlations between numerical
    business columns.
    """

    try:

        df = load_csv(file_path)

        columns = get_numeric_columns(
            df
        )

        if len(columns) < 2:

            return json.dumps({
                "message":
                    "At least two numerical columns are required."
            })


        correlation = (
            df[columns]
            .corr()
            .round(3)
        )

        return json.dumps(
            correlation.to_dict(),
            indent=2
        )

    except Exception as e:

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# TOOL 6: OUTLIERS
# =========================================================

@mcp.tool()
def detect_outliers(
    file_path: str
) -> str:
    """
    Detect potential outliers using the IQR method.

    Outliers are reported, not automatically deleted.
    """

    try:

        df = load_csv(file_path)

        columns = get_numeric_columns(
            df
        )

        result = {}

        for column in columns:

            series = (
                df[column]
                .dropna()
            )

            if len(series) < 4:
                continue

            q1 = series.quantile(
                0.25
            )

            q3 = series.quantile(
                0.75
            )

            iqr = q3 - q1

            lower = q1 - (
                1.5 * iqr
            )

            upper = q3 + (
                1.5 * iqr
            )

            mask = (
                (df[column] < lower)
                |
                (df[column] > upper)
            )

            count = int(
                mask.sum()
            )

            result[column] = {

                "outlier_count":
                    count,

                "outlier_percentage":
                    round(
                        count
                        / max(len(df), 1)
                        * 100,
                        2
                    ),

                "lower_bound":
                    round(
                        float(lower),
                        2
                    ),

                "upper_bound":
                    round(
                        float(upper),
                        2
                    )
            }

        return json.dumps(
            result,
            indent=2
        )

    except Exception as e:

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# TOOL 7: KPI GENERATION
# =========================================================

@mcp.tool()
def calculate_kpis(
    file_path: str
) -> str:
    """
    Automatically calculate useful business KPIs
    when recognizable columns exist.
    """

    try:

        df = load_csv(file_path)

        kpis = {}

        # -------------------------------------------------
        # COMMON COLUMN DETECTION
        # -------------------------------------------------

        sales_column = None
        profit_column = None

        for column in df.columns:

            name = column.lower()

            if sales_column is None and (
                "sales" in name
                or "revenue" in name
                or "amount" in name
            ):

                if pd.api.types.is_numeric_dtype(
                    df[column]
                ):

                    sales_column = column


            if profit_column is None and (
                "profit" in name
                or "margin" in name
            ):

                if pd.api.types.is_numeric_dtype(
                    df[column]
                ):

                    profit_column = column


        # -------------------------------------------------
        # TOTAL RECORDS
        # -------------------------------------------------

        kpis["total_records"] = int(
            len(df)
        )


        # -------------------------------------------------
        # SALES / REVENUE
        # -------------------------------------------------

        if sales_column:

            total_sales = float(
                df[sales_column]
                .sum()
            )

            average_sales = float(
                df[sales_column]
                .mean()
            )

            kpis["sales_column"] = (
                sales_column
            )

            kpis["total_sales"] = round(
                total_sales,
                2
            )

            kpis["average_sales"] = round(
                average_sales,
                2
            )


        # -------------------------------------------------
        # PROFIT
        # -------------------------------------------------

        if profit_column:

            total_profit = float(
                df[profit_column]
                .sum()
            )

            average_profit = float(
                df[profit_column]
                .mean()
            )

            kpis["profit_column"] = (
                profit_column
            )

            kpis["total_profit"] = round(
                total_profit,
                2
            )

            kpis["average_profit"] = round(
                average_profit,
                2
            )


            if (
                sales_column
                and total_sales != 0
            ):

                margin = (
                    total_profit
                    / total_sales
                    * 100
                )

                kpis["profit_margin"] = round(
                    margin,
                    2
                )


        return json.dumps(
            kpis,
            indent=2
        )

    except Exception as e:

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# TOOL 8: DATE ANALYSIS
# =========================================================

@mcp.tool()
def analyze_datetime(
    file_path: str,
    date_column: str = "",
    value_column: str = ""
) -> str:
    """
    Analyze time-based trends.

    Automatically detects date and numeric columns
    when they are not explicitly supplied.
    """

    try:

        df = load_csv(file_path)

        date_columns = detect_date_columns(
            df
        )

        if not date_columns:

            return json.dumps({
                "message":
                    "No date column detected."
            })


        if (
            date_column
            and date_column in df.columns
        ):

            selected_date = date_column

        else:

            selected_date = (
                date_columns[0]
            )


        # Convert to datetime
        df[selected_date] = pd.to_datetime(
            df[selected_date],
            errors="coerce"
        )


        # Select value column
        numeric_columns = (
            get_numeric_columns(df)
        )

        if (
            value_column
            and value_column in df.columns
            and pd.api.types.is_numeric_dtype(
                df[value_column]
            )
        ):

            selected_value = value_column

        elif numeric_columns:

            # Prefer common business columns
            selected_value = numeric_columns[0]

            for column in numeric_columns:

                name = column.lower()

                if (
                    "sales" in name
                    or "revenue" in name
                ):

                    selected_value = column
                    break

        else:

            return json.dumps({
                "message":
                    "No numeric value column found."
            })


        valid = df.dropna(
            subset=[
                selected_date,
                selected_value
            ]
        ).copy()


        if valid.empty:

            return json.dumps({
                "message":
                    "No valid date/value records found."
            })


        valid["period"] = (
            valid[selected_date]
            .dt.to_period("M")
            .astype(str)
        )


        grouped = (
            valid
            .groupby("period")[selected_value]
            .agg(
                total="sum",
                average="mean",
                count="count"
            )
            .round(2)
        )


        return json.dumps({

            "date_column":
                selected_date,

            "value_column":
                selected_value,

            "monthly_trend":
                grouped.to_dict(
                    orient="index"
                )
        }, indent=2)

    except Exception as e:

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# TOOL 9: CREATE CHART
# =========================================================

@mcp.tool()
def create_chart(
    file_path: str,
    chart_type: str,
    x_column: str,
    y_column: str = "",
    output_path: str = ""
) -> str:
    """
    Create a chart from the dataset.

    Supported:
    - bar
    - line
    - scatter
    - histogram
    - box
    """

    try:

        df = load_csv(file_path)

        if x_column not in df.columns:

            return json.dumps({
                "error":
                    f"Column '{x_column}' does not exist."
            })


        if (
            y_column
            and y_column not in df.columns
        ):

            return json.dumps({
                "error":
                    f"Column '{y_column}' does not exist."
            })


        if not output_path:

            source = Path(
                file_path
            )

            output_path = str(
                source.with_name(
                    source.stem
                    + "_chart.png"
                )
            )


        plt.figure(
            figsize=(10, 6)
        )


        chart_type = (
            chart_type.lower()
            .strip()
        )


        if chart_type == "bar":

            if not y_column:

                return json.dumps({
                    "error":
                        "Bar chart requires y_column."
                })

            grouped = (
                df.groupby(x_column)[y_column]
                .sum()
                .sort_values(
                    ascending=False
                )
                .head(15)
            )

            grouped.plot(
                kind="bar"
            )

            plt.xlabel(
                x_column
            )

            plt.ylabel(
                y_column
            )


        elif chart_type == "line":

            if not y_column:

                return json.dumps({
                    "error":
                        "Line chart requires y_column."
                })

            df.plot(
                x=x_column,
                y=y_column,
                kind="line"
            )


        elif chart_type == "scatter":

            if not y_column:

                return json.dumps({
                    "error":
                        "Scatter chart requires y_column."
                })

            plt.scatter(
                df[x_column],
                df[y_column]
            )

            plt.xlabel(
                x_column
            )

            plt.ylabel(
                y_column
            )


        elif chart_type == "histogram":

            df[x_column].plot(
                kind="hist",
                bins=20
            )

            plt.xlabel(
                x_column
            )


        elif chart_type == "box":

            df.boxplot(
                column=x_column
            )

        else:

            return json.dumps({
                "error":
                    "Unsupported chart type."
            })


        plt.title(
            f"{chart_type.title()} Chart"
        )

        plt.tight_layout()

        plt.savefig(
            output_path,
            dpi=150
        )

        plt.close()


        return json.dumps({
            "chart_type":
                chart_type,

            "file":
                output_path
        })

    except Exception as e:

        plt.close()

        return json.dumps({
            "error": str(e)
        })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    mcp.run()