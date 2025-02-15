import requests


class VK:
    def __init__(self, token, version='5.199'):
        self.params = {
            'access_token': token,
            'v': version
        }
        self.base = 'https://api.vk.com/method/'

    def get_user_id(self, screen_name):
        """ Получение user_id по screen_name """
        url = f'{self.base}users.get'
        params = {
            'user_ids': screen_name
        }
        params.update(self.params)
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(
                f"Ошибка при получении user_id: {response.status_code} - {response.json()}")
            return None

        user_info = response.json().get('response')
        if user_info:
            return str(user_info[0]['id'])
        else:
            print("Не удалось найти пользователя по screen_name.")
            return None

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
