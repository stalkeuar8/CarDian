import aiohttp

from app.schemas.lookups_schemas import HttpsUrl

class ParseService:

    @classmethod
    async def parse_url(cls, url_to_parse: HttpsUrl):
        ...