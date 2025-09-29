import logging
from typing import Literal, get_origin, get_args

import lmstudio
from fastmcp.client.sampling import (
    SamplingMessage,
    SamplingParams,
    RequestContext,
)

from mcp_llamaindex.config import settings

llm = lmstudio.llm(settings.summary_model)


def input_given_type(expected_type, message_prefix: str | None = None):
    if message_prefix is None:
        message_prefix = ""

    if expected_type is bool:
        message = "Accept or reject (Y/N) : "
        user_input = input(message_prefix + message)
        if user_input.upper().strip() == "Y":
            return True
        elif user_input.upper().strip() == "N":
            return False
        else:
            raise ValueError("Invalid input. Please enter Y or N.")
    elif expected_type in [str, int, float]:
        message = f"Enter a value of type {expected_type} : "
        user_input = input(message_prefix + message)
        return expected_type(user_input)
    elif get_origin(expected_type) is Literal:
        message = f"Select a value from {get_args(expected_type)} : "
        return input(message_prefix + message)
    elif expected_type is dict:
        return input_given_properties(expected_type)
    else:
        raise NotImplementedError(f"type {expected_type} not supported yet.")


def input_given_properties(properties: dict):
    return {
        prop_name: input_given_type(prop, f"For {prop_name} : ")
        for prop_name, prop in properties.items()
    }


async def elicitation_handler(
    message: str,
    response_type: type,
    params,
    context,
):
    logging.warning(f"Elicitation handler called with message: {message}")
    # Present the message to the user and collect input
    if response_type is None:
        user_input = None
    else:
        properties = response_type.__dict__["__annotations__"]
        user_input = input_given_properties(properties)

    # Create response using the provided dataclass type
    if response_type is None:
        return None
    else:
        return user_input


async def sampling_handler(
    messages: list[SamplingMessage], params: SamplingParams, context: RequestContext
) -> str:
    logging.warning(f"Sampling handler operation with message: {messages}")
    messages = [f"Message {i}:\n{m.content.text}" for i, m in enumerate(messages)]
    message = "\n\n".join(messages)

    response = llm.respond(
        message + " /no_think"
    )  # /no_think for qwen3 models : https://huggingface.co/lmstudio-community/Qwen3-0.6B-GGUF
    logging.warning(f"LLM response: {response.content}")
    return response.content
