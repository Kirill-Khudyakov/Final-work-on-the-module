import configparser
import requests
import json
from pprint import pprint
from tqdm import tqdm

config = configparser.ConfigParser()
config.read('settings.ini')
vk_token = config['Tokens']['vk_token']
yd_token = config['Tokens']['yd_token']


class VK:
    def __init__(self, token, version='5.199'):
        self.params = {
            'access_token': token,
            'v': version
        }
        self.base = 'https://api.vk.com/method/'

    def get_photos(self, user_id, count=5, album_id='profile'):
        url = f'{self.base}photos.get'
        params = {
            'owner_id': user_id,
            'count': count,
            'album_id': album_id,
            'extended': 1,
            'photo_sizes': 1
        }
        params.update(self.params)
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(
                f"Ошибка при получении фотографий: {response.status_code} - {response.json()}")
            return {}

        return response.json()


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


user_id = input('Введите id пользователя VK: ')
album_choice = input('Выберите источник фотографий (1 - профиль, 2 - стена): ')
album_id = 'profile' if album_choice == '1' else 'wall'
count_photos = int(
    input('Введите количество фотографий для загрузки (по умолчанию 5): ') or 5)
folder_name = input(
    'Введите название папки для сохранения фотографий на Яндекс диск: ')

vk = VK(vk_token)
photos = vk.get_photos(user_id, count=count_photos, album_id=album_id)

if 'response' in photos and 'items' in photos['response']:
    items = photos['response']['items']
    sorted_photos = sorted(
        items, key=lambda x: x['likes']['count'], reverse=True)
    selected_photos = sorted_photos[:count_photos]

    yandex = YANDEX(yd_token)
    yandex.create_folder(folder_name)

    upload_info = []
    for photo in tqdm(selected_photos, desc="Загрузка фотографий"):
        max_size_photo = max(
            photo['sizes'], key=lambda x: x['width'] * x['height'])
        file_name = f"{photo['likes']['count']}.jpg"
        file_url = max_size_photo['url']
        file_content = requests.get(file_url).content
        upload_url = yandex.get_upload_url(f'{folder_name}/{file_name}')
        if upload_url:
            if yandex.upload_file(upload_url, file_content):
                upload_info.append({
                    "file_name": file_name,
                    "size": max_size_photo['type']
                })

    with open('upload_info.json', 'w') as json_file:
        json.dump(upload_info, json_file, indent=4)

    print("Загрузка завершена. Информация сохранена в 'upload_info.json'.")
else:
    print("Ошибка получения фотографий. Проверьте ID пользователя и доступ к альбому.")
