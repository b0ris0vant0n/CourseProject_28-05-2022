import requests
from pprint import pprint
import time
import json
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# class IG_GetPhoto(InstagramAPI):
#     def __init__(self, token, user_id):
#         self.token = token
#         self.user_id = user_id
#
#     def get_instagram_photo(self):
#         url = 'https://graph.instagram.com/v11.0/'
#         headers = {}
#         params = {'user_id': '25452882', 'access_token': self.token}
#         response = requests.get(url, headers=headers, params=params)
#         pprint(response.json())
#

class OK_GetPhoto:
    def __init__(self, token, user_id, application_key):
        self.token = token
        self.user_id = user_id
        self.application_key = application_key

    def get_list_albums(self):
        url = 'https://api.ok.ru/api/photos/getAlbums'
        headers = {}
        params = {'fid' : self.user_id, 'access_token': self.token,
                  'application_key' : self.application_key, 'detectTotalCount' : True}
        response = requests.get(url, params=params, headers=headers)
        if 'error_code' in response.json():
            if response.json()['error_code'] == 300:
                print(f"Пользователь с ID №{self.user_id} не найден")
            quit()
        albums = response.json()['albums']
        albums_title = ['Профиль']
        albums_aid = ['']
        for album in albums:
            albums_title.append(album['title'].strip())
            albums_aid.append(album['aid'])
        albums_dict = dict(zip(albums_title, albums_aid))
        print(f'У пользователя есть следуюшие альбомы: {", ".join(albums_title)}')
        album_aid = albums_dict[input('Какой будем скачивать? Введите название альбома: ')]
        return album_aid

    def get_photos(self, download_count='5'):
        self.download_count = download_count
        url = 'https://api.ok.ru/api/photos/getPhotos'
        headers = {}
        params = {'fid' : self.user_id, 'aid' : self.get_list_albums(), 'access_token': self.token,
                  'application_key' : self.application_key, 'detectTotalCount' : True, 'count' : self.download_count,
                  'fields' : 'photo.LIKE_COUNT, photo.PIC1024MAX, photo.CREATED_MS'}
        response = requests.get(url, params=params, headers=headers)
        if 'error_code' in response.json():
            if response.json()['error_code'] == 300:
                print(f"Пользователь с ID №{self.user_id} не найден")
            quit()
        result_log = []
        list_qty_likes = []
        file_path = input('Давайте создадим папку куда сохранить фото на Яндекс.Диске.\nВведите название: ')
        ya = Yandex_Disk(Yandex_token)
        ya.create_folder(file_path)
        count = 0
        for photo in response.json()['photos']:
            url_photo = photo['pic1024max']
            upload_date = str(time.strftime("%d-%m-%Y", time.gmtime(photo['created_ms']/1000)))
            qty_likes = str(photo['like_count'])
            count += 1
            if qty_likes not in list_qty_likes:
                file_name = qty_likes + '.jpg'
            else:
                file_name = qty_likes + '_' + upload_date + '.jpg'
            list_qty_likes.append(qty_likes)
            print(f'{count}/{self.download_count} Фото {file_name} из профиля ID No.{self.user_id} в папку Я.ДИСК/{file_path}/...')
            ya.upload_file_to_disk(f'{file_path}/{file_name}', url_photo)
            results_dict = {"file_name" : file_name, "size" : 'pic640x480'}
            result_log.append(results_dict)
        return result_log

class VK_GetPhoto:
    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_list_album(self):
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {'owner_id': self.user_id,
                  'v': '5.131', 'access_token': self.token}
        response = requests.get(url, params=params)
        if 'error' in response.json():
            print(response.json()['error']['error_msg'])
            quit()
        albums_title = ['Профиль', 'Стена']
        albums_id = ['profile', 'wall']
        albums = response.json()['response']['items']
        for album in albums:
            albums_id.append(album['id'])
            albums_title.append(album['title'].strip())
        albums_dict = dict(zip(albums_title, albums_id))
        print(f'У пользователя есть следуюшие альбомы: {", ".join(albums_title)}')
        album_id = albums_dict[input('Какой будем скачивать? Введите название альбома: ')]
        return album_id

    def take_vk_photos(self, download_count='5'):
        self.download_count = download_count
        url = "https://api.vk.com/method/photos.get"
        headers = {}
        params = {'owner_id' : self.user_id,
                  'count' : self.download_count, 'album_id' : self.get_list_album(),
                  'extended' : 'likes', 'v': '5.131', 'access_token': self.token}
        response = requests.get(url, params=params, headers=headers)
        if 'error' in response.json():
            print(response.json()['error']['error_msg'])
            quit()
        list_qty_likes = []
        result_log = []
        file_path = input('Давайте создадим папку куда сохранить фото на Яндекс.Диске.\nВведите название: ')
        ya = Yandex_Disk(Yandex_token)
        ya.create_folder(file_path)
        count = 0
        for photo in response.json()['response']['items']:
            url_photo = photo['sizes'][-1]['url']
            upload_date = str(time.strftime("%d-%m-%Y_%H.%M.%S", time.gmtime(photo['date'])))
            qty_likes = str(photo['likes']['count'])
            count += 1
            if qty_likes not in list_qty_likes:
                file_name = qty_likes + '.jpg'
            else:
                file_name = qty_likes + '_' + upload_date + '.jpg'
            list_qty_likes.append(qty_likes)
            print(f'{count}/{self.download_count} Фото {file_name} из профиля ID No.{self.user_id} в папку Я.ДИСК/{file_path}/...')
            ya.upload_file_to_disk(f'{file_path}/{file_name}', url_photo)
            results_dict = {"file_name" : file_name, "size" : photo['sizes'][-1]['type']}
            result_log.append(results_dict)
        return result_log

class Log_File:
    def __init__(self,filename):
        self.filename = filename

    def save_data_to_file(self, data):
        with open(self, 'w') as document:
            json.dump(data, document)
        print('Завершено. Результат записан в results.json')

class Yandex_Disk:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {"path": folder_name, "overwrite": "true"}
        response = requests.put(url, headers=headers, params=params)

    def _get_upload_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, urllib.request.urlopen(filename).read())
        response.raise_for_status()
        if response.status_code == 201:
            print("Загружено успешно")

def create_folder():
    file_path = input('Давайте создадим папку куда сохранить фото на Яндекс.Диске.\n Введите название: ')
    ya = Yandex_Disk(Yandex_token)
    ya.create_folder(file_path)

if __name__ == '__main__':
    choice_sm = input('Выберите социальную сеть /VK или OK/: ').upper()
    OK_TOKEN = ''
    VK_TOKEN = ''
    IG_TOKEN = ''
    OK_application_key = ''
    Yandex_token = input('Введите токен с Полигона Яндекс.Диска: ')
    if choice_sm == 'VK' or choice_sm == 'ВК':
        ID_USER = input('Введите ID пользователя "Вконтакте": ')
        DOWNLOAD_COUNT = input('Введиите количество фото для скачивания: ')
        vk_getphoto = VK_GetPhoto(VK_TOKEN, ID_USER)
        if DOWNLOAD_COUNT == '':
            url_photo = vk_getphoto.take_vk_photos()
        else:
            url_photo = vk_getphoto.take_vk_photos(DOWNLOAD_COUNT)
    elif choice_sm == 'OK' or choice_sm == 'ОК':
        ID_USER = input('Введите ID пользователя "Одноклассники": ')
        DOWNLOAD_COUNT = input('Введиите количество фото для скачивания: ')
        ok_getphoto = OK_GetPhoto(OK_TOKEN, ID_USER, OK_application_key)
        if DOWNLOAD_COUNT == '':
            url_photo = ok_getphoto.get_photos()
        else:
            url_photo = ok_getphoto.get_photos(DOWNLOAD_COUNT)
    # elif choice_sm == 'IG':
    #     ID_USER = '25452882'
    #     ig_getphoto = IG_GetPhoto(IG_TOKEN, ID_USER)
    #     ig_getphoto.get_instagram_photo()
    else:
        print('Ошибка! Вы выбрали недоступную соц.сеть.')
        quit()
    Log_File.save_data_to_file('results.json', url_photo)