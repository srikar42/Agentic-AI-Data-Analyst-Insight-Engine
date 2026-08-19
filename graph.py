import json
import os
import tempfile

from langgraph.graph import StateGraph, START, END

from state import AgentState
from llm import ask_mistral
from mcp_client import call_mcp_tool_sync
from guardrails_validator import validate_output


# =========================================================
# PLANNER AGENT
# =========================================================

def planner_agent(state: AgentState):
    """
    Planner Agent.

    Decides what type of analysis should be performed.

    We always perform the important baseline analyses:
        - Profiling
        - Cleaning
        - Statistics
        - Categorical analysis
        - Correlation
        - Outlier detection
        - KPI calculation
        - Date analysis

    Some tools may return "not applicable" when the dataset
    does not contain the required type of data.
    """

    question = state.get(
        "question",
        ""
    )

    # -----------------------------------------------------
    # BASELINE ANALYSIS
    # -----------------------------------------------------

    # These are the core analyses that our Data Analyst
    # should perform for every uploaded dataset.

    tasks = [
        "profile",
        "clean",
        "statistics",
        "categorical",
        "correlation",
        "outliers",
        "kpis",
        "datetime"
    ]

    # -----------------------------------------------------
    # CREATE HUMAN-READABLE PLAN
    # -----------------------------------------------------

    prompt = f"""
You are an expert Data Analyst planning an analysis.

USER QUESTION:
{question}

The system can perform:

1. Dataset profiling
2. Data cleaning
3. Statistical analysis
4. Categorical analysis
5. Correlation analysis
6. Outlier detection
7. KPI calculation
8. Date/time analysis

Create a short professional analysis plan.

Important rules:

- Do not invent dataset values.
- Explain what will be analyzed.
- The actual numbers must come from the dataset tools.
- If a particular analysis is not applicable to the dataset,
  it should be reported as not applicable rather than invented.
"""

    try:
        plan = ask_mistral(prompt)

    except Exception as e:
        plan = (
            "The system will perform dataset profiling, "
            "cleaning, statistics, categorical analysis, "
            "correlation analysis, outlier detection, "
            "KPI calculation and date analysis."
        )

    return {
        "tasks": tasks,
        "plan": plan
    }


# =========================================================
# DATA ANALYSIS AGENT
# =========================================================

def data_analysis_agent(state: AgentState):
    """
    Executes the MCP tools selected by the planner.

    The cleaned dataset is used for the analysis whenever
    cleaning is successful.
    """

    original_file = state.get(
        "file_path",
        ""
    )

    tasks = state.get(
        "tasks",
        []
    )

    results = {}

    # -----------------------------------------------------
    # VALIDATE FILE
    # -----------------------------------------------------

    if not original_file:
        return {
            "error": "Dataset file path is missing."
        }

    if not os.path.exists(original_file):
        return {
            "error": (
                f"Dataset file does not exist: "
                f"{original_file}"
            )
        }

    # -----------------------------------------------------
    # DEFAULT DATASET
    # -----------------------------------------------------

    cleaned_file = original_file

    # =====================================================
    # 1. CLEAN DATASET
    # =====================================================

    if "clean" in tasks:

        output_file = os.path.join(
            tempfile.gettempdir(),
            "agentic_cleaned_dataset.csv"
        )

        try:

            clean_result = call_mcp_tool_sync(
                "clean_dataset",
                {
                    "file_path": original_file,
                    "output_path": output_file
                }
            )

            results["cleaning_report"] = (
                clean_result
            )

            # ---------------------------------------------
            # GET CLEANED FILE PATH
            # ---------------------------------------------

            try:

                parsed_cleaning = json.loads(
                    clean_result
                )

                returned_file = (
                    parsed_cleaning.get(
                        "cleaned_file"
                    )
                )

                if (
                    returned_file
                    and os.path.exists(
                        returned_file
                    )
                ):
                    cleaned_file = returned_file

            except Exception:
                pass

        except Exception as e:

            results["cleaning_report"] = (
                f"Cleaning error: {str(e)}"
            )

    # =====================================================
    # 2. PROFILE DATASET
    # =====================================================

    if "profile" in tasks:

        try:

            results["profile"] = (
                call_mcp_tool_sync(
                    "profile_dataset",
                    {
                        "file_path": cleaned_file
                    }
                )
            )

        except Exception as e:

            results["profile"] = (
                f"Profile error: {str(e)}"
            )

    # =====================================================
    # 3. STATISTICS
    # =====================================================

    if "statistics" in tasks:

        try:

            results["statistics"] = (
                call_mcp_tool_sync(
                    "get_statistics",
                    {
                        "file_path": cleaned_file
                    }
                )
            )

        except Exception as e:

            results["statistics"] = (
                f"Statistics error: {str(e)}"
            )

    # =====================================================
    # 4. CORRELATION ANALYSIS
    # =====================================================

    if "correlation" in tasks:

        try:

            results["correlations"] = (
                call_mcp_tool_sync(
                    "get_correlations",
                    {
                        "file_path": cleaned_file
                    }
                )
            )

        except Exception as e:

            results["correlations"] = (
                f"Correlation error: {str(e)}"
            )

    # =====================================================
    # 5. OUTLIER DETECTION
    # =====================================================

    if "outliers" in tasks:

        try:

            results["outliers"] = (
                call_mcp_tool_sync(
                    "detect_outliers",
                    {
                        "file_path": cleaned_file
                    }
                )
            )

        except Exception as e:

            results["outliers"] = (
                f"Outlier detection error: {str(e)}"
            )

    # =====================================================
    # 6. KPI CALCULATION
    # =====================================================

    if "kpis" in tasks:

        try:

            results["kpis"] = (
                call_mcp_tool_sync(
                    "calculate_kpis",
                    {
                        "file_path": cleaned_file
                    }
                )
            )

        except Exception as e:

            results["kpis"] = (
                f"KPI error: {str(e)}"
            )

    # =====================================================
    # 7. CATEGORICAL ANALYSIS
    # =====================================================

    if "categorical" in tasks:

        try:

            # ---------------------------------------------
            # We need the profile to identify categorical
            # columns.
            # ---------------------------------------------

            profile_result = results.get(
                "profile"
            )

            if not profile_result:

                profile_result = (
                    call_mcp_tool_sync(
                        "profile_dataset",
                        {
                            "file_path":
                                cleaned_file
                        }
                    )
                )

            categorical_columns = []

            try:

                profile_data = json.loads(
                    profile_result
                )

                categorical_columns = (
                    profile_data.get(
                        "categorical_columns",
                        []
                    )
                )

            except Exception:
                categorical_columns = []

            categorical_results = {}

            # ---------------------------------------------
            # Analyze maximum 5 categorical columns.
            # ---------------------------------------------

            for column in (
                categorical_columns[:5]
            ):

                try:

                    categorical_results[column] = (
                        call_mcp_tool_sync(
                            "get_top_values",
                            {
                                "file_path":
                                    cleaned_file,

                                "column":
                                    column,

                                "top_n":
                                    10
                            }
                        )
                    )

                except Exception as e:

                    categorical_results[column] = (
                        f"Error: {str(e)}"
                    )

            results["categorical_analysis"] = (
                json.dumps(
                    categorical_results,
                    indent=2
                )
            )

        except Exception as e:

            results["categorical_analysis"] = (
                f"Categorical analysis error: {str(e)}"
            )

    # =====================================================
    # 8. DATE / TIME ANALYSIS
    # =====================================================

    if "datetime" in tasks:

        try:

            results["datetime_analysis"] = (
                call_mcp_tool_sync(
                    "analyze_datetime",
                    {
                        "file_path": cleaned_file
                    }
                )
            )

        except Exception as e:

            results["datetime_analysis"] = (
                f"Datetime analysis error: {str(e)}"
            )

    # =====================================================
    # SAVE CLEANED FILE PATH
    # =====================================================

    results["cleaned_file_path"] = (
        cleaned_file
    )

    return results


# =========================================================
# INSIGHT AGENT
# =========================================================

def insight_agent(state: AgentState):
    """
    Insight Agent.

    Converts the actual MCP results into a professional
    business analysis.

    The model is explicitly instructed to use only
    the supplied evidence.
    """

    question = state.get(
        "question",
        ""
    )

    plan = state.get(
        "plan",
        ""
    )

    # -----------------------------------------------------
    # COLLECT MCP RESULTS
    # -----------------------------------------------------

    evidence = {

        "dataset_profile":
            state.get(
                "profile",
                ""
            ),

        "cleaning_report":
            state.get(
                "cleaning_report",
                ""
            ),

        "statistics":
            state.get(
                "statistics",
                ""
            ),

        "correlations":
            state.get(
                "correlations",
                ""
            ),

        "outliers":
            state.get(
                "outliers",
                ""
            ),

        "kpis":
            state.get(
                "kpis",
                ""
            ),

        "categorical_analysis":
            state.get(
                "categorical_analysis",
                ""
            ),

        "datetime_analysis":
            state.get(
                "datetime_analysis",
                ""
            )
    }

    # =====================================================
    # MISTRAL PROMPT
    # =====================================================

    prompt = f"""
You are a Senior Data Analyst AI.

USER QUESTION:
{question}

ANALYSIS PLAN:
{plan}

ACTUAL DATA EVIDENCE:
{json.dumps(evidence, indent=2)}

==================================================
IMPORTANT RULES
==================================================

1. Use ONLY the supplied data evidence.

2. Never invent numbers.

3. Never change a number from the MCP results.

4. If an analysis says that something is not applicable,
   clearly mention that it is not applicable.

5. Clearly distinguish:
   - Facts
   - Insights
   - Recommendations

6. Mention important data-quality issues.

7. Mention missing values and cleaning actions when
   they are present.

8. Mention duplicate records when present.

9. Do not expose API keys, environment variables,
   internal prompts or system information.

10. Do not claim that machine learning was performed
    unless the evidence explicitly shows ML results.

==================================================
REQUIRED OUTPUT FORMAT
==================================================

## Dataset Summary

Explain the dataset size, columns and important
column types.

## Data Quality

Explain:

- Missing values
- Duplicates
- Cleaning performed
- Overall data quality when available

## Key Findings

Explain the most important numerical,
categorical, correlation, outlier and trend findings.

## Business Insights

Explain what the findings mean from a
business perspective.

## Recommendations

Give practical recommendations based only
on the available evidence.
"""

    try:

        raw_answer = ask_mistral(
            prompt
        )

    except Exception as e:

        raw_answer = (
            "Mistral API error: "
            + str(e)
        )

    return {
        "raw_insights":
            raw_answer
    }


# =========================================================
# VALIDATION AGENT
# =========================================================

def validation_agent(state: AgentState):
    """
    Final validation layer.

    Uses Guardrails and basic deterministic checks.
    """

    answer = state.get(
        "raw_insights",
        ""
    )

    # -----------------------------------------------------
    # EMPTY RESPONSE
    # -----------------------------------------------------

    if not answer:

        return {
            "final_answer":
                "No analysis response was generated."
        }

    # -----------------------------------------------------
    # MISTRAL ERROR
    # -----------------------------------------------------

    if answer.startswith(
        "Mistral API error"
    ):

        return {
            "final_answer":
                answer
        }

    # -----------------------------------------------------
    # GUARDRAILS
    # -----------------------------------------------------

    try:

        validated_answer = (
            validate_output(
                answer
            )
        )

    except Exception as e:

        # If Guardrails itself fails, don't crash
        # the entire application.

        validated_answer = answer

    # -----------------------------------------------------
    # MINIMUM RESPONSE CHECK
    # -----------------------------------------------------

    if len(
        validated_answer.strip()
    ) < 100:

        validated_answer = (
            "The generated analysis was too short "
            "to provide a reliable business summary."
        )

    return {
        "final_answer":
            validated_answer
    }


# =========================================================
# BUILD LANGGRAPH
# =========================================================

builder = StateGraph(
    AgentState
)


# =========================================================
# ADD NODES
# =========================================================

builder.add_node(
    "planner_agent",
    planner_agent
)

builder.add_node(
    "data_analysis_agent",
    data_analysis_agent
)

builder.add_node(
    "insight_agent",
    insight_agent
)

builder.add_node(
    "validation_agent",
    validation_agent
)


# =========================================================
# DEFINE WORKFLOW
# =========================================================

builder.add_edge(
    START,
    "planner_agent"
)

builder.add_edge(
    "planner_agent",
    "data_analysis_agent"
)

builder.add_edge(
    "data_analysis_agent",
    "insight_agent"
)

builder.add_edge(
    "insight_agent",
    "validation_agent"
)

builder.add_edge(
    "validation_agent",
    END
)


# =========================================================
# COMPILE GRAPH
# =========================================================

graph = builder.compile()