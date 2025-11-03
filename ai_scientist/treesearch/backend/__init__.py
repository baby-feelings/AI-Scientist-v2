from . import backend_anthropic, backend_openai
from .utils import FunctionSpec, OutputType, PromptType, compile_prompt_to_md
<<<<<<< HEAD
import json
import logging
from ...llm import extract_json_between_markers
logger = logging.getLogger("ai-scientist")


=======
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce

def get_ai_client(model: str, **model_kwargs):
    """
    Get the appropriate AI client based on the model string.

    Args:
        model (str): string identifier for the model to use (e.g. "gpt-4-turbo")
        **model_kwargs: Additional keyword arguments for model configuration.
    Returns:
        An instance of the appropriate AI client.
    """
    if "claude-" in model:
        return backend_anthropic.get_ai_client(model=model, **model_kwargs)
    else:
        return backend_openai.get_ai_client(model=model, **model_kwargs)

def query(
    system_message: PromptType | None,
    user_message: PromptType | None,
    model: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
) -> OutputType:
    """
    General LLM query for various backends with a single system and user message.
    Supports function calling for some backends.

    Args:
        system_message (PromptType | None): Uncompiled system message (will generate a message following the OpenAI/Anthropic format)
        user_message (PromptType | None): Uncompiled user message (will generate a message following the OpenAI/Anthropic format)
        model (str): string identifier for the model to use (e.g. "gpt-4-turbo")
        temperature (float | None, optional): Temperature to sample at. Defaults to the model-specific default.
        max_tokens (int | None, optional): Maximum number of tokens to generate. Defaults to the model-specific max tokens.
        func_spec (FunctionSpec | None, optional): Optional FunctionSpec object defining a function call. If given, the return value will be a dict.

    Returns:
        OutputType: A string completion if func_spec is None, otherwise a dict with the function call details.
    """

    model_kwargs = model_kwargs | {
        "model": model,
        "temperature": temperature,
    }

<<<<<<< HEAD
    # --- 修正開始 ---
    is_ollama = model.startswith("ollama/")
    ollama_func_spec_used = False # Ollama + func_spec が使われたかどうかのフラグ

    if is_ollama and func_spec is not None:
        ollama_func_spec_used = True
        
        json_schema_str = json.dumps(func_spec.json_schema, indent=2)
        # OllamaモデルにJSONを強制するためのプロンプト指示
        prompt_injection = (
            f"\n\nIMPORTANT:\nYou must provide your response *only* in a JSON format "
            f"that strictly adheres to the following JSON schema. "
            f"Do not include any other text, reasoning, explanations, or markdown formatting (like ```json). "
            f"Your entire response must be a single, valid JSON object that matches the schema.\n\n"
            f"SCHEMA:\n{json_schema_str}\n\n"
            f"JSON Response:"
        )
        
        # ユーザーメッセージに追加（存在しない場合はシステムメッセージに追加）
        if user_message:
            if isinstance(user_message, str):
                user_message += prompt_injection
            elif isinstance(user_message, dict):
                user_message["json_instructions"] = prompt_injection
        elif system_message:
            if isinstance(system_message, str):
                system_message += prompt_injection
            elif isinstance(system_message, dict):
                system_message["json_instructions"] = prompt_injection
        else:
            system_message = {"json_instructions": prompt_injection}

        func_spec = None # backend_openai.py に func_spec を渡さないようにする
    # --- 修正終了 ---
=======
    # Handle models with beta limitations
    # ref: https://platform.openai.com/docs/guides/reasoning/beta-limitations
    if model.startswith("o1"):
        if system_message and user_message is None:
            user_message = system_message
        elif system_message is None and user_message:
            pass
        elif system_message and user_message:
            system_message["Main Instructions"] = {}
            system_message["Main Instructions"] |= user_message
            user_message = system_message
        system_message = None
        # model_kwargs["temperature"] = 0.5
        model_kwargs["reasoning_effort"] = "high"
        model_kwargs["max_completion_tokens"] = 100000  # max_tokens
        # remove 'temperature' from model_kwargs
        model_kwargs.pop("temperature", None)
    else:
        model_kwargs["max_tokens"] = max_tokens
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce

    query_func = backend_anthropic.query if "claude-" in model else backend_openai.query
    output, req_time, in_tok_count, out_tok_count, info = query_func(
        system_message=compile_prompt_to_md(system_message) if system_message else None,
        user_message=compile_prompt_to_md(user_message) if user_message else None,
<<<<<<< HEAD
        func_spec=func_spec, # Ollamaの場合は None になっている
        **model_kwargs,
    )

    # --- 修正開始 ---
    # OllamaモデルがJSONを返すことを期待していた場合、文字列レスポンスをパースする
    if ollama_func_spec_used:
        if not isinstance(output, str):
            logger.error(f"Ollama response was not a string as expected: {output}")
            raise ValueError("Expected string output from Ollama, but got non-string.")
        
        # llm.py からインポートした関数でJSONを抽出
        parsed_json = extract_json_between_markers(output)
        
        if parsed_json:
            logger.info("Successfully parsed JSON from Ollama response (using markers).")
            return parsed_json
        else:
            # マーカーなしのプレーンなJSONとしてパースを試みる
            try:
                parsed_json = json.loads(output)
                logger.info("Successfully parsed JSON from Ollama response (plain text).")
                return parsed_json
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Ollama response. Raw output: {output}")
                raise ValueError(f"Ollama response was not valid JSON: {output}")
                
    return output
=======
        func_spec=func_spec,
        **model_kwargs,
    )

    return output
>>>>>>> 0af221afc7282ddfc826acae6302d42711d7d4ce
