import json
from pathlib import Path

from mcp_client import call_mcp_tool_sync


# =========================================================
# FIND DATASET
# =========================================================

BASE_DIR = Path(
    __file__
).resolve().parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "sales.csv"
)


# =========================================================
# CHECK DATASET
# =========================================================

if not DATA_FILE.exists():

    print("=" * 70)
    print("ERROR: sales.csv NOT FOUND")
    print("=" * 70)

    print(
        f"\nExpected location:\n{DATA_FILE}"
    )

    raise SystemExit


print("=" * 70)
print("MCP DATA ANALYST TEST")
print("=" * 70)

print(
    f"\nDataset: {DATA_FILE}"
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def run_test(
    tool_name,
    arguments
):
    """
    Runs one MCP tool and prints its result.

    Keeping this in one function makes the test
    file easier to maintain.
    """

    print(
        f"\n{'-' * 70}"
    )

    print(
        f"Testing: {tool_name}()"
    )

    print(
        "-" * 70
    )

    try:

        result = call_mcp_tool_sync(
            tool_name,
            arguments
        )

        # Try to make JSON output readable
        try:

            parsed = json.loads(
                result
            )

            print(
                json.dumps(
                    parsed,
                    indent=2
                )
            )

        except Exception:

            print(result)


    except Exception as e:

        print(
            f"ERROR: {e}"
        )


# =========================================================
# 1. PROFILE DATASET
# =========================================================

run_test(

    "profile_dataset",

    {
        "file_path":
            str(DATA_FILE)
    }
)


# =========================================================
# 2. CLEAN DATASET
# =========================================================

cleaned_file = (
    BASE_DIR
    / "data"
    / "sales_cleaned.csv"
)


run_test(

    "clean_dataset",

    {
        "file_path":
            str(DATA_FILE),

        "output_path":
            str(cleaned_file)
    }
)


# =========================================================
# 3. STATISTICS
# =========================================================

run_test(

    "get_statistics",

    {
        "file_path":
            str(DATA_FILE)
    }
)


# =========================================================
# 4. TOP VALUES
# =========================================================

run_test(

    "get_top_values",

    {
        "file_path":
            str(DATA_FILE),

        "column":
            "Category",

        "top_n":
            5
    }
)


# =========================================================
# 5. CORRELATIONS
# =========================================================

run_test(

    "get_correlations",

    {
        "file_path":
            str(DATA_FILE)
    }
)


# =========================================================
# 6. OUTLIERS
# =========================================================

run_test(

    "detect_outliers",

    {
        "file_path":
            str(DATA_FILE)
    }
)


# =========================================================
# 7. KPIs
# =========================================================

run_test(

    "calculate_kpis",

    {
        "file_path":
            str(DATA_FILE)
    }
)


# =========================================================
# 8. DATE ANALYSIS
# =========================================================

run_test(

    "analyze_datetime",

    {
        "file_path":
            str(DATA_FILE)
    }
)


# =========================================================
# FINAL MESSAGE
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "MCP DATA ANALYST TEST COMPLETED"
)

print(
    "=" * 70
)