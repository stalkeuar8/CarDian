from groq import AsyncGroq
from app.settings.config import groq_settings
from app.settings.groq_prompts import groq_prompts
from app.schemas.groq_schemas import GroqAnalyzeRequestSchema, GroqAnalyzeResponseSchema, GroqExtractorRequestSchema, GroqExtractorResponseSchema

class GroqService:

    def __init__(self):
        self.analyzing_model = groq_settings.ANALYZING_MODEL
        self.extractor_model = groq_settings.EXTRACTOR_MODEL
        self.client = AsyncGroq(api_key=groq_settings.API_KEY)


    async def analyze_existing(self, car_data: GroqAnalyzeRequestSchema) -> GroqAnalyzeResponseSchema | None:

        try:

            prompt = f"GIVE YOUR PROFESSIONAL FEEDBACK\nOUR AI PREDICTED PRICE: {car_data.predicted_price} EUR\nVEHICLE DATA: {car_data.model_dump_json()}"
            
            if car_data.price_in_ad is not None:
                prompt += (f", PRICE LISTED IN ADD: {car_data.price_in_ad} EUR, COMPARE IT AND GIVE YOUR" \
                           "FEEDBACK INCLUDING PRICES REVIEW. BE GENTLE PREDICTED PRICE IS LESS THEN 5% BIGGER, " \
                           "OR GIVE SOME RECOMENDATIONS IF PREDICTED PRICE IS LESS THAN AD PRICE" \
                        )

            chat_completion = await self.client.chat.completions.create(
                model=self.analyzing_model,
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {
                        'role' : 'system',
                        'content' : groq_prompts.SYSTEM_PROMPT_REVIEWER
                    },
                    {
                        'role' : 'user',
                        'content' : prompt
                    }
                ]
            )    

            response = chat_completion.choices[0].message.content

            return GroqAnalyzeResponseSchema.model_validate_json(response)
        
        except Exception as e:
            return (None, e)
    


    async def extract_from_text(self, parsed_data: GroqExtractorRequestSchema) -> GroqExtractorResponseSchema | None:
        
        try:
            prompt = f"EXTRACT ALL NEEDED PARAMETERS AND SPECIFICATIONS FROM THIS TEXT: {parsed_data.parsed_text}"

            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role" : "system",
                        "content" : groq_prompts.SYSTEM_PROMPT_EXTRACTOR
                    },
                    {
                        "role" : "user",
                        "content" : prompt
                    }
                ],
                model=self.extractor_model,
                response_format={"type":"json_object"},
                temperature=0.1
            )

            response = chat_completion.choices[0].message.content

            return GroqExtractorResponseSchema.model_validate_json(response)
        
        except Exception as e:
            return e


groq_service = GroqService()