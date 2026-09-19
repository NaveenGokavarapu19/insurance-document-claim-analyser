from __future__ import annotations

import json
from typing import Any

import boto3


class BedrockClient:
    """Bedrock Runtime wrapper that reuses an injected boto3 session.

    The caller owns session creation and lifecycle; this class only consumes the
    provided session and never creates hidden internal sessions.
    """

    def __init__(
        self,
        model_id: str,
        session: boto3.session.Session,
        region_name: str | None = None,
    ) -> None:
        """Create a Bedrock wrapper bound to the provided session."""
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError("model_id must be a non-empty string.")
        if session is None:
            raise ValueError("session must be provided.")

        self.model_id = model_id.strip()
        self.session = session
        self.region_name = region_name or session.region_name
        self._runtime_client = self.session.client(
            "bedrock-runtime",
            region_name=self.region_name,
        )

    def converse(
        self,
        *,
        prompt: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Call Bedrock Converse and return both raw output and extracted text.

        Provide either prebuilt messages or a prompt. If only prompt is provided,
        it is normalized into a single user message payload.
        """
        request_messages = messages or self._messages_from_prompt(prompt)
        response = self._runtime_client.converse(
            modelId=self.model_id,
            messages=request_messages,
            **kwargs,
        )
        return {
            "raw_response": response,
            "text": self._extract_converse_text(response),
        }

    def invoke(
        self,
        *,
        body: dict[str, Any] | str,
        content_type: str = "application/json",
        accept: str = "application/json",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Call Bedrock InvokeModel and return raw plus parsed payload."""
        serialized_body = body if isinstance(body, str) else json.dumps(body)
        response = self._runtime_client.invoke_model(
            modelId=self.model_id,
            body=serialized_body,
            contentType=content_type,
            accept=accept,
            **kwargs,
        )

        return {
            "raw_response": response,
            "parsed_body": self._parse_invoke_body(response),
        }

    def _messages_from_prompt(self, prompt: str | None) -> list[dict[str, Any]]:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Either messages or a non-empty prompt must be provided.")

        return [
            {
                "role": "user",
                "content": [{"text": prompt.strip()}],
            }
        ]

    def _extract_converse_text(self, response: dict[str, Any]) -> str:
        content = response.get("output", {}).get("message", {}).get("content", [])
        text_parts = [item.get("text", "") for item in content if isinstance(item, dict)]
        return " ".join(part for part in text_parts if part)

    def _parse_invoke_body(self, response: dict[str, Any]) -> Any:
        body_stream = response.get("body")
        if body_stream is None:
            return None

        raw_bytes = body_stream.read() if hasattr(body_stream, "read") else body_stream
        if isinstance(raw_bytes, bytes):
            raw_text = raw_bytes.decode("utf-8")
        else:
            raw_text = str(raw_bytes)

        try:
            return json.loads(raw_text)
        except Exception:
            return raw_text
