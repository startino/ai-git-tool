import os

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from pydantic import SecretStr
from langchain_community.chat_models import ChatPerplexity


def gpt_4o_mini(temperature: float = 0.5) -> AzureChatOpenAI:
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    assert (
        AZURE_OPENAI_API_KEY is not None
    ), "Environment variable 'AZURE_OPENAI_API_KEY' is not set"

    AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
    assert (
        AZURE_OPENAI_API_ENDPOINT is not None
    ), "Environment variable 'AZURE_OPENAI_API_ENDPOINT' is not set"

    return AzureChatOpenAI(
        streaming=True,
        azure_deployment="gpt-4o-mini",
        temperature=temperature,
        api_key=SecretStr(AZURE_OPENAI_API_KEY),
        azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
        model="gpt-4o-mini",
        api_version="2024-06-01",
        max_retries=20,
    )


def gpt_4o(temperature: float = 0.5) -> AzureChatOpenAI:
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    assert (
        AZURE_OPENAI_API_KEY is not None
    ), "Environment variable 'AZURE_OPENAI_API_KEY' is not set"

    AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
    assert (
        AZURE_OPENAI_API_ENDPOINT is not None
    ), "Environment variable 'AZURE_OPENAI_API_ENDPOINT' is not set"

    return AzureChatOpenAI(
        streaming=True,
        azure_deployment="gpt-4o",
        temperature=temperature,
        api_key=SecretStr(AZURE_OPENAI_API_KEY),
        azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
        model="gpt-4o",
        api_version="2024-06-01",
        max_retries=20,
    )
