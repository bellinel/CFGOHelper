from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import os
from dotenv import load_dotenv

load_dotenv()



# Путь к ключу сервисного аккаунта
SERVICE_ACCOUNT_FILE = 'utils/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

# Авторизация
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)



# Права доступа — полный доступ к Google Диску
SCOPES = ['https://www.googleapis.com/auth/drive']  # полный доступ к Google Drive


def authenticate():
    creds = None
    # Файл с сохранёнными токенами пользователя
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Если токена нет или он просрочен — запуск OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраняем токен для будущих запусков
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def upload_file(file_path, upload_name=None):
    file_name = upload_name or os.path.basename(file_path)
    folder_id = '1NzdVZbyNfaMWwQzMCIbtsk7U88FqNYdo'  # <-- ID целевой папки на Google Диске

    creds = authenticate()
    drive_service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,           # Используем заданное имя
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = uploaded_file.get('id')
    print(f"✅ Файл загружен, ID: {file_id}")

    # Открываем доступ по ссылке
    drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    file_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    print(f"🔗 Ссылка на файл: {file_link}")
    return file_link



