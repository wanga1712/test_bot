import time
import datetime
import psycopg2
from user import User
import requests


class PairSearch:
    BASE_URL = "https://api.vk.com/method/"
    MAX_REQUESTS_PER_SECOND = 3
    MAX_PHOTOS_PER_USER = 1000

    def __init__(self, vk_access_token):
        self.access_token = vk_access_token
        self.session = requests.Session()

    def _make_request(self, method, params):

        url = f"{self.BASE_URL}{method}"
        params["access_token"] = self.access_token
        params["v"] = "5.131"

        response = self.session.get(url, params=params)
        response_json = response.json()

        if response.status_code != 200:
            raise ConnectionError(f"Ошибка в запросе к API ВКонтакте: {response_json.get('error')}")

        return response_json.get("response")

    @staticmethod
    def clear_database():
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password=""
        )

        try:
            cursor = conn.cursor()

            # Начинаем транзакцию для атомарной операции
            with conn:
                # Удаляем все записи из таблицы 'user_photos'
                delete_user_photos_query = "DELETE FROM user_photos"
                cursor.execute(delete_user_photos_query)

                # Удаляем все записи из таблицы 'users'
                delete_users_query = "DELETE FROM users"
                cursor.execute(delete_users_query)

            print("База данных успешно очищена!")
        except Exception as e:
            print(f"Ошибка при очистке базы данных: {e}")
        finally:
            conn.close()

    def get_user_and_search_pairs(self, user_vk_id):
        try:
            user_info = self.get_user_info_by_id(user_vk_id)
            if user_info is None:
                print(f"Информация о пользователе с VK ID: {user_vk_id} недоступна. Пропускаю дальнейшую обработку.")
                return
        except ConnectionError as ce:
            print(f"Ошибка подключения: {ce}")
            return
        except ValueError as ve:
            print(f"Ошибка значения: {ve}")
            return
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return

        if user_info is not None:
            print("Информация о пользователе:")
            print(f"Имя: {user_info.first_name}")
            print(f"Фамилия: {user_info.last_name}")
            print(f"ID: {user_info.user_vk_id}")
            print(f"День рождения: {user_info.bdate}")
            print(f"Пол: {'Мужчина' if user_info.sex == 2 else 'Женщина'}")
            print(f"Город: {user_info.city['title']}")
            print("-----------------------------")
            print("Выполняется поиск пары для пользователя...")
            print("---------------------------------------------")

            # Рассчитываем возраст, используя предоставленную дату рождения
            age = user_info.calculate_age()

            if age is None:
                print("Ошибка: Дата рождения недоступна.")
                return

            # Пример параметров поиска, вы можете их изменить по своим требованиям
            search_params = {
                "sex": 2 if user_info.sex == 1 else 1,  # Женский пол (1 для мужчин, 2 для женщин)
                "age_from": age - 1,
                "age": age,
                "age_to": age + 1,
                "city": user_info.city["id"],
            }

            # Поиск пользователей на основе измененных параметров поиска
            try:
                search_results = self.search_users(search_params, user_info)
            except ConnectionError as ce:
                print(f"Ошибка подключения при поиске пользователей: {ce}")
                return
            except ValueError as ve:
                print(f"Ошибка значения при поиске пользователей: {ve}")
                return

            if search_results:
                total_users = len(search_results)
                print(f"Поиск завершен, найдено пользователей противоположного пола: {total_users}")

                # Сохранение информации о пользователе и фотографий в базу данных PostgreSQL
                for user in search_results:
                    user_id = user["id"]
                    try:
                        # Извлечение и сохранение фотографий пользователя в базу данных
                        success = self.save_user_photos_to_db(user_id)
                        if success:
                            print(
                                f"Информация и фотографии пользователя {user['First Name']} {user['Last Name']} успешно сохранены в базу данных!")
                        else:
                            print(
                                f"Не удалось сохранить информацию и фотографии пользователя {user['First Name']} {user['Last Name']} в базу данных.")
                    except ConnectionError as ce:
                        print(f"Ошибка подключения при сохранении данных в базу данных: {ce}")
                    except ValueError as ve:
                        print(f"Ошибка значения при сохранении данных в базу данных: {ve}")
                    except Exception as e:
                        print(f"Неизвестная ошибка при сохранении данных в базу данных: {e}")
            else:
                print("Пользователи, соответствующие критериям поиска, не найдены.")

    def get_user_info_by_id(self, user_vk_id):
        method = "users.get"
        params = {
            "user_ids": user_vk_id,
            "fields": "sex,bdate,city",
        }

        try:
            response = self._make_request(method, params)
            user_info = response[0]
            if all(key in user_info for key in ["id", "first_name", "last_name", "sex", "bdate", "city"]):
                return User(
                    user_vk_id=user_info["id"],
                    first_name=user_info["first_name"],
                    last_name=user_info["last_name"],
                    sex=user_info["sex"],
                    bdate=user_info.get("bdate"),
                    city=user_info.get("city"),
                )
            else:
                return None  # Вернуть None, если данные о пользователе неполные
        except ConnectionError as ce:
            print(f"Ошибка подключения при получении информации о пользователе: {ce}")
            return None
        except ValueError as ve:
            print(f"Ошибка значения при получении информации о пользователе: {ve}")
            return None
        except Exception as e:
            print(f"Неизвестная ошибка при получении информации о пользователе: {e}")
            return None

    def search_users(self, search_params, user_info):
        method = "users.search"
        search_params["count"] = 1000

        if user_info.city and "id" in user_info.city:
            city_id = user_info.city["id"]
        else:
            return []  # Вернуть пустой список, если данные о городе недоступны

        if user_info.sex == 1:
            search_params["sex"] = 2
        elif user_info.sex == 2:
            search_params["sex"] = 1

        if user_info.bdate:
            try:
                bdate = datetime.datetime.strptime(user_info.bdate, "%d.%m.%Y")
                birth_year = bdate.year
            except ValueError:
                return []  # Вернуть пустой список, если ошибка в формате даты рождения
        else:
            return []  # Вернуть пустой список, если данные о дате рождения недоступны

        age_from = birth_year - 1
        age_to = birth_year + 1

        try:
            response = self._make_request(method, search_params)
            if response is None:
                return []  # Вернуть пустой список, если VK API не вернул результаты поиска

            items = response.get("items", [])

            users = []
            for user in items:
                user_info = self.get_user_info_by_id(user["id"])
                if user_info and user_info.city and "id" in user_info.city and user_info.city["id"] == city_id:
                    if user_info.bdate:
                        try:
                            user_birth_year = datetime.datetime.strptime(user_info.bdate, "%d.%m.%Y").year
                            if age_from <= user_birth_year <= age_to:
                                user_dict = {
                                    "First Name": user_info.first_name,
                                    "Last Name": user_info.last_name,
                                    "id": user_info.user_vk_id,
                                    "Birthday": user_info.bdate,
                                    "Sex": user_info.sex,
                                    "City": user_info.city["title"]
                                }
                                users.append(user_dict)
                        except ValueError:
                            pass  # Игнорировать пользователей с некорректным форматом даты рождения
                    else:
                        pass  # Игнорировать пользователей без информации о дате рождения

            return users
        except Exception:
            return []  # Вернуть пустой список, если произошла ошибка при поиске пользователей

    def get_all_user_photos(self, user_vk_id):
        method = "photos.get"
        params = {
            "owner_id": user_vk_id,
            "album_id": "wall",
            "extended": 1,
            "photo_sizes": 1,
            "access_token": self.access_token,
            "v": "5.131",
            "count": 100,
            # Установите количество фотографий, которые необходимо получить за один запрос (можно изменить по необходимости)
        }

        try:
            photos = []

            while True:
                response = self._make_request(method, params)

                if response is None or "items" not in response:
                    break  # Нет фотографий для получения или ошибка в ответе, выйти из цикла

                photos.extend(response["items"])

                # Проверить, есть ли еще фотографии для получения
                total_count = response["count"]
                fetched_count = len(photos)

                # Проверить, если у пользователя больше фотографий, чем получено за запрос
                if fetched_count >= total_count:
                    break  # Все фотографии были получены, выйти из цикла

                # Обновить параметр "offset" для следующего запроса
                params["offset"] = fetched_count

                # Быть ответственным пользователем API и ограничить количество запросов в секунду
                time.sleep(1 / self.MAX_REQUESTS_PER_SECOND)

            return photos
        except Exception as e:
            print(f"Ошибка при получении фотографий пользователя: {e}")
            return []

    def save_user_photos_to_db(self, user_vk_id):
        user_info = self.get_user_info_by_id(user_vk_id)
        if user_info is None:
            print(
                f"Не удалось сохранить информацию и фотографии пользователя {user_vk_id} в базе данных. Причина: Информация о пользователе недоступна.")
            return False

        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="05321983"
        )

        try:
            cursor = conn.cursor()

            # Начать транзакцию для атомарной операции
            with conn:
                # Проверить, существует ли пользователь уже в таблице 'users' на основе user_vk_id
                check_user_query = "SELECT * FROM users WHERE user_vk_id = %s"
                cursor.execute(check_user_query, (user_vk_id,))
                existing_user = cursor.fetchone()

                if existing_user:
                    # Обновить информацию о пользователе в таблице 'users', если пользователь уже существует
                    update_user_query = "UPDATE users SET first_name = %s, last_name = %s, sex = %s, bdate = %s, city = %s WHERE user_vk_id = %s"
                    cursor.execute(update_user_query, (
                        user_info.first_name,
                        user_info.last_name,
                        user_info.sex,
                        user_info.bdate,
                        user_info.city["title"] if user_info.city else None,
                        user_vk_id,
                    ))
                else:
                    # Вставить информацию о пользователе в таблицу 'users', если пользователь не существует
                    insert_user_query = "INSERT INTO users (user_vk_id, first_name, last_name, sex, bdate, city) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(insert_user_query, (
                        user_vk_id,
                        user_info.first_name,
                        user_info.last_name,
                        user_info.sex,
                        user_info.bdate,
                        user_info.city["title"] if user_info.city else None,
                    ))

                # Получить все фотографии пользователя из всех альбомов
                all_photos = self.get_all_user_photos(user_vk_id)

                if not all_photos:
                    print(
                        f"Не удалось сохранить информацию и фотографии пользователя {user_vk_id} в базу данных. Причина: Фотографии не найдены.")
                    return False

                # Сохранить фотографии пользователя в таблицу 'user_photos'
                for photo in all_photos:
                    largest_size_url = max(photo["sizes"], key=lambda x: x["width"])["url"]
                    likes_count = photo["likes"]["count"]
                    comments_count = photo["comments"]["count"]
                    photo_date = datetime.datetime.fromtimestamp(photo["date"])

                    insert_photo_query = "INSERT INTO user_photos (user_vk_id, photo_url, likes_count, comments_count, photo_date) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(insert_photo_query, (
                        user_vk_id,
                        largest_size_url,
                        likes_count,
                        comments_count,
                        photo_date,
                    ))

            print(
                f"Информация и фотографии пользователя {user_info.first_name} {user_info.last_name} успешно сохранены в базе данных!")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных в базу данных: {e}")
            return False
        finally:
            conn.close()
