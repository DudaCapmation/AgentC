import json
import logging
from apps.core.services.openai_services import OpenAIService
from apps.core.services.schemas import get_schemas
from apps.core.services.functions.team_member import FUNCTION_MAP as TEAM_MEMBER_FUNCTIONS
from apps.core.services.functions.client import FUNCTION_MAP as CLIENT_FUNCTIONS
from apps.core.services.functions.communication import FUNCTION_MAP as COMMUNICATION_FUNCTIONS

FUNCTION_MAP = {
    **TEAM_MEMBER_FUNCTIONS,
    **CLIENT_FUNCTIONS,
    **COMMUNICATION_FUNCTIONS,
}

def summarize_result(result):
    # Helper function to summarize function result in a nice way
    if isinstance(result, list):
        if not result:
            return "No entries found."
        return "\n\n".join(f"- {json.dumps(item, indent=2)}" for item in result)
    if isinstance(result, dict):
        if not result:
            return "No entries found."
        return json.dumps(result, indent=2)
    return str(result) if result else "No entries found."


class Agent:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.function_map = FUNCTION_MAP
        self.function_schemas = get_schemas()

        available_tools = ", ".join(self.function_map.keys())

        self.system_message = {
            "role": "system",
            "content": (
                f"You are a helpful, proactive AI assistant designed to support leadership and operations teams. "
                f"You can access internal tools via function calls, such as: {available_tools}.\n\n"

                "OUTPUT RULES (MANDATORY):\n"
                "1) Always reply in plain, unformatted text only. Do NOT use Markdown, HTML, code blocks, tables, or emojis. "
                "Do not include raw JSON or other machine-readable encodings unless explicitly requested.\n\n"

                "2) Be concise and presentation-friendly. Use short paragraphs separated by single blank lines. "
                "When listing multiple items, write them as simple numbered lines or short sentences — do NOT use bullet Markdown syntax.\n\n"

                "3) For structured records (clients, team members, etc.), use this plain-text format exactly:\n\n"
                "Name: Client Name\n"
                "Description: Short description here.\n"
                "Email: contact@client.com\n\n"
                "Repeat the block above for each record, separated by a single blank line.\n\n"

                "4) If a function call returns no results, reply exactly:\n"
                "No results found.\n\n"
                "Then offer a helpful next step or question.\n\n"

                "5) ALWAYS produce a non-empty answer. If you need clarification, ask one simple clarifying question.\n\n"

                "Tone: professional, supportive, and efficient."
            )
        }

        self.messages = [self.system_message]

    def reset_messages(self):
        self.messages = [self.system_message]

    def add_user_message(self, user_input: str):
        self.messages.append({
            "role": "user",
            "content": user_input or "[No user message provided.]"
        })

    def add_function_result_message(self, function_name: str, function_result: str):
        self.messages.append({
            "role": "function",
            "name": function_name,
            "content": function_result or "[No data returned by function.]"
        })

    def add_assistant_reply_message(self, assistant_reply: str):
        self.messages.append({
            "role": "assistant",
            "content": assistant_reply or "[No reply returned.]"
        })

    def handle_message(self, user_input: str, reset: bool = False) -> str:
        if reset:
            logging.info("Resetting conversation history.")
            self.reset_messages()

        self.add_user_message(user_input)
        logging.debug(f"Current messages: {self.messages}")

        # Call model with messages and function definitions
        response = self.openai_service.chat_with_tools(
            messages=self.messages,
            functions=self.function_schemas
        )
        message = response.choices[0].message

        logging.debug(f"Model message: {message}")

        # Check if model wants to call a function
        if hasattr(message, "function_call") and message.function_call:
            function_call = message.function_call
            function_name = function_call.name
            arguments_str = function_call.arguments or "{}"

            try:
                arguments = json.loads(arguments_str)
            except Exception as e:
                error_msg = f"[Failed to parse arguments JSON: {str(e)}]"
                logging.error(error_msg)
                self.add_function_result_message(function_name, error_msg)
                return error_msg

            try:
                result = self.function_map[function_name](**arguments)
            except Exception as e:
                error_msg = f"[Error executing function '{function_name}': {str(e)}]"
                logging.error(error_msg)
                self.add_function_result_message(function_name, error_msg)
                return error_msg

            formatted_result = summarize_result(result)
            self.add_function_result_message(function_name, formatted_result)

            # Sending updated messages with function response back for final assistant reply
            final_response = self.openai_service.chat_with_tools(
                messages=self.messages,
                functions=self.function_schemas
            )
            final_message = final_response.choices[0].message
            final_content = final_message.content or "[No reply returned.]"
            self.add_assistant_reply_message(final_content)
            return final_content

        # No function call, just assistant reply
        assistant_reply = message.content or "[No reply returned.]"
        self.add_assistant_reply_message(assistant_reply)
        return assistant_reply

    def stream_message(self, user_input: str, reset: bool = False):
        if reset:
            self.reset_messages()
        self.add_user_message(user_input)

        assistant_accum = ""

        try:
            # LLM may generate text or decide to function_call
            for chunk in self.openai_service.stream_chat(
                    messages=self.messages,
                    functions=self.function_schemas
            ):
                try:
                    choice = chunk.choices[0]
                except Exception:
                    continue

                # Check for content
                delta = getattr(choice, "delta", None)
                if delta is None and isinstance(choice, dict):
                    delta = choice.get("delta")

                content = None
                if delta is not None:
                    content = getattr(delta, "content", None)
                    if content is None and isinstance(delta, dict):
                        content = delta.get("content")

                if content:
                    assistant_accum += content
                    yield content
                    continue

                # If no content, check finish_reason
                finish_reason = getattr(choice, "finish_reason", None)
                if finish_reason is None and isinstance(choice, dict):
                    finish_reason = choice.get("finish_reason")

                # If function_call, break to handle it
                if finish_reason == "function_call":
                    # Stop the first stream then fetch the function_call non-streaming
                    break

            if assistant_accum:
                # Verify if a function_call was triggered by calling a non-streaming check
                response_check = self.openai_service.chat_with_tools(
                    messages=self.messages, functions=self.function_schemas
                )
                message_check = response_check.choices[0].message
                if not (hasattr(message_check, "function_call") and message_check.function_call):
                    # No function_call means it's safe to store assistant_accum as final assistant message.
                    self.add_assistant_reply_message(assistant_accum)
                    return  # Streaming complete

            # function_call was triggered
            response = self.openai_service.chat_with_tools(
                messages=self.messages,
                functions=self.function_schemas
            )
            message = response.choices[0].message

            if not (hasattr(message, "function_call") and message.function_call):
                # If no function_call, return what we have
                if assistant_accum:
                    self.add_assistant_reply_message(assistant_accum)
                return

            function_call = message.function_call
            function_name = function_call.name
            arguments_str = function_call.arguments or "{}"

            # Parse arguments
            try:
                arguments = json.loads(arguments_str)
            except Exception as e:
                err = f"[Failed to parse function arguments: {str(e)}]"
                # Yield an error so frontend sees it streamed
                yield err
                # Also append error function result in history
                self.add_function_result_message(function_name, err)
                return

            # Execute the function
            try:
                result = self.function_map[function_name](**arguments)
            except Exception as e:
                err = f"[Error executing function '{function_name}': {str(e)}]"
                yield err
                self.add_function_result_message(function_name, err)
                return

            formatted_result = summarize_result(result)
            self.add_function_result_message(function_name, formatted_result)

            # Now that the function result is in messages, stream the final assistant reply
            # Start a new streaming call so the final assistant message comes back token-by-token
            final_accum = ""
            for chunk in self.openai_service.stream_chat(
                    messages=self.messages,
                    functions=self.function_schemas
            ):
                try:
                    choice = chunk.choices[0]
                except Exception:
                    continue

                delta = getattr(choice, "delta", None)
                if delta is None and isinstance(choice, dict):
                    delta = choice.get("delta")

                content = None
                if delta is not None:
                    content = getattr(delta, "content", None)
                    if content is None and isinstance(delta, dict):
                        content = delta.get("content")

                if content:
                    final_accum += content
                    yield content
                    continue

            # After streaming final reply, append it to the message history
            if final_accum:
                self.add_assistant_reply_message(final_accum)

        except Exception as e:
            # Stream an error message
            err_msg = f"[Streaming error: {str(e)}]"
            logging.exception(err_msg)
            yield err_msg
            return