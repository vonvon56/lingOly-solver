# gpt_utils.py
# GPT model, temperature, API KEY 등 설정하고 직접 호출하는 파트
import time
import os
import openai
from dotenv import load_dotenv

MAX_RETRY = 5
load_dotenv()  # .env 파일에서 환경변수 로드
openai.api_key = os.getenv("OPENAI_API_KEY")


def gpt(prompt=None, messages=None, model="gpt-4o", temp=0.5):
    """
    Wrapper for OpenAI ChatCompletion with retry logic (OpenAI Python SDK >=1.0.0).

    Args:
        prompt (str): The user prompt (ignored if messages is provided).
        messages (List[dict], optional): A list of messages for the chat API.
        model (str): Model name to use.
        temp (float): Sampling temperature.

    Returns:
        openai.ChatCompletion or dict: The API response object.

    Raises:
        RuntimeError: If all retry attempts fail.
    """
    # If explicit messages provided, use them; otherwise wrap prompt.
    if messages is None:
        messages = [{"role": "user", "content": prompt}]

    for i in range(MAX_RETRY):
        try:
            # Using the new v1.0.0+ interface
            return openai.chat.completions.create(
                model=model,
                temperature=temp,
                messages=messages,
            )
        except openai.OpenAIError as e:
            wait = 2 ** i
            print(f"[GPT] retry {i+1}/{MAX_RETRY} … ({wait}s) due to error: {e}")
            time.sleep(wait)

    # If we get here, all retries have failed
    raise RuntimeError("GPT call failed after retries")
