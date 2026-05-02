import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
from app.schemas.lookups_schemas import HttpsUrl
from app.settings.config import proxy_settings

class ParseService:

    @classmethod
    async def get_html(cls, url_to_parse: HttpsUrl) -> str | None:
        headers = {
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            
            try:
                async with session.get(url=f"{proxy_settings.URL}?url={url_to_parse}", timeout=aiohttp.ClientTimeout(10)) as response:

                    if response.status != 200:
                        return response.status
                    
                    return await response.text()
                
            except aiohttp.ClientError:
                return None
            
            except Exception:
                return None


    @classmethod
    async def extract_car_data(cls, parsed_html: str) -> str | None:
        soup = BeautifulSoup(parsed_html, "html.parser")

        ld_json_scripts = soup.find_all("script", type="application/ld+json")
    
        for script in ld_json_scripts:
            try:
                data = json.loads(script.get_text())
            
                if isinstance(data, list):
                    data = data[0]

                if data.get("@type") in ["Product", "Car", "Vehicle"]:
                    return data
                
            except (json.JSONDecodeError, TypeError, AttributeError):
                continue

        return None
    


    @classmethod
    async def extract_description(cls, parsed_html: str) -> str | None:
        soup = BeautifulSoup(parsed_html, 'html.parser')
    
        desc_block = soup.find("div", {"data-testid": "description-content"})
        if desc_block:
            return desc_block.get_text(separator=" ", strip=True)

        for header in soup.find_all(['h2', 'h3']):
            if "description" in header.text.lower() or "beschreibung" in header.text.lower():
                parent = header.find_parent()
                if parent:
                    return parent.get_text(separator=" ", strip=True)

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
            
        main_content = soup.find('main')
        if main_content:
            return main_content.get_text(separator=" ", strip=True)
            
        return None


    @classmethod
    async def process_url(cls, url: HttpsUrl) -> str | None:
        html = await ParseService.get_html(url)

        car_data = await ParseService.extract_car_data(parsed_html=html)

        desc = await ParseService.extract_description(parsed_html=html)

        if car_data is None:
            return None
        
        if desc is None:
            return str(car_data)
        
        return str(car_data) + "\n\nDESCRIPTION: \n\n" + desc
    


parse_service = ParseService()