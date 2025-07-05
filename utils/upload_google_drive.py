import os
import asyncio
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = 'utils/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1NzdVZbyNfaMWwQzMCIbtsk7U88FqNYdo'


# Асинхронная обёртка вокруг авторизации
async def authenticate_async() -> Credentials:
    return await asyncio.to_thread(authenticate_sync)


def authenticate_sync():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


# Асинхронная функция загрузки файла
async def upload_file_async(file_path: str, upload_name: str = None) -> str:
    file_ext = os.path.splitext(file_path)[1]
    base_name = os.path.basename(file_path)

    if upload_name:
        file_name = upload_name + file_ext if not upload_name.endswith(file_ext) else upload_name
    else:
        file_name = base_name

    creds = await authenticate_async()

    drive_service = await asyncio.to_thread(build, 'drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }

    media = MediaFileUpload(file_path, resumable=True)

    uploaded_file = await asyncio.to_thread(
        drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute
    )

    file_id = uploaded_file.get('id')
    print(f"✅ Файл загружен, ID: {file_id}")

    await asyncio.to_thread(
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute
    )

    file_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    print(f"🔗 Ссылка на файл: {file_link}")
    return file_link
