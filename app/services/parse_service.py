import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
# from app.schemas.lookups_schemas import HttpsUrl

class ParseService:

    @classmethod
    async def get_html(cls, url_to_parse: str) -> str | None:
        headers = {
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            
            try:
                async with session.get(url=str(url_to_parse), timeout=aiohttp.ClientTimeout(10)) as response:

                    if response.status != 200:
                        return None
                    
                    return await response.text()
                
            except aiohttp.ClientError:
                return None
            
            except Exception:
                return None


    @classmethod
    async def extract_car_data(cls, parsed_html: str) -> str | None:
        soup = BeautifulSoup(parsed_html, "html.parser")

        ld_json = soup.find("script", type="application/ld+json")
        tech_data = json.loads(ld_json.string) if ld_json else None

        return tech_data
    


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
    async def process_url(cls, url: str) -> str | None:
        html = await ParseService.get_html(url)

        car_data = await ParseService.extract_car_data(parsed_html=html)

        desc = await ParseService.extract_description(parsed_html=html)

        if car_data is None:
            return None
        
        if desc is None:
            return str(car_data)
        
        return str(car_data) + "\n\nDESCRIPTION: \n\n" + desc
    

print(asyncio.run(ParseService.process_url(url="https://www.autoscout24.com.ua/proposyzii/bmw-m5-ahk-sitzlueftung-b-w-acc-multiseats-carbonext-e---379946f6-2631-4cc2-98bf-7a2db9a27e3a?ipc=recommendation&ipl=homepage-bestresult-listings&source_otp=t50&ap_tier=t50&boost_level=t50&applied_boost_level=t50&relevance_adjustment=boost&boosting_product=mia&source=homepage_last-search&position=1")))