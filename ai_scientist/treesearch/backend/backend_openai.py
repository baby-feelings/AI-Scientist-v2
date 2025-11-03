<<<<<<< HEAD
# backend_openai.py

=======
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce
import json
import logging
import time

from .utils import FunctionSpec, OutputType, opt_messages_to_list, backoff_create
from funcy import notnone, once, select_values
import openai
from rich import print
<<<<<<< HEAD
# Import re for JSON extraction
import re
=======
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce

logger = logging.getLogger("ai-scientist")


OPENAI_TIMEOUT_EXCEPTIONS = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.InternalServerError,
)

def get_ai_client(model: str, max_retries=2) -> openai.OpenAI:
    if model.startswith("ollama/"):
        client = openai.OpenAI(
<<<<<<< HEAD
            base_url="http://localhost:11434/v1",
            # Add dummy API key for Ollama as identified in the debug log 
            api_key="ollama",
=======
            base_url="http://localhost:11434/v1", 
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce
            max_retries=max_retries
        )
    else:
        client = openai.OpenAI(max_retries=max_retries)
    return client

<<<<<<< HEAD
# Helper function to extract JSON from Ollama's text response
def _extract_json_from_ollama(text: str) -> dict | None:
    # Find JSON content between ```json and ```
    json_pattern = r"```json(.*?)```"
    matches = re.findall(json_pattern, text, re.DOTALL)

    if not matches:
        # Fallback: Try to find any JSON-like content
        json_pattern = r"\{.*?\}"
        matches = re.findall(json_pattern, text, re.DOTALL)

    for json_string in matches:
        json_string = json_string.strip()
        try:
            # Remove invalid control characters
            json_string_clean = re.sub(r"[\x00-\x1F\x7F]", "", json_string)
            parsed_json = json.loads(json_string_clean)
            return parsed_json
        except json.JSONDecodeError:
            continue
    return None
=======
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce

def query(
    system_message: str | None,
    user_message: str | None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
) -> tuple[OutputType, float, int, int, dict]:
    client = get_ai_client(model_kwargs.get("model"), max_retries=0)
    filtered_kwargs: dict = select_values(notnone, model_kwargs)  # type: ignore

    messages = opt_messages_to_list(system_message, user_message)
<<<<<<< HEAD
    
    # --- Ollama: func_spec (Tools) fix [cite: 3017-3018] ---
    is_ollama = filtered_kwargs.get("model", "").startswith("ollama/")
    
    if is_ollama:
        filtered_kwargs["model"] = filtered_kwargs["model"].replace("ollama/", "")
        if func_spec is not None:
            # Ollama doesn't support 'tools'. Add schema to system prompt.
            json_schema_str = json.dumps(func_spec.json_schema, indent=2)
            ollama_prompt = (
                f"{system_message}\n\n"
                "IMPORTANT: You MUST respond in the following JSON format. "
                "Do not include any other text, reasoning, or explanations outside of the JSON structure.\n"
                "JSON Schema:\n"
                f"```json\n{json_schema_str}\n```\n"
                "Your JSON response:\n"
            )
            messages = opt_messages_to_list(ollama_prompt, user_message)
            # Remove tool-related kwargs for Ollama
            filtered_kwargs.pop("tools", None)
            filtered_kwargs.pop("tool_choice", None)
        # --- End Ollama fix ---
    else:
        if func_spec is not None:
            filtered_kwargs["tools"] = [func_spec.as_openai_tool_dict]
            filtered_kwargs["tool_choice"] = func_spec.openai_tool_choice_dict
=======

    if func_spec is not None:
        filtered_kwargs["tools"] = [func_spec.as_openai_tool_dict]
        # force the model to use the function
        filtered_kwargs["tool_choice"] = func_spec.openai_tool_choice_dict

    if filtered_kwargs.get("model", "").startswith("ollama/"):
       filtered_kwargs["model"] = filtered_kwargs["model"].replace("ollama/", "")
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce

    t0 = time.time()
    completion = backoff_create(
        client.chat.completions.create,
        OPENAI_TIMEOUT_EXCEPTIONS,
        messages=messages,
        **filtered_kwargs,
    )
    req_time = time.time() - t0

    choice = completion.choices[0]

<<<<<<< HEAD
    # --- Ollama: Parse response fix ---
    if func_spec is None or (not is_ollama):
        # Original logic for OpenAI (with tools) or non-tool calls
        if func_spec is None:
            output = choice.message.content
        else:
            assert (
                choice.message.tool_calls
            ), f"function_call is empty, it is not a function call: {choice.message}"
            assert (
                choice.message.tool_calls[0].function.name == func_spec.name
            ), "Function name mismatch"
            try:
                print(f"[cyan]Raw func call response: {choice}[/cyan]")
                output = json.loads(choice.message.tool_calls[0].function.arguments)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Error decoding the function arguments: {choice.message.tool_calls[0].function.arguments}"
                )
                raise e
    else:
        # Ollama: Parse JSON from text response [cite: 3018]
        raw_output = choice.message.content
        output = _extract_json_from_ollama(raw_output)
        if output is None:
            logger.error(f"Failed to parse JSON from Ollama response. Raw output: {raw_output}")
            # Raise an error similar to OpenAI's tool call failure
            raise json.JSONDecodeError(f"Ollama response was not valid JSON: {raw_output}", raw_output, 0)
    # --- End Ollama fix ---
=======
    if func_spec is None:
        output = choice.message.content
    else:
        assert (
            choice.message.tool_calls
        ), f"function_call is empty, it is not a function call: {choice.message}"
        assert (
            choice.message.tool_calls[0].function.name == func_spec.name
        ), "Function name mismatch"
        try:
            print(f"[cyan]Raw func call response: {choice}[/cyan]")
            output = json.loads(choice.message.tool_calls[0].function.arguments)
        except json.JSONDecodeError as e:
            logger.error(
                f"Error decoding the function arguments: {choice.message.tool_calls[0].function.arguments}"
            )
            raise e
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce

    in_tokens = completion.usage.prompt_tokens
    out_tokens = completion.usage.completion_tokens

    info = {
        "system_fingerprint": completion.system_fingerprint,
        "model": completion.model,
        "created": completion.created,
    }

<<<<<<< HEAD
    return output, req_time, in_tokens, out_tokens, info
=======
    return output, req_time, in_tokens, out_tokens, info
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce
