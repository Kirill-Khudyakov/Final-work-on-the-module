import configparser
import json
import requests
from tqdm import tqdm
from datetime import datetime
from vk import VK
from yandex import YANDEX


def main():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    vk_token = config['Tokens']['vk_token']
    yd_token = config['Tokens']['yd_token']

    while True:
        command = input(
            "Введите 'cтоп' для завершения или нажмите Enter для продолжения: ")
        if command.lower() == 'cтоп':
            print('Завершение работы программы.')
            break

        try:
            user_input = input('Введите id или screen_name пользователя VK: ')
            album_choice = input(
                'Выберите источник фотографий (1 - профиль, 2 - стена): ')
            if album_choice not in ['1', '2']:
                raise ValueError(
                    'Неправильный выбор источника фотографий. Введите 1 или 2.')

            album_id = 'profile' if album_choice == '1' else 'wall'
            count_photos = int(
                input('Введите количество фотографий для загрузки (по умолчанию 5): ') or 5)
            folder_name = input(
                'Введите название папки для сохранения фотографий на Яндекс диск: ')

            vk = VK(vk_token)

            # Получаем user_id, если передан screen_name
            if not user_input.isdigit():
                user_id = vk.get_user_id(user_input)
                if user_id is None:
                    print('Не удалось получить user_id. Проверьте screen_name.')
                    continue
            else:
                user_id = user_input

            photos = vk.get_photos(
                user_id, count=count_photos, album_id=album_id)

            if 'response' in photos and 'items' in photos['response']:
                items = photos['response']['items']
                sorted_photos = sorted(
                    items, key=lambda x: x['likes']['count'], reverse=True)
                selected_photos = sorted_photos[:count_photos]

                yandex = YANDEX(yd_token)
                yandex.create_folder(folder_name)

                upload_info = []
                last_likes_count = None

                for photo in tqdm(selected_photos, desc="Загрузка фотографий"):
                    max_size_photo = max(
                        photo['sizes'], key=lambda x: x['width'] * x['height'])
                    likes_count = photo['likes']['count']

                    # Формируем имя файла
                    if last_likes_count is not None and likes_count == last_likes_count:
                        # Если количество лайков равно предыдущему, добавляем дату
                        date_str = datetime.now().strftime("%Y-%m-%d")
                        file_name = f"{likes_count}_{date_str}.jpg"
                    else:
                        # Если количество лайков не равно, используем только количество лайков
                        file_name = f"{likes_count}.jpg"

                    last_likes_count = likes_count  # Обновляем количество лайков для следующей итерации

                    file_url = max_size_photo['url']
                    file_content = requests.get(file_url).content
                    upload_url = yandex.get_upload_url(
                        f'{folder_name}/{file_name}')

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
                print(
                    'Ошибка получения фотографий. Проверьте ID пользователя и доступ к альбому. Попробуйте снова.')

        except ValueError as ve:
            print(f'Ошибка: {ve}. Попробуйте снова.')
        except Exception as e:
            print(f'Произошла ошибка: {e}. Попробуйте снова.')


if __name__ == "__main__":
    main()
