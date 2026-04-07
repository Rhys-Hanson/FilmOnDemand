import os
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def generate_movie_recommendations(prompt: str, services: Optional[List[str]] = None) -> List[str]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not found in environment. Using fallback empty AI response.")
        return []

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        services_instruction = ""
        if services:
            services_instruction = f" The movies must be available on these streaming platforms: {', '.join(services)}."

        system_instruction = (
            "You are a helpful movie recommendation AI."
            " You must return EXACTLY AND ONLY a JSON list of strings containing movie titles based on the user's prompt."
            " Return just the JSON array of strings (e.g. ['Inception', 'Batman']), no markdown formatting, no fluff."
            + services_instruction
        )
        
        # Fallback list based on your account's available models
        available_models = ['gemini-2.0-flash', 'gemini-flash-latest', 'gemini-2.0-flash-lite']
        response = None
        last_error = None

        for model_id in available_models:
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        system_instruction=system_instruction,
                        response_mime_type="application/json"
                    ),
                )
                if response:
                    break
            except Exception as e:
                last_error = e
                # If it's a 404, we just try the next model silently
                if "404" in str(e):
                    continue
                # If it's a 429, we still try the next model in case it has its own quota
                if "429" in str(e):
                    continue
                raise e

        if not response:
            if last_error:
                raise last_error
            return []
            
        text_response = response.text
        if not text_response:
            return []
            
        try:
            titles = json.loads(text_response)
            if isinstance(titles, list):
                return [str(title) for title in titles]
            elif isinstance(titles, dict) and "titles" in titles:
                return [str(title) for title in titles.get("titles", [])]
            return []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {text_response}")
            return []

    except ImportError:
        logger.error("google-genai package is not installed.")
        return []
    except Exception as e:
        # Check if this is a 429/Rate Limit error to log it cleanly
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            logger.warning("Gemini API rate limit exceeded (429). Please wait 15 seconds.")
        else:
            logger.exception("Failed to generate movie recommendations with Gemini API")
        return []

