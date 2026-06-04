from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from app.core.models import ChatMessage


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> str:
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        pass


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview") -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> str:
        formatted_messages = [{"role": msg.role.value, "content": msg.content} for msg in messages]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        formatted_messages = [{"role": msg.role.value, "content": msg.content} for msg in messages]
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def count_tokens(self, text: str) -> int:
        import tiktoken

        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229") -> None:
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> str:
        formatted_messages = [{"role": msg.role.value, "content": msg.content} for msg in messages]
        response = await self.client.messages.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return response.content[0].text

    async def stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        formatted_messages = [{"role": msg.role.value, "content": msg.content} for msg in messages]
        async with self.client.messages.stream(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def count_tokens(self, text: str) -> int:
        response = await self.client.count_tokens(text)
        return response.count


class MockLLMProvider(LLMProvider):
    async def generate(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> str:
        import asyncio

        await asyncio.sleep(0.5)
        last_message = messages[-1].content if messages else ""
        return (
            f"[DEMO MODE] Mock response to: '{last_message[:50]}...'. "
            "This is a simulated AI response. In production mode with API keys, "
            "you would receive real LLM-generated content with proper reasoning and citations."
        )

    async def stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        import asyncio

        last_message = messages[-1].content if messages else ""
        response = (
            f"[DEMO MODE] Mock streaming response to: '{last_message[:50]}...'. "
            "This is a simulated AI response. In production mode with API keys, "
            "you would receive real LLM-generated content with proper reasoning and citations."
        )
        words = response.split()
        for word in words:
            await asyncio.sleep(0.05)
            yield word + " "

    async def count_tokens(self, text: str) -> int:
        return len(text.split())
