from yandex_cloud_ml_sdk import YCloudML

from dotenv import load_dotenv
import os

load_dotenv()

async def yandex_gpt_async(resume, vacancy):
    ID = os.getenv('ID')
    API_KEY = os.getenv('API_KEY')


    promt = """
Проанализируй это резюме как опытный карьерный консультант. Оцени структуру, стиль и содержание. Укажи, что можно улучшить, убрать или усилить, чтобы резюме произвело лучшее впечатление на рекрутера в сфере финансов
Сравни это резюме с вакансией. Оцени, насколько кандидат соответствует требованиям, и какие формулировки стоит усилить или добавить, чтобы повысить шансы на получение приглашения на собеседование
"""

    
    
    messages = [
    {
        "role": "system",
        "text": promt,
    },
    {
        "role": "user",
        "text": f'Резюме: {resume}\nВакансия: {vacancy}',
    },
]
    
   

    sdk = YCloudML(
        folder_id=ID,
        auth=API_KEY,
    )
    result = (
        sdk.models.completions("yandexgpt").configure(temperature=0.5).run(messages)
    )
    text = result.alternatives[0].text
    return text
# Пример запуска
# if __name__ == "__main__":
#     resume = "Опыт работы: бухгалтер в компании А, 5 лет. Образование: Финансовый университет."
#     vacancy = "Требуется главный бухгалтер с опытом от 3 лет, знание 1С и МСФО."
#     result = asyncio.run(yandex_gpt_async(resume, vacancy))
#     text = result.alternatives[0].text
#     pprint(text)
