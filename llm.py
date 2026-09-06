import os

from dotenv import load_dotenv
from mistralai import Mistral


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv(
    ".env",
    override=True
)


# =========================================================
# MISTRAL CONFIGURATION
# =========================================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY"
)

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest"
)


# =========================================================
# CHECK API KEY
# =========================================================

if not MISTRAL_API_KEY:

    raise ValueError(
        "MISTRAL_API_KEY not found. "
        "Please check your .env file."
    )


# =========================================================
# CREATE MISTRAL CLIENT
# =========================================================

client = Mistral(
    api_key=MISTRAL_API_KEY
)


# =========================================================
# ASK MISTRAL
# =========================================================

def ask_mistral(
    prompt,
    system_prompt=None
):
    """
    Sends a prompt to Mistral AI.

    This function is used by graph.py.

    Parameters:
        prompt:
            The instruction/question sent to Mistral.

        system_prompt:
            Optional instruction defining the AI's role.

    Returns:
        Mistral generated text.
    """

    # -----------------------------------------------------
    # CREATE MESSAGE LIST
    # -----------------------------------------------------

    messages = []


    # -----------------------------------------------------
    # ADD SYSTEM PROMPT
    # -----------------------------------------------------

    if system_prompt:

        messages.append(
            {
                "role": "system",
                "content": system_prompt
            }
        )


    # -----------------------------------------------------
    # ADD USER PROMPT
    # -----------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    # -----------------------------------------------------
    # CALL MISTRAL
    # -----------------------------------------------------

    try:

        response = client.chat.complete(

            model=MISTRAL_MODEL,

            messages=messages,

            temperature=0.2
        )


        # -------------------------------------------------
        # GET GENERATED TEXT
        # -------------------------------------------------

        answer = (
            response.choices[0]
            .message
            .content
        )


        # -------------------------------------------------
        # HANDLE EMPTY RESPONSE
        # -------------------------------------------------

        if answer is None:

            return (
                "Mistral returned an empty response."
            )


        return str(answer).strip()


    # -----------------------------------------------------
    # HANDLE API ERROR
    # -----------------------------------------------------

    except Exception as e:

        return (
            f"Mistral API error: {str(e)}"
        )


# =========================================================
# COMPATIBILITY FUNCTION
# =========================================================

def generate_response(
    prompt,
    system_prompt=None
):
    """
    Compatibility wrapper.

    Some parts of the project may use
    generate_response() instead of ask_mistral().
    """

    return ask_mistral(
        prompt=prompt,
        system_prompt=system_prompt
    )


# =========================================================
# SIMPLE TEST
# =========================================================

def test_mistral():
    """
    Tests the Mistral connection.
    """

    return ask_mistral(
        prompt=(
            "Explain sales analysis in "
            "one simple sentence."
        ),

        system_prompt=(
            "You are a helpful data analyst."
        )
    )


# =========================================================
# RUN DIRECT TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print("MISTRAL AI TEST")

    print("=" * 60)

    print(
        f"Model: {MISTRAL_MODEL}"
    )

    print()

    print(
        test_mistral()
    )

    print()

    print(
        "MISTRAL TEST COMPLETED"
    )

    print("=" * 60)