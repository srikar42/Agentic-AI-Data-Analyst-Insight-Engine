from typing import TypedDict, List


class AgentState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    # Original uploaded dataset
    file_path: str

    # Cleaned dataset
    cleaned_file_path: str

    # User's natural-language question
    question: str

    # Tasks selected by the planner
    tasks: List[str]

    # Planner's explanation
    plan: str

    # Dataset profile
    profile: str

    # Cleaning report
    cleaning_report: str

    # Statistical analysis
    statistics: str

    # Correlation analysis
    correlations: str

    # Outlier analysis
    outliers: str

    # KPI analysis
    kpis: str

    # Categorical analysis
    categorical_analysis: str

    # Date analysis
    datetime_analysis: str

    # Generated chart
    chart_path: str

    # Mistral-generated insights
    raw_insights: str

    # Guardrails result
    final_answer: str

    # Errors
    error: str