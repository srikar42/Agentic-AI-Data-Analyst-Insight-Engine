import os
from pathlib import Path

from dotenv import load_dotenv
from mistralai.client import Mistral


# =========================================================
# FIND THE PROJECT FOLDER
# =========================================================

# __file__ means the location of this llm.py file.
#
# .resolve() gives the complete path.
#
# .parent gives the folder containing llm.py.
BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# FIND .ENV FILE
# =========================================================

ENV_FILE = BASE_DIR / ".env"


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# =========================================================
# READ MISTRAL SETTINGS
# =========================================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-large-latest"
)


# =========================================================
# MISTRAL FUNCTION
# =========================================================

def ask_mistral(prompt: str) -> str:
    """
    Send a prompt to Mistral AI.

    Parameters:
        prompt: User/agent instruction sent to Mistral.

    Returns:
        Mistral's generated response.
    """

    # -----------------------------------------------------
    # CHECK API KEY
    # -----------------------------------------------------

    if not MISTRAL_API_KEY:

        return (
            "ERROR: MISTRAL_API_KEY is missing.\n\n"
            f"Expected .env location:\n{ENV_FILE}"
        )


    try:

        # -------------------------------------------------
        # CREATE MISTRAL CLIENT
        # -------------------------------------------------

        client = Mistral(
            api_key=MISTRAL_API_KEY
        )


        # -------------------------------------------------
        # SEND REQUEST
        # -------------------------------------------------

        response = client.chat.complete(
            model=MISTRAL_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        # -------------------------------------------------
        # GET RESPONSE
        # -------------------------------------------------

        answer = response.choices[0].message.content


        if answer is None:

            return "Mistral returned an empty response."


        return str(answer)


    except Exception as e:

        return (
            f"Mistral API error:\n{str(e)}"
        )