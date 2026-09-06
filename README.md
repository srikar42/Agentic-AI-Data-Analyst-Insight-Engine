# 🤖 Agentic AI Data Analyst

## 📌 Project Overview

**Agentic AI Data Analyst** is an autonomous AI-powered data analysis system that allows users to upload CSV datasets and ask questions using natural language.

The system automatically:

- Understands the user's question
- Creates an analysis plan
- Checks data quality
- Cleans the dataset
- Performs data analysis
- Generates relevant charts
- Extracts business insights
- Validates the final response using Guardrails

The project combines **Agentic AI, LangGraph, Mistral AI, MCP, Pandas, Matplotlib, Guardrails, and Streamlit**.

---

# 🏗️ System Architecture

```text
                    User
                     │
                     ▼
              Streamlit UI
                     │
                     ▼
             LangGraph Workflow
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
   Planner Agent          Data Quality Agent
        │                         │
        ▼                         ▼
  Analysis Tasks            Quality Report
        │                         │
        └────────────┬────────────┘
                     ▼
               Data Cleaner
                     │
                     ▼
                MCP Client
                     │
                     ▼
                MCP Server
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    Statistics   Correlation   Outliers
        │            │            │
        └────────────┼────────────┘
                     ▼
                Chart Agent
                     │
                     ▼
               Insight Agent
                     │
                     ▼
               Mistral AI
                     │
                     ▼
              Guardrails
                     │
                     ▼
             Final Answer
```

---

# 🔄 Agent Workflow

The project follows an autonomous multi-step workflow.

### Step 1 — User Uploads Dataset

The user uploads a CSV file through the Streamlit interface.

Example:

```text
sales.csv
```

The system loads the dataset using Pandas.

### Step 2 — User Asks a Question

The user can ask questions using natural language.

Examples:

```text
What are the total sales?
```

```text
Which category has the highest sales?
```

```text
Which region generates the highest profit?
```

```text
Show me the relationship between sales and profit.
```

### Step 3 — Planner Agent

The Planner Agent understands the user's question and determines what analysis needs to be performed.

For example:

```text
Question:
Which category has the highest sales?
```

The planner identifies tasks such as:

```text
1. Analyze categorical columns
2. Calculate sales by category
3. Identify the highest-performing category
```

---

# 🧹 Data Quality Agent

The Data Quality Agent evaluates the dataset before analysis.

It checks:

- Number of rows
- Number of columns
- Missing values
- Duplicate rows
- Empty columns
- Constant columns
- Data quality score
- Data quality grade

### Quality Grades

| Score | Grade |
|---|---|
| 90–100 | Excellent |
| 75–89 | Good |
| 60–74 | Fair |
| Below 60 | Poor |

The system also compares the dataset:

```text
Before Cleaning
        ↓
Cleaning
        ↓
After Cleaning
```

This allows the user to see whether data quality improved.

---

# 🧽 Data Cleaning

The Data Cleaner automatically handles common data-quality problems.

It can:

- Remove duplicate rows
- Fill missing numerical values
- Handle missing values
- Preserve the dataset structure
- Generate a cleaned CSV file

For numerical columns, missing values can be filled using the median.

Example:

```text
Sales

10000
12000
Missing
15000
```

The system can calculate the median and replace the missing value.

---

# 🔌 MCP Integration

The project uses **Model Context Protocol (MCP)** to provide structured data-analysis tools.

The MCP Server exposes tools that can be called by the analysis workflow.

### MCP Tools

The project includes tools such as:

- `profile_dataset`
- `clean_dataset`
- `get_statistics`
- `get_correlations`
- `detect_outliers`
- `calculate_kpis`
- `get_top_values`
- `analyze_datetime`

This allows the AI workflow to use specialized tools instead of depending only on the LLM.

---

# 📊 Data Analysis Capabilities

The system can perform different types of analysis.

## 1. Dataset Profiling

Provides information about:

- Rows
- Columns
- Data types
- Missing values
- Unique values
- Basic dataset structure

Example question:

```text
What is the structure of the dataset?
```

## 2. Statistical Analysis

The system can calculate:

- Mean
- Median
- Minimum
- Maximum
- Standard deviation
- Count
- Quartiles

Example question:

```text
What is the average sales?
```

## 3. Categorical Analysis

The system can analyze categorical columns.

Example:

```text
Which category has the highest sales?
```

The system can calculate sales grouped by category.

## 4. Correlation Analysis

The system can identify relationships between numerical variables.

Example:

```text
What is the relationship between sales and profit?
```

The system calculates correlations between numerical columns.

## 5. Outlier Detection

The system detects unusual values in numerical columns.

Example:

```text
Are there any outliers in sales?
```

Outliers are treated as **analysis findings**, not automatically as data-quality errors.

## 6. KPI Analysis

The system calculates useful business KPIs.

Examples:

```text
Total Sales
Total Profit
Average Sales
Average Profit
Total Quantity
```

## 7. Top Values

The system can identify top-performing values.

Example:

```text
What are the top 5 products?
```

or:

```text
Which regions have the highest sales?
```

## 8. Date and Time Analysis

If the dataset contains date/time columns, the system can analyze:

- Dates
- Years
- Months
- Trends
- Time-based patterns

Example:

```text
Show me the sales trend over time.
```

---

# 📈 Chart Agent

The Chart Agent automatically generates useful visualizations based on the dataset.

The project supports business-oriented charts such as:

### 1. Sales by Category

Bar chart showing sales across categories.

### 2. Sales Distribution

Histogram showing the distribution of sales values.

### 3. Profit vs Sales

Scatter plot showing the relationship between sales and profit.

### 4. Sales Trend Over Time

Line chart showing sales movement over time when a suitable date column exists.

The system selects charts based on the available dataset columns.

---

# 🧠 Insight Agent

The Insight Agent converts analysis results into meaningful business insights.

Instead of only displaying numbers, it explains what the numbers mean.

Example:

```text
Category A generated the highest sales,
indicating stronger customer demand compared
with the other categories.
```

The Insight Agent uses **Mistral AI** to generate natural-language business insights.

---

# 🛡️ Guardrails

The project includes Guardrails validation to improve the reliability of AI-generated responses.

The Guardrails layer helps ensure that the final answer:

- Is relevant to the dataset
- Is based on available analysis
- Avoids unsupported claims
- Provides meaningful business insights
- Handles invalid or unsupported responses safely

---

# 🔗 LangGraph Orchestration

**LangGraph** is used to orchestrate the different stages of the Agentic AI workflow.

The workflow connects multiple processing steps.

```text
Question
   ↓
Planner
   ↓
Data Quality
   ↓
Data Cleaning
   ↓
MCP Analysis
   ↓
Chart Generation
   ↓
Insight Generation
   ↓
Guardrails
   ↓
Final Answer
```

This creates a structured agentic workflow instead of using a single LLM call.

---

# 🖥️ Streamlit Interface

The project uses **Streamlit** to provide an interactive user interface.

The interface includes:

- CSV upload
- Dataset preview
- Dataset information
- Data quality report
- Cleaning report
- Analysis execution
- Analysis evidence
- Generated charts
- Business insights
- Cleaned dataset download

---

# 💬 Example Questions

Users can ask questions such as:

```text
What are the total sales?
```

```text
What is the average profit?
```

```text
Which category has the highest sales?
```

```text
Which region generates the highest profit?
```

```text
Show the correlation between sales and profit.
```

```text
Are there any outliers?
```

```text
Show me the sales trend over time.
```

```text
What are the key business insights from this dataset?
```

---

# ❌ Unsupported Questions

The system is designed specifically for dataset analysis.

Questions unrelated to the uploaded dataset are rejected.

For example:

```text
What is the capital of India?
```

This is not a dataset-analysis question, so the system does not unnecessarily execute the complete analysis workflow.

---

# 📁 Project Structure

```text
Agentic AI project FULL/
│
├── app.py
├── graph.py
├── agent_state.py
├── llm.py
├── mcp_client.py
├── mcp_server.py
├── data_cleaner.py
├── data_quality_agent.py
├── chart_agent.py
├── guardrails_validator.py
├── test_graph.py
├── test_charts.py
├── README.md
├── requirements.txt
│
├── data/
│   ├── sales.csv
│   ├── sales_cleaned.csv
│   └── test_missing.csv
│
└── .env
```

---

# ⚙️ Installation

## 1. Create the Project

Create the project folder:

```text
Agentic AI project FULL
```

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
MISTRAL_API_KEY=your_mistral_api_key
```

The Mistral API key is used by the Insight Agent to generate business insights.

---

# ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in the browser.

---

# 🧪 Testing

The project contains testing files for different components.

### Test Graph

```bash
python test_graph.py
```

### Test Charts

```bash
python test_charts.py
```

These tests help verify the analysis workflow and chart-generation functionality.

---

# 🔄 End-to-End Example

Suppose the user uploads:

```text
sales.csv
```

and asks:

```text
Which category has the highest sales?
```

The system performs:

```text
1. Upload CSV
       ↓
2. Validate dataset
       ↓
3. Check data quality
       ↓
4. Clean dataset
       ↓
5. Create analysis plan
       ↓
6. Execute MCP analysis
       ↓
7. Generate relevant chart
       ↓
8. Generate business insight
       ↓
9. Validate response
       ↓
10. Display final answer
```

Example final insight:

```text
The Technology category generated the highest sales,
indicating that it is the strongest-performing category
in the dataset.
```

---

# 🌍 Real-World Applications

This project can be adapted for:

- Sales analytics
- Business intelligence
- Customer analytics
- Financial analysis
- Marketing analytics
- E-commerce analytics
- Inventory analysis
- Operations analytics
- Data quality monitoring

---

# ⭐ Key Features

- 🤖 Agentic AI workflow
- 🧠 Natural-language data analysis
- 📊 Automated data profiling
- 🧹 Automatic data cleaning
- 🔌 MCP tool integration
- 📈 Automated chart generation
- 💡 Business insight generation
- 🛡️ Guardrails validation
- 🔗 LangGraph orchestration
- 🖥️ Streamlit user interface
- 📥 Cleaned dataset download
- ❌ Unsupported-question handling
- 📋 Before/after data-quality comparison

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming |
| Pandas | Data processing |
| Matplotlib | Data visualization |
| Streamlit | User interface |
| LangGraph | Agent workflow orchestration |
| Mistral AI | LLM-based business insights |
| MCP | Data-analysis tool integration |
| Guardrails | AI response validation |
| python-dotenv | Environment variable management |

---

# 🎯 Project Objective

The main objective of this project is to build an **autonomous AI Data Analyst** that allows users to analyze datasets using natural language instead of manually writing Python or SQL queries.

The system combines traditional data-analysis techniques with Agentic AI to create an automated end-to-end analytics workflow.

---

# 🚀 Future Enhancements

Possible future improvements include:

- Support for Excel files
- Support for multiple datasets
- SQL database integration
- More advanced visualizations
- Automated report generation
- PDF report export
- Excel report export
- More sophisticated AI agents
- RAG-based business knowledge
- Improved chart recommendations
- Cloud deployment
- User authentication
- Conversation memory

---

# 💼 Interview Explanation

You can explain the project in an interview like this:

> **"I developed an Agentic AI Data Analyst that allows users to upload CSV datasets and ask questions in natural language. I used LangGraph to orchestrate multiple stages including planning, data-quality analysis, data cleaning, MCP-based data analysis, chart generation, and business insight generation. Mistral AI is used for generating natural-language business insights, while Guardrails validates the final response. Streamlit provides the user interface."**

---

# 🌟 Key Project Highlight

The main strength of this project is that it is **not just a chatbot**.

It combines:

```text
LLM
+
Agentic Workflow
+
Data Quality
+
Data Cleaning
+
MCP Tools
+
Data Analysis
+
Visualization
+
Business Insights
+
Guardrails
```

This creates a complete **Agentic AI Data Analytics Pipeline**.

---

# 📌 Status

**Project Status: Core Implementation Completed ✅**

The project successfully supports the end-to-end CSV data analysis workflow including:

- Data profiling
- Data quality analysis
- Data cleaning
- MCP-based analysis
- Visualization
- Mistral AI business insights
- LangGraph orchestration
- Guardrails-based validation
- Streamlit interface

Final documentation, testing, and deployment preparation are being completed.

---

# 👨‍💻 Project Summary

**Agentic AI Data Analyst** demonstrates how Agentic AI can be combined with traditional data-analysis tools to build an autonomous analytics assistant.

The project provides a complete workflow from:

```text
Raw Dataset
     ↓
Data Quality
     ↓
Data Cleaning
     ↓
Data Analysis
     ↓
Visualization
     ↓
AI Insights
     ↓
Validation
     ↓
Business Decision Support
```

**Built with Python, LangGraph, Mistral AI, MCP, Pandas, Matplotlib, Guardrails, and Streamlit.**
