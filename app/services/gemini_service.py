import logging
import asyncio
from google import genai
from pydantic import BaseModel

from app.settings.config import gemini_settings
from app.settings.gemini_prompts import gemini_prompts
from app.schemas.gemini_schemas import GeminiAnalyzeResponseSchema, GeminiAnalyzeRequestSchema, GeminiExtractorRequestSchema, GeminiExtractorResponseSchema

import logging


class GeminiService:

    def __init__(self):
        self.client = genai.Client(api_key=gemini_settings.API_KEY)
        self.model_id = gemini_settings.GEMINI_MODEL


    async def analyze_existing(self, car_data: GeminiAnalyzeRequestSchema) -> GeminiAnalyzeResponseSchema:
        config = genai.types.GenerateContentConfig(
            temperature=0.15,
            system_instruction=gemini_prompts.SYSTEM_PROMPT_REVIEWER,
            response_mime_type="application/json",
            response_schema=GeminiAnalyzeResponseSchema
        )

        prompt = f"GIVE YOUR PROFESSIONAL FEEDBACK\nOUR AI PREDICTED PRICE: {car_data.predicted_price} EUR\nVEHICLE DATA: {car_data.model_dump_json()}"
        
        if car_data.price_in_ad is not None:
            prompt += f", PRICE LISTED IN ADD: {car_data.price_in_ad} EUR, COMPARE IT AND GIVE YOU FEEDBACK INCLUDING PRICES REVIEW"

        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            config=config,
            contents=prompt
        )
        
        return GeminiAnalyzeResponseSchema(**response.parsed.model_dump())
    


    async def extract_from_text(self, parsed_data: GeminiExtractorRequestSchema) -> GeminiExtractorResponseSchema:
        config = genai.types.GenerateContentConfig(
            temperature=0.15,
            system_instruction=gemini_prompts.SYSTEM_PROMPT_EXTRACTOR,
            response_mime_type="application/json"
        )

        response = await self.client.aio.models.generate_content(
            config=config,
            model=self.model_id,
            contents=f"EXTRACT ALL NEEDED PARAMETERS AND SPECIFICATIONS FROM THIS TEXT: {parsed_data.parsed_text}"
        )
        
        try:
            return GeminiExtractorResponseSchema.model_validate_json(response.text)
        
        except Exception:
            return None
        
gemini_service = GeminiService()
