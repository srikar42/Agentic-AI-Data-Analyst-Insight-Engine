import os
import tempfile

import pandas as pd
import streamlit as st

from graph import graph


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Agentic AI Data Analyst",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title(
    "🤖 Agentic AI Data Analyst"
)

st.write(
    "Upload a dataset and ask questions using an "
    "autonomous AI data-analysis workflow."
)

st.caption(
    "LangGraph • Mistral AI • MCP • Guardrails • Pandas"
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header(
        "🧠 Agentic Workflow"
    )

    st.markdown(
        """
        **1. Planner**

        Decides what analysis is needed.

        **2. Data Agent**

        Calls MCP tools dynamically.

        **3. Insight Agent**

        Converts evidence into business insights.

        **4. Guardrails**

        Validates the AI response.
        """
    )


# =========================================================
# UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📂 Upload CSV",
    type=["csv"]
)


if uploaded_file is None:

    st.info(
        "Upload a CSV file to start."
    )

    st.stop()


# =========================================================
# READ DATASET
# =========================================================

try:

    df = pd.read_csv(
        uploaded_file
    )

except Exception as e:

    st.error(
        "Unable to read this CSV file."
    )

    st.exception(e)

    st.stop()


# =========================================================
# DATASET OVERVIEW
# =========================================================

st.success(
    "Dataset uploaded successfully."
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Rows",
        df.shape[0]
    )


with col2:

    st.metric(
        "Columns",
        df.shape[1]
    )


with col3:

    st.metric(
        "Missing Values",
        int(
            df.isnull()
            .sum()
            .sum()
        )
    )


with col4:

    st.metric(
        "Duplicates",
        int(
            df.duplicated()
            .sum()
        )
    )


# =========================================================
# DATA PREVIEW
# =========================================================

with st.expander(
    "👀 Preview Dataset"
):

    st.dataframe(
        df.head(20),
        use_container_width=True
    )


# =========================================================
# QUESTION
# =========================================================

st.subheader(
    "💬 Ask Your Data"
)


question = st.text_area(
    "Enter your question",
    placeholder=(
        "Example: Find missing values, analyze sales "
        "performance, detect outliers and give "
        "business recommendations."
    ),
    height=100
)


# =========================================================
# ANALYZE
# =========================================================

if st.button(
    "🚀 Analyze Dataset",
    type="primary",
    use_container_width=True
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()


    # -----------------------------------------------------
    # SAVE UPLOADED FILE
    # -----------------------------------------------------

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv"
    )


    try:

        temp_file.write(
            uploaded_file.getbuffer()
        )

        temp_file.close()


        # -------------------------------------------------
        # RUN GRAPH
        # -------------------------------------------------

        with st.spinner(
            "🤖 Agents are analyzing your dataset..."
        ):

            result = graph.invoke({

                "file_path":
                    temp_file.name,

                "question":
                    question
            })


        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "💡 AI Analysis"
        )


        final_answer = result.get(
            "final_answer",
            "No answer generated."
        )


        st.markdown(
            final_answer
        )


        # -------------------------------------------------
        # AGENT DETAILS
        # -------------------------------------------------

        with st.expander(
            "🔍 View Agent Workflow"
        ):

            st.write(
                "### 🧠 Selected Tasks"
            )

            st.write(
                result.get(
                    "tasks",
                    []
                )
            )


            st.write(
                "### 📋 Analysis Plan"
            )

            st.write(
                result.get(
                    "plan",
                    "No plan available."
                )
            )


            st.write(
                "### 🔎 Dataset Profile"
            )

            st.code(
                result.get(
                    "profile",
                    "Not requested."
                )
            )


            st.write(
                "### 🧹 Cleaning Report"
            )

            st.code(
                result.get(
                    "cleaning_report",
                    "Not requested."
                )
            )


            st.write(
                "### 📊 Statistics"
            )

            st.code(
                result.get(
                    "statistics",
                    "Not requested."
                )
            )


            st.write(
                "### 🔗 Correlations"
            )

            st.code(
                result.get(
                    "correlations",
                    "Not requested."
                )
            )


            st.write(
                "### 🚨 Outliers"
            )

            st.code(
                result.get(
                    "outliers",
                    "Not requested."
                )
            )


            st.write(
                "### 📈 KPIs"
            )

            st.code(
                result.get(
                    "kpis",
                    "Not requested."
                )
            )


            st.write(
                "### 📅 Date Analysis"
            )

            st.code(
                result.get(
                    "datetime_analysis",
                    "Not requested."
                )
            )


        st.success(
            "Analysis completed and validated."
        )


    except Exception as e:

        st.error(
            "The Agentic AI workflow encountered an error."
        )

        st.exception(e)


    finally:

        # Remove temporary uploaded file
        if os.path.exists(
            temp_file.name
        ):

            os.remove(
                temp_file.name
            )