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

# print(asyncio.run(gemini_service.extract_from_text("{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'item': {'@id': '/', 'name': 'Главная'}}, {'@type': 'ListItem', 'position': 2, 'item': {'@id': '/lst', 'name': 'Пошук'}}, {'@type': 'ListItem', 'position': 3, 'item': {'@id': '/lst/bmw', 'name': 'BMW'}}, {'@type': 'ListItem', 'position': 4, 'item': {'@id': '/lst/bmw/m5', 'name': 'M5'}}, {'@type': 'ListItem', 'position': 5, 'item': {'@id': '/lst/bmw/m5/koenigsbrunn', 'name': 'Königsbrunn'}}, {'@type': 'ListItem', 'position': 6, 'item': {'@id': 'https://www.autoscout24.com.ua/proposyzii/bmw-m5-ahk-sitzlueftung-b-w-acc-multiseats-carbonext-e---379946f6-2631-4cc2-98bf-7a2db9a27e3a', 'name': 'BMW M5 AHK Sitzlüftung B&W ACC MultiSeats CarbonExt.'}}]} " \
# "DESCRIPTION: " \
# "Зателефонувати e-mail WhatsApp Ще не визначилися? Додайте цей автомобіль в обране і отримуйте оновлення, коли ціна на нього знизиться. Додати до списку бажань 1 / 44 До вибраного Поділитись Друкувати BMW M5 AHK Sitzlüftung B&W ACC MultiSeats CarbonExt. Königsbrunn € 124 989 1 Надіслати e-mail Показати номер BayernCar GmbH Зірковий рейтинг 4.5 з 5 4,5 зірки 61 Оцінки Пробіг у кілометрах 9 974 км Тип коробки передач Автоматична Дата першої реєстрації 09/2025 Паливо Eлектро/Бензин Потужність 535 кВт (727 к.с.) Продавець Дилер ⚠ Повідомте про пропозицію Основні дані Тип кузова Седани Тип автомобіля Демонстраційні авто Тип двигуна 4x4 Сидіння 5 Двері 4 Номер оголошення 26-53128 Код моделі: 7909/ADP Історія автомобіля Пробіг у кілометрах 9 974 км Дата першої реєстрації 09/2025 Загальна інспекція 09/2028 Колишні власники 1 З ідеально заповненою сервісною книжкою Так Автомобіль, в якому не курили Так Технічні дані Потужність 535 кВт (727 к.с.) Тип коробки передач Автоматична Літраж двигуна 4 395 см³ Передачі 8 Циліндри 8 Власна маса 2 510 кг Споживання енергії Екологічний клас Euro 6 Еко-стікер 4 (Зелений) Паливо Eлектро/Бензин Інші енергоносії Electricity Викиди CO₂ 37 г/км (комб.) Електротяга 77 км Устаткування Комфорт 360° камера Aвтоматичний старт/стоп Tоновані стекла Автоматичний клімат-контроль, 4 зони Бесьключевой доступ Вентиляція сидінь дзеркало бокове електричне Ел. привід сидінь Електр. склопідіймачі Електричне відкриття кришки багажника знімне заднє сидіння індикатор на лобовому склі камера паркування Круїз-контроль Мультифункціональне кермо Обігрів двигуна Обігрів рульового колеса Обігрів сидіння Парктронік Підлокітник Поперекова опора самокерована система паркування сенсор дощу сенсор паркування позаду сенсор паркування попереду сенсор світла Система допомоги при підйомі по схилу Система навігації Шкіряне кермо Шкіряний салон Розваги / ЗМІ Android Auto Apple CarPlay MP3 USB блютуз Бортовий комп'ютер Вбудована потокова передача музики Звукова система Індукційна зарядка для смартфонів Пристрій вільні руки Радіоприймач Точка доступу W-Lan / Wifi Цифрова панель Цифрове радіо Безпека ABS Aдаптивні фари AFL eCall - система автоматичного оповіщення про дорожні пригоди ESP LED денні ходові вогні LED фари Адаптивний круїз-контроль АПС Гідропідсилювач керма Денні ходові вогні ізофікс Іммобілайзер Незасліплююче дальнє світло Повністю світлодіодні фари Подушка безпеки Подушка безпеки для голови Подушка безпеки позаду Подушка безпеки сбоку Подушки безпеки Помічник управління дальнім світлом Пристрій обмеження швидкості Сигналiзацiя Система аварійного гальмування Система контролю «сліпих» зон Система контролю втоми водія Система контролю дистанції Система контролю тиску в шинах Система попередження при виїзді за межі своєї смуги Система розпізнавання дорожних знаків Центральний замок Центральний замок Додатково Cпортивні сидіння Внутрішнє дзеркало з автозатемненням Голосове управління Електронне паркувальне гальмо Легкосплавні диски Літні шини Протисажовий фільтр Підрульові пелюстки перемикання передач Розсіяне світло в салоні Сенсорний екран Спорт-пакет Фаркоп Показати більше Колір та оббивка Зовнішній колір Сірий Колір за документацією виробника BROOKLYN GRAU METALLIC Лакофарбове покриття Металік Колір внутрішнього обладнання Чорний Матеріал Шкіра Опис автомобіля +WILLKOMMEN BEIM AUTOHAUS BAYERNCAR KÖNIGSBRUNN ...kaufen mit gutem Gefühl! ++ALLE FAHRZEUGE optional DEKRA geprüft !++ Zwischenverkauf, Änderungen und Irrtümer vorbehalten ++WE ALSO SALE WITHOUT VAT FOR EXPORT-JUST ASK US!++ Deutschlandweite Zustellungen möglich!!! Unsere Serviceleistungen: - Allianz Automotive Garantie Erweiterung (optional) - Finanzierung über die BMW Premium Financial oder die Credit Plus Bank Ab sofort sind wir über WhatsApp erreichbar. WhatsApp-/FaceTime Kontakt: +49-171 19 021 90 ++ BMW M5 Limousine ++ Farbe: 0C4P Brooklyngrau Metallic Polster: LKSW Leder Merino Schwarz Sonderausstattung: 01GE BMW LM-Rad D.Sp. 952M STD SO MB 20''/21'' 01MB M DRIVE PROFESSIONAL 0248 Lenkradheizung 02PA Radschraubensicherung 02VB Reifendruckanzeige 02VC Reifenreparatur-Set 0302 Alarmanlage 0322 Komfortzugang 03AC Anhängerkupplung 03DP BMW Iconic Glow Exterieurpaket 03M6 M COMPOUND-BREMSE, SCHWARZ HOCHGL. 03MF M Leuchten Shadow Line 0416 Sonnenschutzrollo hinten/seitlich 0420 Abgedunkelte Verglasung 0428 Warndreieck und Verbandstasche 043P Kohlenstofffaser und Silberfaden hochgl. 0453 Klimatisierte Sitze vorne 0459 Sitzverstellung elektrisch mit Memory 04FL Travel & Comfort Rail System 04GQ M Sicherheitsgurte 04HA Sitzheizung vorne und hinten 04MA M Multifunktionssitz 04NB Klimaautomatik mit 4-Zonenregelung 04NR INNENRAUMKAMERA 04T2 LADEKABEL PROFESSIONAL (MODE 3) 04U8 Schnellladen Wechselstrom 04U9 Akustischer Fussgängerschutz 04UR Ambientes Innenlicht 04V1 BMW ICONICSOUNDS ELECTRIC 0548 Kilometertacho 0552 Adaptiver LED-Scheinwerfer 05AU Driving Assistant Professional 05AV Active Guard 05DW Parking assistant professional 0654 DAB-Tuner 06AE Teleservices 06AF Gesetzlicher Notruf 06AK Connected Drive Services 06C4 Connected Package Professional 06F4 Bowers & Wilkins Surround Sound System 06NX Storage tray wireless charging 06PA Personal eSIM 06U3 BMW Live Cockpit Professional 071C M Exterieurpaket Carbon 0760 Hochglanz Shadow-Line 0776 M Dachhimmel Alcantara anthrazit 07M9 M Shadow Line mit erweitertem Umfang 07VB Comfort Paket Serien-Ausstattung: Airbag Fahrer-/Beifahrerseite Akustischer Fußgängerschutz (Außensound) Ambiente-Beleuchtung Antriebsart: xDrive (Allrad) Connected Professional Außenausstattung: Shadow-Line Hochglanz (erweiterter Umfang) BMW IconicSounds Electric (Soundgenerator) BMW Live Cockpit Professional Dachhimmel Anthrazit (BMW Individual) Diebstahl-Warnanlage mit Innenraumabsicherung Diebstahlsicherung für Räder (Felgenschlösser) Exterieurumfänge Iconic Glow Active Guard (Bremsassistent) Aufmerksamkeits-Assistent Fahrwerksdämpfung elektronisch geregelt (EDC / VDC) Geschwindigkeits-Begrenzeranlage (Speed Limit Device)n Heckklappenbetätigung automatisch Induktionsladeschale für Smartphone (Wireless Charging) Interieurleisten M Dunkel-Silber / Aluminium Rhombicle Innenraumkamera Klimaautomatik 4-Zonen mit autom. Umluft-Control Knieairbag Fahrerseite Komfortzugang (Öffnungs- und Schließsystem) Kopf-Airbag-System hinten Kopf-Airbag-System vorn Ladekabel (5,0 m) mit Typ 2-Stecker (Mode 3, 22 kW) Ladekabel Wechselstrom / Gleichstrom (20 A / 230 V) Lendenwirbelstütze Sitz vorn links und rechts Lenkrad (Leder) mit Multifunktion M-Technic Lenkrad heizbar M Drive Professional (Fahrprofilauswahl) Panoramadach (Glas)) Radioempfang digital (DAB+) Reifen-Reparaturset (Mobility-Pack) Reifendruck-Kontrollsystem Scheinwerfer BMW Individual Shadow-Line Scheinwerfer LED mit adaptiver Lichtverteilung Seitenairbag vorn ConnectedDrive Services Gesetzlicher Notruf Intelligenter Notruf inkl. TeleServices Servolenkung Integral - Aktivlenkung Sicherheitsgurte M Sitze vorn elektr. verstellbar (mit Memory) Sitzheizung vorn Sonnenschutzverglasung (hinten abgedunkelt) Sound-System Bowers & Wilkins Sportdifferential Steckdose (12V-Anschluß) in Mittelkonsole und Koffer-/Laderaum (4-fach) Ein Angebot von BMW Premium Finacial: Laufzeit: 36 Monate Anzahlung: 20.755,00 € effekt. Jahreszins: 6,99 % Schlussrate: 79.294,00 € Nettokreditbetrag: 109.234,00 € Bruttokreditbetrag: 128.448,00 € Abschlussgebühr: 0,00 € Ratensicherung: 0,00 € Sollzinssatz: 6,78 % monatl. Rate: 1.405,00 € Wir bieten unsere Fahrzeuge bereits kurz nach Kauf und ohne Bilder an. Sobald diese bei uns eingetroffen sind werden Bilder eingestellt. Mit einer Bestellung versenden wir nochmal eine detaillierte Aufstellung der kompletten Fahrzeugausstattung. Wir bitten diese vor Vertragsabschluß sorgfältig zu lesen, da Fehler im Inserat vorbehaltlich sind und Irrtümer nicht ausgeschlossen werden können. Leasing shared.leasing.targetGroupPrivate detailpage.leasing.title BayernCar GmbH detailpage.leasing.oneTimeCosts detailpage.leasing.configurator.downPayment € 0 shared.listItem.leasing.transferCost Keine Angabe shared.listItem.leasing.registrationCost Keine Angabe detailpage.leasing.total € 0 detailpage.leasing.generalData detailpage.leasing.contractType Kilometerleasing detailpage.leasing.mileage p.a. 10.000 km detailpage.leasing.monthlyCosts detailpage.leasing.duration 48 Monate detailpage.leasing.monthlyInstallment € 312 detailpage.leasing.additionalInformation detailpage.leasing.finalInstallment € 23.615 detailpage.leasing.tip.headline detailpage.leasing.tip.text detailpage.leasing.loanBrokerage Volkswagen Leasing GmbH / Gifhorner Str. 57 / 38112 Braunschweig Die Angaben entsprechen zugleich dem 2/3 Beispiel nach § 6a Abs. 3 PAngV. Показати більше Продавець Дилер BayernCar GmbH Зірковий рейтинг 4.5 з 5 4,5 зірки 61 Оцінки Дилер AutoScout24 із 2005 VERKAUFSAUSSTELLUNG зачинено (місцевий час) Відкривається о (місцевий час) 9:00 пт. Dornierstraße 10 , 86343 Königsbrunn, DE Контактні дані Verkaufsteam BayernCar Показати номер Інші автомобілі цього дилера Інформація про продавця Вихідні дані ")))