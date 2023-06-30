import logging
import csv
from typing import List

import requests


class EmployerSearch:
    def __init__(self, url: str = 'https://api.hh.ru/employers'):
        self.url = url
        self.params = {}

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')

        file_handler = logging.FileHandler('employer_search.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_employers(self, employer_name: str) -> List[dict]:
        """
        Отправляет GET-запрос по API и получает информацию о работодателях.
        :param employer_name: Название работодателя.
        :return: Список с информацией о работодателях.
        """
        self.params = {
            'text': employer_name,
            'only_with_vacancies': True,
            'page': 0,
            'per_page': 100,
        }
        employers = []

        try:
            self.logger.info("Отправка GET-запроса по поиску работодателей.")
            while True:
                response = requests.get(self.url, params=self.params)
                response.raise_for_status()
                data = response.json()

                if 'items' in data:
                    employers.extend(data['items'])

                if 'pages' in data:
                    total_pages = data['pages']
                    if self.params['page'] >= total_pages:
                        break
                    self.params['page'] += 1
                else:
                    break

        except requests.exceptions.RequestException as e:
            self.logger.error(f'Ошибка при отправке запроса: {e}')
            raise
        except ValueError as e:
            self.logger.error(f'Ошибка при обработке ответа: {e}')
            raise

        return employers

    def save_employers_to_csv(self, employers: List[dict], filename: str) -> None:
        """
        Сохраняет результаты поиска о работодателях в CSV-файл.
        :param employers: Список с информацией о работодателях.
        :param filename: Имя файла для сохранения результатов.
        :return: None.
        """
        fieldnames = ['employer_id', 'name', 'website', 'count_open_vacancies']

        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for employer in employers:
                row = {
                    'employer_id': employer.get('id'),
                    'name': employer.get('name'),
                    'website': employer.get('alternate_url'),
                    'count_open_vacancies': employer.get('open_vacancies')
                }
                writer.writerow(row)

        self.logger.info(f"Данные о работодателях сохранены в файл: {filename}")
