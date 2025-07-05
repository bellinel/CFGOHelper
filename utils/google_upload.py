import asyncio
from collections import OrderedDict
from gspread_asyncio import AsyncioGspreadClientManager
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = '1W5t0ObiQxpoYnxbBxRrYcxaHRU8xlFj927qP1w62RLI'
SHEET_NAME = 'Лист1'
SERVICE_ACCOUNT_FILE = 'utils/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Получение асинхронного клиента
def get_creds():
    return Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

async def get_agcm():
    agcm = AsyncioGspreadClientManager(get_creds)
    return await agcm.authorize()

# Получить последний номер строки
async def get_last_row_number(sheet_id: str = SPREADSHEET_ID, sheet_name: str = SHEET_NAME) -> int:
    agc = await get_agcm()
    ss = await agc.open_by_key(sheet_id)
    worksheet = await ss.worksheet(sheet_name)

    col_a = await worksheet.col_values(1)
    col_a = col_a[1:]  # Пропускаем заголовок  # Пропускаем заголовок
    
    if not col_a:
        return 0

    try:
        numbers = [int(val) for val in col_a if val.isdigit()]
        return max(numbers) if numbers else 0
    except ValueError:
        return 0

# Добавить строку в таблицу
async def upload_dict_to_sheet(data: dict, last_row_number: int, sheet_id: str = SPREADSHEET_ID, sheet_name: str = SHEET_NAME):
    agc = await get_agcm()
    ss = await agc.open_by_key(sheet_id)
    worksheet = await ss.worksheet(sheet_name)

    current_row_number = last_row_number + 1

    ordered_data = OrderedDict()
    ordered_data["№"] = current_row_number
    for key, value in data.items():
        ordered_data[key] = value

    # Получаем заголовки
    existing_headers = await worksheet.row_values(1)
    new_headers = list(ordered_data.keys())

    # Если нет заголовков — вставим
    if not existing_headers:
        await worksheet.insert_row(new_headers, 1)
        headers = new_headers
    else:
        headers = existing_headers
        missing_headers = [k for k in new_headers if k not in headers]
        if missing_headers:
            headers += missing_headers
            await worksheet.update('A1', [headers])

    # Формируем строку по заголовкам
    row = []
    for header in headers:
        val = ordered_data.get(header, 'не известно')
        if isinstance(val, list):
            val = ', '.join(val)
        row.append(val)

    await worksheet.append_row(row)
    print("✅ Данные добавлены в таблицу.")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0"
    print(f"🔗 Ссылка: {sheet_url}")
    return sheet_url

# Упрощённая вставка (как append_row_to_billing_sheet)
async def append_row_to_billing_sheet(spreadsheet_id: str, sheet_name: str, data: dict):
    agc = await get_agcm()
    ss = await agc.open_by_key(spreadsheet_id)
    worksheet = await ss.worksheet(sheet_name)

    row = [
        data.get('№', ''),
        data.get('Дата и время', ''),
        data.get('Имя пользователя', ''),
        data.get('Услуга', ''),
        data.get('Операция', ''),
        data.get('Количество', ''),
        data.get('Баланс', '')
    ]

    await worksheet.append_row(row)
    print("✅ Новое действие пользователя добавлено.")
