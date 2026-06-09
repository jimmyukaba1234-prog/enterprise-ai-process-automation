"""
Gemini Model Client.

This file is responsible only for communicating with the LLM.

Model usage in this project:
1. Gemini model = reasoning, intent extraction, response generation.
2. SentenceTransformer model = embeddings for FAISS knowledge retrieval.
3. Simulated APIs = banking data/tools, not AI models.
"""

import os
import json
import logging
from typing import Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv


#load_dotenv()
load_dotenv(override=True)

logger = logging.getLogger(__name__)


class GeminiModelClient:
    """
    Wrapper around Gemini so the rest of the chatbot does not directly
    depend on the Gemini SDK.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 2048
    ):

        self.api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self.model_name = (
            model_name
            or os.getenv(
                "GEMINI_MODEL",
                "gemini-2.0-flash"
            )
        )

        print(
            f"Using Gemini model: {self.model_name}"
        )

        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables."
            )

        genai.configure(
            api_key=self.api_key
        )

        self.model = genai.GenerativeModel(
            model_name=self.model_name
        )

    
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Generates normal text response from Gemini.
        """

        final_prompt = self._build_prompt(
            prompt,
            system_instruction
        )

        try:
            response = self.model.generate_content(
                final_prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_output_tokens,
                }
            )

            text = (
                response.text.strip()
                if response.text
                else ""
            )

            return {
                "success": True,
                "model": self.model_name,
                "response_type": "text",
                "text": text,
                "error": None
            }

        except Exception as e:
            logger.exception(
                "Gemini text generation failed."
            )

            return {
                "success": False,
                "model": self.model_name,
                "response_type": "text",
                "text": "",
                "error": str(e)
            }



    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_retries: int = 1
    ) -> dict[str, Any]:
        """
        Generates structured JSON response from Gemini with retry handling.
        """


        final_prompt = self._build_prompt(prompt, system_instruction)

        last_error = None
        last_raw_text = ""

        for attempt in range(1, max_retries + 1):
            try:
                response = self.model.generate_content(
                    final_prompt,
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_output_tokens,
                        "response_mime_type": "application/json",
                    }
                )

                raw_text = response.text.strip() if response.text else "{}"
                last_raw_text = raw_text

                parsed_json = self._clean_json_response(raw_text)

                if parsed_json.get("success") is False and parsed_json.get("error"):
                    last_error = parsed_json.get("error")
                    logger.warning(
                        "Gemini JSON parse failed on attempt %s/%s. Error: %s",
                        attempt,
                        max_retries,
                        last_error
                    )
                    continue

                return {
                    "success": True,
                    "model": self.model_name,
                    "response_type": "json",
                    "data": parsed_json,
                    "raw_text": raw_text,
                    "attempts": attempt,
                    "error": None
                    #"error": last_error or "Gemini is currently unavailable or quota has been exhausted."
                }

            except Exception as e:
                last_error = str(e)

                logger.exception(
                    "Gemini JSON generation failed on attempt %s/%s.",
                    attempt,
                    max_retries
                )

                continue

        return {
            "success": False,
            "model": self.model_name,
            "response_type": "json",
            "data": {},
            "raw_text": last_raw_text,
            "attempts": max_retries,
            "error": last_error or "Gemini JSON generation failed after retries."
        }



    

    def health_check(self) -> dict[str, Any]:
        """
        Checks whether Gemini is reachable before the chatbot starts.
        """
        try:
            response = self.model.generate_content(
                "Reply with only: OK",
                generation_config={
                    "temperature": 0,
                    "max_output_tokens": 10,
                }
            )

            text = response.text.strip() if response.text else ""

            return {
                "success": True,
                "model": self.model_name,
                "status": "available",
                "response": text,
                "error": None
            }

        except Exception as e:
            logger.exception("Gemini health check failed.")

            return {
                "success": False,
                "model": self.model_name,
                "status": "unavailable",
                "response": "",
                "error": str(e)
            }

    def _build_prompt(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Combines system instruction and user/task prompt.
        """
        if system_instruction:
            return f"{system_instruction.strip()}\n\n{prompt.strip()}"

        return prompt.strip()

    def _clean_json_response(self, raw_text: str) -> dict[str, Any]:
        """
        Cleans and parses Gemini JSON output.
        Handles cases where model wraps JSON in markdown.
        """
        cleaned = raw_text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "").strip()

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse Gemini JSON response. Error: %s | Raw response: %s",
                str(e),
                raw_text
            )

            return {
                "success": False,
                "error": "Invalid JSON returned by model.",
                "raw_response": raw_text
            }