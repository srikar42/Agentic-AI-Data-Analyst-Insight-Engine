import os
import re
import pandas as pd
import streamlit as st

from graph import graph


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Agentic AI Data Analyst",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .sub-title {
            font-size: 18px;
            color: #666;
            margin-bottom: 25px;
        }

        .section-title {
            font-size: 25px;
            font-weight: 650;
            margin-top: 25px;
            margin-bottom: 12px;
        }

        .tech-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #f5f5f5;
            margin-bottom: 20px;
        }

        .success-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #e8f5e9;
            border-left: 5px solid #2e7d32;
        }

        .warning-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #fff8e1;
            border-left: 5px solid #f9a825;
        }

        .error-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #ffebee;
            border-left: 5px solid #c62828;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 Agentic AI Data Analyst</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Autonomous Data Profiling, Analysis & Business Insight Engine'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# TECHNOLOGY STACK
# ============================================================

st.markdown(
    """
    <div class="tech-box">
        <b>Technology Stack</b><br><br>
        Python &nbsp; | &nbsp;
        Streamlit &nbsp; | &nbsp;
        LangGraph &nbsp; | &nbsp;
        Mistral AI &nbsp; | &nbsp;
        MCP &nbsp; | &nbsp;
        Pandas &nbsp; | &nbsp;
        Matplotlib &nbsp; | &nbsp;
        Guardrails
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🤖 Agent Workflow")

    st.markdown(
        """
        **1. Planner Agent**  
        Understands the user's question.

        **2. Data Quality Agent**  
        Checks dataset quality.

        **3. Data Cleaning**  
        Handles missing values and duplicates.

        **4. MCP Data Analysis**  
        Performs profiling, statistics,
        correlations, outlier detection and KPI analysis.

        **5. Chart Agent**  
        Generates business-relevant visualizations.

        **6. Insight Agent**  
        Converts analysis results into business insights.

        **7. Guardrails**  
        Validates the final response.
        """
    )

    st.divider()

    st.info(
        "Supported formats:\n\n"
        "📄 CSV\n\n"
        "📊 Excel (.xlsx)"
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_filename(filename):
    """
    Create a safe filename for storing uploaded files.
    """

    filename = os.path.basename(filename)

    filename = re.sub(
        r"[^A-Za-z0-9_.-]",
        "_",
        filename
    )

    return filename


def read_dataset(file_path):
    """
    Read CSV or Excel dataset.
    """

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


def is_data_analysis_question(question):
    """
    Basic validation to prevent clearly unrelated
    questions from triggering the workflow.
    """

    question = question.lower().strip()

    if not question:
        return False

    data_keywords = [
        "data",
        "dataset",
        "sales",
        "profit",
        "revenue",
        "quantity",
        "order",
        "orders",
        "customer",
        "customers",
        "category",
        "categories",
        "region",
        "regions",
        "product",
        "products",
        "average",
        "mean",
        "median",
        "maximum",
        "minimum",
        "max",
        "min",
        "sum",
        "total",
        "count",
        "percentage",
        "percent",
        "trend",
        "growth",
        "correlation",
        "outlier",
        "highest",
        "lowest",
        "top",
        "bottom",
        "compare",
        "comparison",
        "distribution",
        "kpi",
        "statistics",
        "statistical",
        "analyze",
        "analysis",
        "insight",
        "insights",
        "performance",
        "missing",
        "duplicate",
        "column",
        "columns",
        "row",
        "rows"
    ]

    return any(
        keyword in question
        for keyword in data_keywords
    )


# ============================================================
# FILE UPLOAD
# ============================================================

st.markdown(
    '<div class="section-title">📂 Upload Dataset</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload your CSV or Excel file",
    type=["csv", "xlsx"],
    help="Supported formats: CSV and Excel (.xlsx)"
)


# ============================================================
# PROCESS UPLOADED FILE
# ============================================================

if uploaded_file is not None:

    try:

        # ----------------------------------------------------
        # Save uploaded file
        # ----------------------------------------------------

        original_name = safe_filename(
            uploaded_file.name
        )

        extension = os.path.splitext(
            original_name
        )[1].lower()

        os.makedirs(
            "data",
            exist_ok=True
        )

        file_path = os.path.join(
            "data",
            original_name
        )

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )

        # ----------------------------------------------------
        # Read dataset
        # ----------------------------------------------------

        df = read_dataset(
            file_path
        )

        # ----------------------------------------------------
        # Validate dataset
        # ----------------------------------------------------

        if df.empty:

            st.error(
                "❌ The uploaded dataset is empty."
            )

            st.stop()

        if len(df.columns) == 0:

            st.error(
                "❌ The dataset does not contain any columns."
            )

            st.stop()

        # ----------------------------------------------------
        # File information
        # ----------------------------------------------------

        st.success(
            f"✅ Dataset uploaded successfully: "
            f"**{original_name}**"
        )

        if extension == ".csv":

            file_type = "CSV"

        else:

            file_type = "Excel (.xlsx)"

        st.caption(
            f"File type: **{file_type}**"
        )

        # ====================================================
        # DATASET OVERVIEW
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '📊 Dataset Overview'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Rows",
                f"{df.shape[0]:,}"
            )

        with col2:

            st.metric(
                "Columns",
                f"{df.shape[1]:,}"
            )

        with col3:

            st.metric(
                "Missing Values",
                f"{int(df.isnull().sum().sum()):,}"
            )

        with col4:

            st.metric(
                "Duplicate Rows",
                f"{int(df.duplicated().sum()):,}"
            )

        # ====================================================
        # DATA PREVIEW
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '👀 Dataset Preview'
            '</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        # ====================================================
        # COLUMN INFORMATION
        # ====================================================

        with st.expander(
            "📋 View Column Information"
        ):

            column_info = pd.DataFrame(
                {
                    "Column": df.columns,
                    "Data Type": [
                        str(dtype)
                        for dtype in df.dtypes
                    ],
                    "Non-Null Values": [
                        int(
                            df[column].notna().sum()
                        )
                        for column in df.columns
                    ],
                    "Missing Values": [
                        int(
                            df[column].isna().sum()
                        )
                        for column in df.columns
                    ],
                    "Unique Values": [
                        int(
                            df[column].nunique()
                        )
                        for column in df.columns
                    ]
                }
            )

            st.dataframe(
                column_info,
                use_container_width=True,
                hide_index=True
            )

        # ====================================================
        # QUESTION
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '💬 Ask Your Data'
            '</div>',
            unsafe_allow_html=True
        )

        question = st.text_area(
            "Enter your business question",
            placeholder=(
                "Example: Which category has the highest sales?"
            ),
            height=100
        )

        analyze_button = st.button(
            "🚀 Analyze Dataset",
            type="primary",
            use_container_width=True
        )

        # ====================================================
        # RUN AGENTIC WORKFLOW
        # ====================================================

        if analyze_button:

            if not question.strip():

                st.warning(
                    "⚠️ Please enter a question."
                )

                st.stop()

            # ------------------------------------------------
            # Validate question
            # ------------------------------------------------

            if not is_data_analysis_question(
                question
            ):

                st.warning(
                    "⚠️ Please ask a question related "
                    "to the uploaded dataset."
                )

                st.info(
                    "Example questions:\n\n"
                    "- Which category has the highest sales?\n"
                    "- What is the total profit?\n"
                    "- Show the sales trend.\n"
                    "- Which region performs best?\n"
                    "- Are there any outliers?"
                )

                st.stop()

            # ------------------------------------------------
            # Execute workflow
            # ------------------------------------------------

            st.markdown(
                '<div class="section-title">'
                '⚙️ Agentic Analysis'
                '</div>',
                unsafe_allow_html=True
            )

            with st.spinner(
                "🤖 Agents are analyzing your dataset..."
            ):

                try:

                    result = graph.invoke(
                        {
                            "question": question,
                            "file_path": file_path
                        }
                    )

                except Exception as e:

                    st.error(
                        "❌ Error while executing "
                        "the analysis workflow."
                    )

                    st.exception(e)

                    st.stop()

            # =================================================
            # PLAN
            # =================================================

            if result.get("plan"):

                st.markdown(
                    '<div class="section-title">'
                    '🧠 Analysis Plan'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.info(
                    result.get("plan")
                )

            # =================================================
            # TASKS
            # =================================================

            tasks = result.get(
                "tasks",
                []
            )

            if tasks:

                with st.expander(
                    "🔎 View Planned Tasks"
                ):

                    for i, task in enumerate(
                        tasks,
                        start=1
                    ):

                        st.write(
                            f"**{i}.** {task}"
                        )

            # =================================================
            # ANALYSIS RESULTS
            # =================================================

            analysis_results = result.get(
                "analysis_results",
                {}
            )

            # =================================================
            # DATA QUALITY
            # =================================================

            if analysis_results:

                st.markdown(
                    '<div class="section-title">'
                    '🛡️ Data Quality Analysis'
                    '</div>',
                    unsafe_allow_html=True
                )

                before = analysis_results.get(
                    "data_quality_before_cleaning"
                )

                after = analysis_results.get(
                    "data_quality_after_cleaning"
                )

                if before:

                    quality_col1, quality_col2, quality_col3 = st.columns(
                        3
                    )

                    with quality_col1:

                        st.metric(
                            "Quality Before",
                            f"{before.get('score', 0):.2f}"
                        )

                    with quality_col2:

                        after_score = (
                            after.get(
                                "score",
                                0
                            )
                            if after
                            else before.get(
                                "score",
                                0
                            )
                        )

                        st.metric(
                            "Quality After",
                            f"{after_score:.2f}"
                        )

                    with quality_col3:

                        improvement = (
                            after_score
                            - before.get(
                                "score",
                                0
                            )
                        )

                        st.metric(
                            "Improvement",
                            f"{improvement:+.2f}"
                        )

                    quality_table = pd.DataFrame(
                        [
                            {
                                "Metric": "Rows",
                                "Before": before.get(
                                    "rows",
                                    0
                                ),
                                "After": (
                                    after.get(
                                        "rows",
                                        0
                                    )
                                    if after
                                    else "-"
                                )
                            },
                            {
                                "Metric": "Columns",
                                "Before": before.get(
                                    "columns",
                                    0
                                ),
                                "After": (
                                    after.get(
                                        "columns",
                                        0
                                    )
                                    if after
                                    else "-"
                                )
                            },
                            {
                                "Metric": "Missing Values",
                                "Before": before.get(
                                    "missing_values",
                                    0
                                ),
                                "After": (
                                    after.get(
                                        "missing_values",
                                        0
                                    )
                                    if after
                                    else "-"
                                )
                            },
                            {
                                "Metric": "Duplicates",
                                "Before": before.get(
                                    "duplicate_rows",
                                    0
                                ),
                                "After": (
                                    after.get(
                                        "duplicate_rows",
                                        0
                                    )
                                    if after
                                    else "-"
                                )
                            }
                        ]
                    )

                    st.dataframe(
                        quality_table,
                        use_container_width=True,
                        hide_index=True
                    )

                    grade = (
                        after.get("grade")
                        if after
                        else before.get("grade")
                    )

                    if grade:

                        st.write(
                            f"**Quality Grade:** {grade}"
                        )

            # =================================================
            # CLEANING REPORT
            # =================================================

            cleaning_report = analysis_results.get(
                "cleaning_report"
            )

            if cleaning_report:

                st.markdown(
                    '<div class="section-title">'
                    '🧹 Data Cleaning'
                    '</div>',
                    unsafe_allow_html=True
                )

                clean_col1, clean_col2, clean_col3 = st.columns(
                    3
                )

                with clean_col1:

                    st.metric(
                        "Original Rows",
                        cleaning_report.get(
                            "original_rows",
                            "-"
                        )
                    )

                with clean_col2:

                    st.metric(
                        "Final Rows",
                        cleaning_report.get(
                            "final_rows",
                            "-"
                        )
                    )

                with clean_col3:

                    st.metric(
                        "Missing Values After",
                        cleaning_report.get(
                            "missing_values_after",
                            "-"
                        )
                    )

                actions = cleaning_report.get(
                    "actions",
                    []
                )

                if actions:

                    st.write(
                        "**Cleaning Actions:**"
                    )

                    for action in actions:

                        st.write(
                            f"• {action}"
                        )

            # =================================================
            # MCP ANALYSIS RESULTS
            # =================================================

            st.markdown(
                '<div class="section-title">'
                '🔬 Analysis Results'
                '</div>',
                unsafe_allow_html=True
            )

            profile = analysis_results.get(
                "profile"
            )

            if profile:

                with st.expander(
                    "📋 Dataset Profile"
                ):

                    st.json(profile)

            statistics = analysis_results.get(
                "statistics"
            )

            if statistics:

                with st.expander(
                    "📈 Statistical Analysis"
                ):

                    if isinstance(
                        statistics,
                        pd.DataFrame
                    ):

                        st.dataframe(
                            statistics,
                            use_container_width=True
                        )

                    else:

                        st.json(statistics)

            categorical = analysis_results.get(
                "categorical"
            )

            if categorical:

                with st.expander(
                    "🏷️ Categorical Analysis"
                ):

                    if isinstance(
                        categorical,
                        pd.DataFrame
                    ):

                        st.dataframe(
                            categorical,
                            use_container_width=True
                        )

                    else:

                        st.json(categorical)

            correlations = analysis_results.get(
                "correlations"
            )

            if correlations:

                with st.expander(
                    "🔗 Correlations"
                ):

                    if isinstance(
                        correlations,
                        pd.DataFrame
                    ):

                        st.dataframe(
                            correlations,
                            use_container_width=True
                        )

                    else:

                        st.json(correlations)

            outliers = analysis_results.get(
                "outliers"
            )

            if outliers:

                with st.expander(
                    "⚠️ Outlier Detection"
                ):

                    if isinstance(
                        outliers,
                        pd.DataFrame
                    ):

                        st.dataframe(
                            outliers,
                            use_container_width=True
                        )

                    else:

                        st.json(outliers)

            kpis = analysis_results.get(
                "kpis"
            )

            if kpis:

                with st.expander(
                    "🎯 KPIs"
                ):

                    if isinstance(
                        kpis,
                        pd.DataFrame
                    ):

                        st.dataframe(
                            kpis,
                            use_container_width=True
                        )

                    else:

                        st.json(kpis)

            datetime_analysis = analysis_results.get(
                "datetime"
            )

            if datetime_analysis:

                with st.expander(
                    "📅 Date & Time Analysis"
                ):

                    if isinstance(
                        datetime_analysis,
                        pd.DataFrame
                    ):

                        st.dataframe(
                            datetime_analysis,
                            use_container_width=True
                        )

                    else:

                        st.json(datetime_analysis)

            # =================================================
            # CHARTS
            # =================================================

            charts = result.get(
                "charts",
                []
            )

            if charts:

                st.markdown(
                    '<div class="section-title">'
                    '📊 Business Charts'
                    '</div>',
                    unsafe_allow_html=True
                )

                for chart in charts:

                    try:

                        # ------------------------------------
                        # SMALL CHART SIZE
                        # ------------------------------------

                        chart.set_size_inches(
                            6,
                            3.2
                        )

                        st.pyplot(
                            chart,
                            use_container_width=False
                        )

                    except Exception:

                        st.warning(
                            "⚠️ A chart could not be displayed."
                        )

            # =================================================
            # RAW INSIGHTS
            # =================================================

            raw_insights = result.get(
                "raw_insights"
            )

            if raw_insights:

                with st.expander(
                    "🧠 Raw AI Insights"
                ):

                    st.write(
                        raw_insights
                    )

            # =================================================
            # FINAL BUSINESS INSIGHTS
            # =================================================

            final_answer = result.get(
                "final_answer"
            )

            if final_answer:

                st.markdown(
                    '<div class="section-title">'
                    '💡 Final Business Insights'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="success-box">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    final_answer
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            # =================================================
            # CLEANED FILE DOWNLOAD
            # =================================================

            cleaned_file_path = result.get(
                "cleaned_file_path"
            )

            if cleaned_file_path and os.path.exists(
                cleaned_file_path
            ):

                st.markdown(
                    '<div class="section-title">'
                    '📥 Download Cleaned Dataset'
                    '</div>',
                    unsafe_allow_html=True
                )

                cleaned_extension = os.path.splitext(
                    cleaned_file_path
                )[1].lower()

                if cleaned_extension == ".xlsx":

                    download_type = (
                        "application/"
                        "vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )

                else:

                    download_type = "text/csv"

                with open(
                    cleaned_file_path,
                    "rb"
                ) as file:

                    st.download_button(
                        label="⬇️ Download Cleaned Dataset",
                        data=file,
                        file_name=os.path.basename(
                            cleaned_file_path
                        ),
                        mime=download_type,
                        use_container_width=True
                    )

            # =================================================
            # COMPLETION STATUS
            # =================================================

            st.success(
                "✅ Agentic analysis completed successfully."
            )

    # ========================================================
    # OUTER FILE PROCESSING ERROR
    # ========================================================

    except Exception as e:

        st.error(
            "❌ Error while processing the uploaded file."
        )

        st.exception(e)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🤖 Agentic AI Data Analyst | "
    "Python • Streamlit • LangGraph • Mistral AI • MCP • Guardrails"
)