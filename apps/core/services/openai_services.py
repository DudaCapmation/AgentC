import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat_with_tools (self, messages, functions):
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=functions
        )

        return response

    def stream_chat (self, messages, functions):
        # Alternative way to get responses using streaming
        stream = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=functions,
            stream=True
        )

        for chunk in stream:
            yield chunk