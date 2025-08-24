import datetime
import json
import os

from google.auth.exceptions import GoogleAuthError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import HttpLib2Error

from src.parser_service.util.error import NoReserveFileError
from src.tools.logger import set_up_logger

logger = set_up_logger('./log/excell_loader.log')


# подгрузка и обновление excel
def update_excell():
    request = ''
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials_json = os.getenv("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(credentials_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        file_id = os.getenv("GOOGLE_SHEET_ID")
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        request = drive_service.files().export_media(fileId=file_id, mimeType=mime_type)
    except GoogleAuthError as err:
        logger.warning('Error during google auth. %s', err)

    remove_old_reserve_file()
    reserve_current_active_file()
    download_schedule_file(request)


def download_schedule_file(request):
    try:
        with open(os.getenv('MAIN_SCHEDULE_PATH'), "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
    except (HttpError, HttpLib2Error) as err:
        logger.warning("Ошибка зпгрузки файла с расписанием. Попытаемся использовать резервную копию. %s", err)
        dereserve_file()


def remove_old_reserve_file():
    res_path = os.getenv('RESERVATION_SCHEDULE_PATH')
    if os.path.exists(res_path):
        os.remove(res_path)
        logger.info("Удален файл резервации")


def reserve_current_active_file():
    temp_path = os.getenv('MAIN_SCHEDULE_PATH')
    if os.path.exists(temp_path):
        os.rename(temp_path, os.getenv('RESERVATION_SCHEDULE_PATH'))
        logger.info(f"Резервирован старый файл: {temp_path}")


def dereserve_file():
    res_path = os.getenv('RESERVATION_SCHEDULE_PATH')
    if os.path.exists(res_path):
        os.rename(res_path, os.getenv('MAIN_SCHEDULE_PATH'))
        logger.info(f"Дерезервирован старый файл: {res_path}")
    else:
        logger.error("Файл резервании не найден. Получение расписания невозможно.")
        raise NoReserveFileError()


def download_and_update():
    current_date = datetime.datetime.now()
    try:
        update_excell()
        logger.info(f"Расписание обновлено {current_date.strftime('%d %B %Y, %H:%M:%S')}")
    except NoReserveFileError as err:
        logger.error("Фатальная ошибка обновления расписания. %s", err)
        raise NoReserveFileError()
    except Exception as err:
        logger.info(f"!!!Расписание НЕ обновлено {current_date.strftime('%d %B %Y, %H:%M:%S')}. %s", err)
        raise err
