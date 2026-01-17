"""Groq LLM provider implementation."""

from groq import AsyncGroq
from app.providers.base import LLMProvider, LLMResponse
from app.config import settings
from typing import Optional, List, Dict


class GroqLLMProvider(LLMProvider):
    """Groq LLM provider for conversation generation."""

    def __init__(self):
        """Initialize Groq client."""
        if not settings.groq_api_key:
            raise ValueError("Groq API key not configured")

        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text completion using Groq.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Call Groq API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        return LLMResponse(
            text=response.choices[0].message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Chat completion with conversation history.

        Args:
            messages: Conversation history [{"role": "user|assistant", "content": "..."}]
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated text
        """
        chat_messages = []

        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        chat_messages.extend(messages)

        # Call Groq API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        return LLMResponse(
            text=response.choices[0].message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason
        )

    async def generate_conversation_response(
        self,
        conversation_history: List[Dict[str, str]],
        situation_context: str,
        user_weak_phonemes: List[str],
        vocabulary: List[str]
    ) -> str:
        """
        Generate contextual conversation response targeting user's weak areas.

        Args:
            conversation_history: Previous messages in the conversation
            situation_context: Description of the current situation
            user_weak_phonemes: Phonemes the user struggles with
            vocabulary: Relevant vocabulary for this situation

        Returns:
            Generated response text in Tamil
        """
        # Build system prompt for Tamil conversation
        weak_phonemes_str = ", ".join(user_weak_phonemes) if user_weak_phonemes else "none identified yet"
        vocab_str = ", ".join(vocabulary[:10]) if vocabulary else ""

        system_prompt = f"""You are a Tamil language conversation partner helping a learner practice speaking.

Context: {situation_context}

The learner has difficulty with these Tamil phonemes: {weak_phonemes_str}

Relevant vocabulary for this situation: {vocab_str}

Instructions:
1. Respond naturally in Tamil to continue the conversation
2. Keep responses concise (1-2 sentences)
3. When possible, naturally include words containing the learner's weak phonemes for practice
4. Use vocabulary appropriate for the situation
5. Be encouraging and patient
6. Respond ONLY in Tamil (no English unless absolutely necessary)"""

        response = await self.chat(
            messages=conversation_history,
            system_prompt=system_prompt,
            max_tokens=150,
            temperature=0.8
        )

        return response.text
