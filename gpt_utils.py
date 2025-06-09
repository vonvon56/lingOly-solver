# gpt_utils.py
# GPT model, temperature, API KEY 등 설정하고 직접 호출하는 파트
import time, os, openai
from dotenv import load_dotenv

MAX_RETRY = 5
load_dotenv()  # .env 파일에서 환경변수 로드
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt(prompt=None, messages=None, model="gpt-3.5-turbo", temp=0.5):
    if messages is None:
        messages = [{"role": "user", "content": prompt}]
    
    for i in range(MAX_RETRY):
        try:
            return openai.ChatCompletion.create(
                model=model,
                temperature=temp,
                messages=[{"role": "user", "content": prompt}]
            )
        except openai.error.OpenAIError:
            wait = 2 ** i
            print(f"[GPT] retry {i+1}/{MAX_RETRY} … ({wait}s)")
            time.sleep(wait)
    raise RuntimeError("GPT call failed after retries")
