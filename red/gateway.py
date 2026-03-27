import os
from openai import OpenAI


def make_bedrock_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["BEDROCK_API_KEY"],
        base_url=os.environ["BEDROCK_BASE_URL"],
    )


def make_ollama_client(base_url: str = "http://localhost:11434/v1") -> OpenAI:
    return OpenAI(api_key="ollama", base_url=base_url)


def chat(client: OpenAI, model: str, messages: list, **kwargs) -> str:
    if "localhost" in str(client.base_url):
        resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
        return resp.choices[0].message.content
    resp = client.responses.create(model=model, input=messages, **kwargs)
    return resp.output_text
