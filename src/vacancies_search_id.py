import logging
import csv
import os
import requests

class VacancySearch:
    def __init__(self, url: str = 'https://api.hh.ru/vacancies'):
        self.url = url
        self.params = {}

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')

        file_handler = logging.FileHandler('vacancy_search.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_vacancies(self, employer_id: str) -> list:
        """
        Отправляет GET-запрос по API и получает список вакансий выбранного работодателя.
        :param employer_id: ID работодателя.
        :return: Список с информацией о вакансиях.
        """
        vacancies_url = f"{self.url}?employer_id={employer_id}"

        try:
            self.logger.info("Отправка GET-запроса по поиску вакансий.")
            response = requests.get(vacancies_url)
            response.raise_for_status()
            vacancies = response.json().get('items', [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f'Ошибка при отправке запроса: {e}')
            raise
        except ValueError as e:
            self.logger.error(f'Ошибка при обработке ответа: {e}')
            raise

        return vacancies

    def save_vacancies_to_csv(self, vacancies: list, filename: str):
        """
        Сохраняет результаты поиска о вакансиях в CSV-файл.
        :param vacancies: Список с информацией о вакансиях.
        :param filename: Имя файла для сохранения результатов.
        :return: None.
        """
        fieldnames = ['vacancy name', 'vacancy id', 'vacancy location', 'salary', 'url',
                      'employer id', 'employer name', 'job requirement', 'responsibility', 'experience']

        # Проверяем, существует ли файл
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Если файл не существует, записываем заголовки
            if not file_exists:
                writer.writeheader()

            existing_vacancy_ids = set()

            try:
                with open(filename, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        existing_vacancy_ids.add(row['vacancy id'])
            except FileNotFoundError:
                pass

            for vacancy in vacancies:
                if vacancy['id'] not in existing_vacancy_ids:
                    existing_vacancy_ids.add(vacancy['id'])
                    salary = vacancy.get('salary')
                    salary_from = salary.get('from') if isinstance(salary, dict) and 'from' in salary else None
                    salary_to = salary.get('to') if isinstance(salary, dict) and 'to' in salary else None
                    salary_value = salary_from or salary_to

                    row = {
                        'vacancy name': vacancy.get('name'),
                        'vacancy id': vacancy.get('id'),
                        'vacancy location': vacancy.get('area', {}).get('name'),
                        'salary': salary_value,
                        'url': vacancy.get('alternate_url'),
                        'employer id': vacancy.get('employer', {}).get('id'),
                        'employer name': vacancy.get('employer', {}).get('name'),
                        'job requirement': vacancy.get('snippet', {}).get('requirement'),
                        'responsibility': vacancy.get('snippet', {}).get('responsibility'),
                        'experience': vacancy.get('experience', {}).get('name')
                    }
                    writer.writerow(row)

        self.logger.info(f"Данные с вакансиями сохранены в файл: {filename}")
