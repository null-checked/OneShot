"""
This module provides a unified client for interacting with various Large Language Models (LLMs)
such as Ollama, OpenAI, and other OpenAI-compatible APIs.
"""

import requests
import json
from abc import ABC, abstractmethod
from typing import Generator, Optional, List

from openai import OpenAI, OpenAIError

from config import Settings, settings


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generates a response from the LLM."""
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        """Generates a streaming response from the LLM."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the LLM provider is available."""
        pass
    
    def get_models(self) -> List[str]:
        """Gets a list of available models from the provider.
           Returns an empty list if not applicable by default."""
        return []


class OllamaClient(BaseLLMClient):
    """Client for Ollama LLMs."""

    def __init__(self, config: Settings):
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL

    def _generate_request_payload(self, prompt: str, system: Optional[str], stream: bool, temperature: float = 0.7):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        return {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generates a response from the Ollama model."""
        payload = self._generate_request_payload(prompt, system, stream=False, temperature=temperature)
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["message"]["content"].strip()
        except (requests.RequestException, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to communicate with Ollama: {e}") from e

    def generate_stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        """Generates a streaming response from the Ollama model."""
        payload = self._generate_request_payload(prompt, system, stream=True)
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, stream=True, timeout=60)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'message' in chunk and 'content' in chunk['message']:
                        yield chunk['message']['content']
        except (requests.RequestException, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to stream from Ollama: {e}") from e

    def is_available(self) -> bool:
        """Checks if the Ollama server is running."""
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
            
    def get_models(self) -> List[str]:
        """Gets a list of available models from the Ollama server."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model['name'] for model in models]
        except (requests.RequestException, json.JSONDecodeError):
            return []


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI API."""

    def __init__(self, config: Settings):
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL

    def _prepare_messages(self, prompt: str, system: Optional[str]):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generates a response from the OpenAI model."""
        messages = self._prepare_messages(prompt, system)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except OpenAIError as e:
            raise RuntimeError(f"Failed to communicate with OpenAI: {e}") from e


    def generate_stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        """Generates a streaming response from the OpenAI model."""
        messages = self._prepare_messages(prompt, system)
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except OpenAIError as e:
            raise RuntimeError(f"Failed to stream from OpenAI: {e}") from e

    def is_available(self) -> bool:
        """Checks if the OpenAI API is accessible."""
        try:
            self.client.models.list()
            return True
        except OpenAIError:
            return False
            
    def get_models(self) -> List[str]:
        """Gets a list of available models from the provider."""
        try:
            return [model.id for model in self.client.models.list().data]
        except OpenAIError:
            return []


class OpenAICompatibleClient(BaseLLMClient):
    """Client for any OpenAI-compatible API (e.g., vLLM, LocalAI)."""

    def __init__(self, config: Settings):
        if not config.CUSTOM_BASE_URL or not config.CUSTOM_MODEL:
            raise ValueError("CUSTOM_BASE_URL and CUSTOM_MODEL must be set for the custom provider.")
        self.client = OpenAI(
            base_url=config.CUSTOM_BASE_URL,
            api_key=config.CUSTOM_API_KEY or "not-needed"
        )
        self.model = config.CUSTOM_MODEL

    def _prepare_messages(self, prompt: str, system: Optional[str]):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generates a response from the custom model."""
        messages = self._prepare_messages(prompt, system)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except OpenAIError as e:
            raise RuntimeError(f"Failed to communicate with custom LLM endpoint: {e}") from e

    def generate_stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        """Generates a streaming response from the custom model."""
        messages = self._prepare_messages(prompt, system)
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except OpenAIError as e:
            raise RuntimeError(f"Failed to stream from custom LLM endpoint: {e}") from e


    def is_available(self) -> bool:
        """Checks if the custom API is accessible."""
        try:
            self.client.models.list()
            return True
        except (OpenAIError, requests.exceptions.RequestException):
            return False

    def get_models(self) -> List[str]:
        """Gets a list of available models from the provider."""
        try:
            return [model.id for model in self.client.models.list().data]
        except (OpenAIError, requests.exceptions.RequestException):
            return []


def create_llm_client(config: Settings = settings) -> BaseLLMClient:
    """
    Factory function to create an LLM client based on the provider specified in the settings.

    Args:
        config: The application settings.

    Returns:
        An instance of a BaseLLMClient implementation.

    Raises:
        ValueError: If the LLM provider is unknown.
    """
    if config.LLM_PROVIDER == "ollama":
        return OllamaClient(config)
    elif config.LLM_PROVIDER == "openai":
        return OpenAIClient(config)
    elif config.LLM_PROVIDER == "custom":
        return OpenAICompatibleClient(config)
    else:
        raise ValueError(f"Unknown LLM provider: {config.LLM_PROVIDER}")