"""LLM utilities for interacting with OpenAI and Anthropic APIs."""

import os
from typing import Any, Dict, List, Optional, Union
from anthropic import Anthropic, AsyncAnthropic
from openai import OpenAI, AsyncOpenAI
from ..config.settings import settings


class LLMClient:
    """Unified client for interacting with LLM providers."""

    def __init__(
        self,
        provider: str = "anthropic",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize LLM client.

        Args:
            provider: Either 'openai' or 'anthropic'
            model: Model name (defaults based on provider)
            api_key: API key (falls back to settings if not provided)
        """
        self.provider = provider.lower()

        if self.provider == "anthropic":
            self.model = model or "claude-3-5-sonnet-20241022"
            self.api_key = api_key or settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if self.api_key:
                self.client = Anthropic(api_key=self.api_key)
                self.async_client = AsyncAnthropic(api_key=self.api_key)
            else:
                self.client = None
                self.async_client = None
        elif self.provider == "openai":
            self.model = model or "gpt-4-turbo-preview"
            self.api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
                self.async_client = AsyncOpenAI(api_key=self.api_key)
            else:
                self.client = None
                self.async_client = None
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def is_available(self) -> bool:
        """Check if LLM client is properly configured."""
        return self.client is not None and self.api_key is not None

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Synchronous completion.

        Args:
            prompt: User prompt
            system: System message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text response
        """
        if not self.is_available():
            raise RuntimeError(f"LLM client not configured. Please set API key for {self.provider}")

        if self.provider == "anthropic":
            messages = [{"role": "user", "content": prompt}]
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=messages,
                **kwargs,
            )
            return response.content[0].text
        else:  # openai
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            return response.choices[0].message.content

    async def acomplete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Async completion.

        Args:
            prompt: User prompt
            system: System message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text response
        """
        if not self.is_available():
            raise RuntimeError(f"LLM client not configured. Please set API key for {self.provider}")

        if self.provider == "anthropic":
            messages = [{"role": "user", "content": prompt}]
            response = await self.async_client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=messages,
                **kwargs,
            )
            return response.content[0].text
        else:  # openai
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            return response.choices[0].message.content

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Multi-turn chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text response
        """
        if not self.is_available():
            raise RuntimeError(f"LLM client not configured. Please set API key for {self.provider}")

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=messages,
                **kwargs,
            )
            return response.content[0].text
        else:  # openai
            full_messages = []
            if system:
                full_messages.append({"role": "system", "content": system})
            full_messages.extend(messages)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            return response.choices[0].message.content

    async def achat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Async multi-turn chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text response
        """
        if not self.is_available():
            raise RuntimeError(f"LLM client not configured. Please set API key for {self.provider}")

        if self.provider == "anthropic":
            response = await self.async_client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=messages,
                **kwargs,
            )
            return response.content[0].text
        else:  # openai
            full_messages = []
            if system:
                full_messages.append({"role": "system", "content": system})
            full_messages.extend(messages)

            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            return response.choices[0].message.content


# Global LLM client instances
_default_client: Optional[LLMClient] = None


def get_llm_client(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> LLMClient:
    """Get or create an LLM client instance.

    Args:
        provider: LLM provider ('openai' or 'anthropic')
        model: Model name
        api_key: API key

    Returns:
        LLMClient instance
    """
    global _default_client

    # If no specific config provided, return cached default
    if not any([provider, model, api_key]) and _default_client is not None:
        return _default_client

    # Determine provider priority: param > env var > setting
    if not provider:
        if settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif settings.openai_api_key or os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            provider = "anthropic"  # Default fallback

    client = LLMClient(provider=provider, model=model, api_key=api_key)

    # Cache as default if no specific config
    if not any([provider, model, api_key]):
        _default_client = client

    return client
