
import logging
from typing import Optional, Dict, Any
import requests
from superset import db
from superset.models.ai import AIProviderConfig

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self) -> None:
        self._config = self._get_active_config()

    def _get_active_config(self) -> Optional[AIProviderConfig]:
        """Fetch the currently active AI provider configuration."""
        return db.session.query(AIProviderConfig).filter_by(is_active=True).first()

    def is_configured(self) -> bool:
        return self._config is not None

    def query(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Send a query to the configured LLM provider.
        Returns a dict with 'text' and/or 'sql'.
        """
        if not self._config:
            raise ValueError("No active AI Provider configuration found.")

        provider = self._config.provider.lower()
        api_key = self._config.api_key
        model = self._config.model_name

        if provider == 'openai':
            return self._query_openai(api_key, model, system_prompt, user_prompt)
        elif provider == 'gemini':
            return self._query_gemini(api_key, model, system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _query_openai(self, api_key: str, model: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call OpenAI Chat Completion API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1  # Low temperature for SQL generation
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data['choices'][0]['message']['content']
            return self._parse_response(content)
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            raise

    def _query_gemini(self, api_key: str, model: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call Google Gemini API."""
        # Simplified implementation using direct REST API if google-generativeai is not installed
        # Note: Depending on the specific Gemini model version, the URL might change.
        # Assumes standard Gemini Pro usage.

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUser Question: {user_prompt}"}]
            }]
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data['candidates'][0]['content']['parts'][0]['text']
            return self._parse_response(content)
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            raise

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Heuristic to extract SQL from Markdown code blocks.
        """
        sql_query = None
        response_text = content

        if "```sql" in content:
            parts = content.split("```sql")
            if len(parts) > 1:
                sql_block = parts[1].split("```")[0].strip()
                sql_query = sql_block
                # remove the SQL block from text to avoid duplication if desired,
                # or keep it as explanation.

        return {
            "response": response_text,
            "sql_query": sql_query
        }
