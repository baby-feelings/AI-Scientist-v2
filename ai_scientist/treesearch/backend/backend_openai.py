import json
import logging
import time

from .utils import FunctionSpec, OutputType, opt_messages_to_list, backoff_create
from funcy import notnone, once, select_values
import openai
from rich import print

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
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # <-- 既存の修正
            max_retries=max_retries
        )
    else:
        client = openai.OpenAI(max_retries=max_retries)
    return client


def query(
    system_message: str | None,
    user_message: str | None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
) -> tuple[OutputType, float, int, int, dict]:
    client = get_ai_client(model_kwargs.get("model"), max_retries=0)
    filtered_kwargs: dict = select_values(notnone, model_kwargs)  # type: ignore

    messages = opt_messages_to_list(system_message, user_message)

    # --- OLLAMA FIX: START ---
    is_ollama = filtered_kwargs.get("model", "").startswith("ollama/")

    if func_spec is not None:
        if is_ollama:
            # Ollamaは 'tools' と 'tool_choice' をサポートしていないため、渡さない
            # (parallel_agent.py側で func_spec=None になっているはずだが、ここで二重に防ぐ)
            pass
        else:
            # OpenAI/Anthropicの場合は従来通り設定
            filtered_kwargs["tools"] = [func_spec.as_openai_tool_dict]
            # force the model to use the function
            filtered_kwargs["tool_choice"] = func_spec.openai_tool_choice_dict

    if is_ollama:
       filtered_kwargs["model"] = filtered_kwargs["model"].replace("ollama/", "")
       # Ollamaがサポートしていない引数をAPIコールから確実に削除
       filtered_kwargs.pop("tools", None)
       filtered_kwargs.pop("tool_choice", None)
    # --- OLLAMA FIX: END ---


    t0 = time.time()
    completion = backoff_create(
        client.chat.completions.create,
        OPENAI_TIMEOUT_EXCEPTIONS,
        messages=messages,
        **filtered_kwargs,
    )
    req_time = time.time() - t0

    choice = completion.choices[0]

    # --- OLLAMA FIX: START ---
    # Ollamaは常にテキスト応答として扱う (func_specがNoneのため)
    if func_spec is None or is_ollama:
        output = choice.message.content
    # --- OLLAMA FIX: END ---
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

    in_tokens = completion.usage.prompt_tokens
    out_tokens = completion.usage.completion_tokens

    info = {
        "system_fingerprint": completion.system_fingerprint,
        "model": completion.model,
        "created": completion.created,
    }

    return output, req_time, in_tokens, out_tokens, info