import requests


class YANDEX:
    def __init__(self, token):
        self.headers = {
            'Authorization': f'OAuth {token}'
        }
        self.base = 'https://cloud-api.yandex.net/v1/disk/resources'

    def create_folder(self, folder_name):
        url = f'{self.base}'
        params = {
            'path': folder_name
        }
        response = requests.put(url, headers=self.headers, params=params)
        if 200 <= response.status_code < 300 or response.status_code == 409:
            print(f'Папка {folder_name} создана!')
        else:
            print(f'Ошибка при создании папки: {response.json()}')

    def get_upload_url(self, file_path):
        url = f'{self.base}/upload'
        params = {
            'path': file_path,
            'overwrite': 'true'
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get('href')
        else:
            print(f'Ошибка получения URL для загрузки: {response.json()}')
            return None

    def upload_file(self, upload_url, file_content):
        response = requests.put(upload_url, data=file_content)
        return response.status_code == 201


