from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    question: str
    file_path: str

    tasks: list
    plan: str

    analysis_results: dict

    cleaned_file_path: str

    charts: list

    raw_insights: str
    final_answer: str