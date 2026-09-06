import os
import time

from dotenv import load_dotenv
from mistralai.client import Mistral


# Load environment variables
load_dotenv(".env", override=True)

# Mistral configuration
API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

# Create Mistral client
if not API_KEY:
    raise ValueError("MISTRAL_API_KEY is not configured.")

client = Mistral(api_key=API_KEY)


def ask_mistral(prompt: str) -> str:
    """
    Send a prompt to Mistral and return the generated response.
    Includes retry handling for temporary rate-limit errors.
    """

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.chat.complete(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:

            error_text = str(e).lower()

            # Handle rate limiting
            if (
                "429" in error_text
                or "rate limit" in error_text
                or "rate_limited" in error_text
            ):

                if attempt < max_retries - 1:
                    wait_time = 4 * (2 ** attempt)
                    time.sleep(wait_time)
                    continue

            raise e

    return "Unable to generate response."
