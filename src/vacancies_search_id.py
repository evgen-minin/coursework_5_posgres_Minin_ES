import logging
import csv
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
        fieldnames = ['Vacancy Name', 'Vacancy ID', 'Vacancy Location', 'Salary', 'URL',
                      'Employer ID', 'Employer Name', 'Job Requirement', 'Responsibility', 'Experience']

        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for vacancy in vacancies:
                salary_from = vacancy.get('salary', {}).get('from') if vacancy.get('salary') is not None else None
                salary_to = vacancy.get('salary', {}).get('to') if vacancy.get('salary') is not None else None
                salary = salary_from or salary_to

                row = {
                    'Vacancy Name': vacancy.get('name'),
                    'Vacancy ID': vacancy.get('id'),
                    'Vacancy Location': vacancy.get('area', {}).get('name'),
                    'Salary': salary,
                    'URL': vacancy.get('alternate_url'),
                    'Employer ID': vacancy.get('employer', {}).get('id'),
                    'Employer Name': vacancy.get('employer', {}).get('name'),
                    'Job Requirement': vacancy.get('snippet', {}).get('requirement'),
                    'Responsibility': vacancy.get('snippet', {}).get('responsibility'),
                    'Experience': vacancy.get('experience', {}).get('name')
                }
                writer.writerow(row)

        self.logger.info(f"Данные с вакансиями сохранены в файл: {filename}")
