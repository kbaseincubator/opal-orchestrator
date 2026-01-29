"""LLM service using CBORG API with Anthropic SDK."""

import json
from typing import Any, Optional

from anthropic import Anthropic

from app.config import get_settings


class LLMRefusalError(Exception):
    """Raised when the LLM refuses to generate content."""
    pass


class LLMService:
    """Service for LLM interactions via CBORG."""

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[Anthropic] = None

    @property
    def client(self) -> Anthropic:
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            self._client = Anthropic(
                api_key=self.settings.anthropic_auth_token,
                base_url=self.settings.anthropic_base_url,
            )
        return self._client

    def generate(
        self,
        messages: list[dict],
        system: Optional[str] = None,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> dict:
        """Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            tools: Optional list of tool definitions for function calling
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Response dict with 'content', 'tool_calls', and 'usage'
        """
        kwargs: dict[str, Any] = {
            "model": self.settings.llm_model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        if system:
            kwargs["system"] = system

        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)

        # Check if the LLM refused to generate content
        if response.stop_reason == "refusal":
            raise LLMRefusalError("LLM refused to generate content due to safety guidelines.")

        result = {
            "content": "",
            "tool_calls": [],
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "stop_reason": response.stop_reason,
        }

        for block in response.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                result["tool_calls"].append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        return result

    async def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system: Optional[str] = None,
        max_iterations: int = 10,
        tool_executor: Optional[callable] = None,
    ) -> dict:
        """Generate a response with tool use loop.

        Args:
            messages: Initial messages
            tools: Tool definitions
            system: System prompt
            max_iterations: Max tool call iterations
            tool_executor: Async function to execute tools (name, input) -> result

        Returns:
            Final response after tool use loop
        """
        import logging
        logger = logging.getLogger(__name__)

        current_messages = list(messages)
        all_tool_results = []

        for _ in range(max_iterations):
            response = self.generate(
                messages=current_messages,
                system=system,
                tools=tools,
            )

            if not response["tool_calls"]:
                response["all_tool_results"] = all_tool_results
                return response

            # Add assistant message with tool calls
            assistant_content = []
            if response["content"]:
                assistant_content.append({
                    "type": "text",
                    "text": response["content"],
                })
            for tool_call in response["tool_calls"]:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tool_call["id"],
                    "name": tool_call["name"],
                    "input": tool_call["input"],
                })

            current_messages.append({
                "role": "assistant",
                "content": assistant_content,
            })

            # Execute tools and add results
            tool_results = []
            for tool_call in response["tool_calls"]:
                if tool_executor:
                    try:
                        result = await tool_executor(tool_call["name"], tool_call["input"])
                    except Exception as e:
                        logger.error(f"Tool execution error for {tool_call['name']}: {e}", exc_info=True)
                        result = {"error": str(e)}
                else:
                    result = {"error": "No tool executor provided"}

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call["id"],
                    "content": json.dumps(result) if isinstance(result, dict) else str(result),
                })
                all_tool_results.append({
                    "tool_name": tool_call["name"],
                    "tool_input": tool_call["input"],
                    "tool_result": result,
                })

            current_messages.append({
                "role": "user",
                "content": tool_results,
            })

        # Max iterations reached
        response["all_tool_results"] = all_tool_results
        return response

    async def agenerate(
        self,
        messages: list[dict],
        system: Optional[str] = None,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> dict:
        """Async version of generate (uses sync client internally)."""
        # For now, wrap sync call - can be made truly async later
        return self.generate(
            messages=messages,
            system=system,
            tools=tools,
            max_tokens=max_tokens,
            temperature=temperature,
        )


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
