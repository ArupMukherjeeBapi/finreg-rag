import os
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

MODEL = "open-mistral-nemo"

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])


def ask_llm(prompt: str) -> str:
    response = client.chat.complete(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(ask_llm("Reply with exactly: hello from finreg-rag"))
