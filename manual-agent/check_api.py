import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
c = genai.Client(
    http_options=types.HttpOptions(
        timeout=15000,
        retry_options=types.HttpRetryOptions(attempts=1),
    )
)

CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

for model in CANDIDATES:
    t = time.time()
    try:
        r = c.models.generate_content(model=model, contents="Say: ok")
        print(f"OK     {model:28} {time.time() - t:.1f}s  {r.text.strip()[:20]!r}")
    except Exception as e:
        print(f"FAIL   {model:28} {type(e).__name__}: {str(e)[:60]}")