from google import genai
from pydantic import BaseModel

from app.settings.config import gemini_settings
from app.settings.gemini_prompts import gemini_prompts
from app.schemas.gemini_schemas import GeminiAnalyzeResponseSchema, GeminiAnalyzeRequestSchema

import logging


class GeminiService:

    def __init__(self):
        self.client = genai.Client(api_key=gemini_settings.API_KEY)
        # for model in self.client.models.list():
        #     print(model)
        self.model_id = "gemini-3-flash-preview"


    async def analyze_existing(self, car_data: GeminiAnalyzeRequestSchema) -> GeminiAnalyzeResponseSchema:
        config = genai.types.GenerateContentConfig(
            temperature=0.15,
            system_instruction=gemini_prompts.SYSTEM_PROMPT_REVIEWER,
            response_mime_type="application/json",
            response_schema=GeminiAnalyzeResponseSchema
        )


        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            config=config,
            contents=f"GIVE YOUR PROFESSIONAL FEEDBACK\nOUR AI PREDICTED PRICE: {car_data.predicted_price} USD\nVEHICLE DATA: {car_data.model_dump_json()}"
        )
        
        return GeminiAnalyzeResponseSchema(**response.parsed.model_dump())
    


gemini_service = GeminiService()
