import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# READ DATASET
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
# FIND COLUMN
# ============================================================

def find_column(df, possible_names):
    """
    Find a column using case-insensitive matching.
    """

    column_mapping = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:

        name_lower = name.strip().lower()

        if name_lower in column_mapping:

            return column_mapping[name_lower]

    return None


# ============================================================
# SALES BY CATEGORY
# ============================================================

def create_sales_by_category_chart(df):
    """
    Create Sales by Category bar chart.
    """

    sales_column = find_column(
        df,
        [
            "sales",
            "revenue",
            "total_sales",
            "total revenue"
        ]
    )

    category_column = find_column(
        df,
        [
            "category",
            "product_category",
            "product category",
            "type"
        ]
    )

    if not sales_column or not category_column:
        return None

    temp_df = df[
        [category_column, sales_column]
    ].copy()

    temp_df[sales_column] = pd.to_numeric(
        temp_df[sales_column],
        errors="coerce"
    )

    temp_df = temp_df.dropna(
        subset=[
            category_column,
            sales_column
        ]
    )

    if temp_df.empty:
        return None

    grouped = (
        temp_df
        .groupby(category_column)[sales_column]
        .sum()
        .sort_values(ascending=False)
    )

    if grouped.empty:
        return None

    fig, ax = plt.subplots(
        figsize=(8, 4.5)
    )

    grouped.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Sales by Category"
    )

    ax.set_xlabel(
        "Category"
    )

    ax.set_ylabel(
        "Sales"
    )

    plt.xticks(
        rotation=30,
        ha="right"
    )

    plt.tight_layout()

    return fig


# ============================================================
# SALES DISTRIBUTION
# ============================================================

def create_sales_distribution_chart(df):
    """
    Create Sales distribution histogram.
    """

    sales_column = find_column(
        df,
        [
            "sales",
            "revenue",
            "total_sales",
            "total revenue"
        ]
    )

    if not sales_column:
        return None

    sales = pd.to_numeric(
        df[sales_column],
        errors="coerce"
    ).dropna()

    if sales.empty:
        return None

    fig, ax = plt.subplots(
        figsize=(8, 4.5)
    )

    ax.hist(
        sales,
        bins=10
    )

    ax.set_title(
        "Distribution of Sales"
    )

    ax.set_xlabel(
        "Sales"
    )

    ax.set_ylabel(
        "Frequency"
    )

    plt.tight_layout()

    return fig


# ============================================================
# PROFIT VS SALES
# ============================================================

def create_profit_vs_sales_chart(df):
    """
    Create Profit vs Sales scatter plot.
    """

    sales_column = find_column(
        df,
        [
            "sales",
            "revenue",
            "total_sales",
            "total revenue"
        ]
    )

    profit_column = find_column(
        df,
        [
            "profit",
            "net_profit",
            "gross_profit"
        ]
    )

    if not sales_column or not profit_column:
        return None

    temp_df = df[
        [sales_column, profit_column]
    ].copy()

    temp_df[sales_column] = pd.to_numeric(
        temp_df[sales_column],
        errors="coerce"
    )

    temp_df[profit_column] = pd.to_numeric(
        temp_df[profit_column],
        errors="coerce"
    )

    temp_df = temp_df.dropna()

    if temp_df.empty:
        return None

    fig, ax = plt.subplots(
        figsize=(8, 4.5)
    )

    ax.scatter(
        temp_df[sales_column],
        temp_df[profit_column]
    )

    ax.set_title(
        "Profit vs Sales"
    )

    ax.set_xlabel(
        "Sales"
    )

    ax.set_ylabel(
        "Profit"
    )

    plt.tight_layout()

    return fig


# ============================================================
# SALES TREND OVER TIME
# ============================================================

def create_sales_trend_chart(df):
    """
    Create Sales Trend Over Time line chart.

    Automatically searches for common date columns.
    """

    sales_column = find_column(
        df,
        [
            "sales",
            "revenue",
            "total_sales",
            "total revenue"
        ]
    )

    date_column = find_column(
        df,
        [
            "date",
            "order_date",
            "order date",
            "sales_date",
            "sales date",
            "datetime",
            "timestamp"
        ]
    )

    if not sales_column or not date_column:
        return None

    temp_df = df[
        [date_column, sales_column]
    ].copy()

    temp_df[date_column] = pd.to_datetime(
        temp_df[date_column],
        errors="coerce"
    )

    temp_df[sales_column] = pd.to_numeric(
        temp_df[sales_column],
        errors="coerce"
    )

    temp_df = temp_df.dropna(
        subset=[
            date_column,
            sales_column
        ]
    )

    if temp_df.empty:
        return None

    grouped = (
        temp_df
        .groupby(date_column)[sales_column]
        .sum()
        .sort_index()
    )

    if grouped.empty:
        return None

    fig, ax = plt.subplots(
        figsize=(8, 4.5)
    )

    ax.plot(
        grouped.index,
        grouped.values
    )

    ax.set_title(
        "Sales Trend Over Time"
    )

    ax.set_xlabel(
        "Date"
    )

    ax.set_ylabel(
        "Sales"
    )

    plt.xticks(
        rotation=30,
        ha="right"
    )

    plt.tight_layout()

    return fig


# ============================================================
# GENERATE ALL CHARTS
# ============================================================

def generate_charts(file_path):
    """
    Generate business-relevant charts from CSV or Excel data.

    Returns:
        list of matplotlib Figure objects
    """

    df = read_dataset(
        file_path
    )

    charts = []

    # --------------------------------------------------------
    # Chart 1: Sales by Category
    # --------------------------------------------------------

    try:

        chart = create_sales_by_category_chart(
            df
        )

        if chart is not None:
            charts.append(chart)

    except Exception as e:

        print(
            f"Sales by Category chart skipped: {e}"
        )

    # --------------------------------------------------------
    # Chart 2: Sales Distribution
    # --------------------------------------------------------

    try:

        chart = create_sales_distribution_chart(
            df
        )

        if chart is not None:
            charts.append(chart)

    except Exception as e:

        print(
            f"Sales Distribution chart skipped: {e}"
        )

    # --------------------------------------------------------
    # Chart 3: Profit vs Sales
    # --------------------------------------------------------

    try:

        chart = create_profit_vs_sales_chart(
            df
        )

        if chart is not None:
            charts.append(chart)

    except Exception as e:

        print(
            f"Profit vs Sales chart skipped: {e}"
        )

    # --------------------------------------------------------
    # Chart 4: Sales Trend
    # --------------------------------------------------------

    try:

        chart = create_sales_trend_chart(
            df
        )

        if chart is not None:
            charts.append(chart)

    except Exception as e:

        print(
            f"Sales Trend chart skipped: {e}"
        )

    return charts


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_file = "data/sales.csv"

    if os.path.exists(test_file):

        charts = generate_charts(
            test_file
        )

        print(
            f"Generated {len(charts)} charts."
        )

        for chart in charts:

            plt.show()

    else:

        print(
            f"Test file not found: {test_file}"
        )