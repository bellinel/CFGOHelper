import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request








SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'utils/service_account.json'
SPREADSHEET_ID = '1W5t0ObiQxpoYnxbBxRrYcxaHRU8xlFj927qP1w62RLI'  # из ссылки
SHEET_NAME = 'Лист1'  # или 'Sheet1' — проверь, как называется лист в твоей таблице

from collections import OrderedDict

def upload_dict_to_sheet(data: dict, last_row_number: int):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Текущий номер строки + 1
    current_row_number = last_row_number + 1

    # Вставляем номер в начало словаря
    ordered_data = OrderedDict()
    ordered_data["№"] = current_row_number
    for key, value in data.items():
        ordered_data[key] = value

    # Получаем существующие заголовки
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'{SHEET_NAME}!A1:Z1').execute()
    existing_headers = result.get('values', [])[0] if result.get('values') else []

    # Обновляем заголовки, если надо
    new_headers = list(ordered_data.keys())
    if not existing_headers:
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A1',
            valueInputOption='RAW',
            body={'values': [new_headers]}
        ).execute()
        headers = new_headers
    else:
        headers = existing_headers
        missing_headers = [k for k in new_headers if k not in headers]
        if missing_headers:
            headers += missing_headers
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'{SHEET_NAME}!A1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()

    # Формируем строку в нужном порядке
    row = []
    for header in headers:
        val = ordered_data.get(header, '')
        if val == '' or val == []:
            val = 'не известно'
        if isinstance(val, list):
            val = ', '.join(val)
        row.append(val)

    # Добавляем строку
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A2',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': [row]}
    ).execute()

    print("✅ Данные добавлены в таблицу.")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid=0"
    print(f"🔗 Ссылка: {sheet_url}")
    return sheet_url




def get_last_row_number():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Получаем все значения из колонки "A" (где хранятся номера)
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A2:A'
    ).execute()

    values = result.get('values', [])

    if not values:
        return 0  # таблица пуста, кроме заголовка

    try:
        # Преобразуем в числа и ищем максимальное значение
        numbers = [int(row[0]) for row in values if row and row[0].isdigit()]
        return max(numbers) if numbers else 0
    except ValueError:
        return 0
