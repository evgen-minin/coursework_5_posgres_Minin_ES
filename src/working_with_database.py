import psycopg2
from typing import List


class DBManager:
    def __init__(self, config):
        self.config = config

    def execute_query(self, query, params=None):
        with psycopg2.connect(
                host=self.config['HOST'],
                user=self.config['USER'],
                password=self.config['PASSWORD'],
                database=self.config['DB_NAME']
        ) as connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()

    def table_exists(self, table_name):
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')"
        result = self.execute_query(query)
        return result[0][0]

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        :return: Список с информацией о компаниях и количестве вакансий.
        """
        query = """
                SELECT employers.employer_id, employers.name, employers.website, COUNT(vacancies."vacancy id") AS count_open_vacancies
                FROM employers
                LEFT JOIN vacancies ON employers.employer_id = vacancies."employer id"
                GROUP BY employers.employer_id, employers.name, employers.website;
                """
        return self.execute_query(query)

    def get_all_vacancies_count(self):
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию.
        :return: Список с информацией о вакансиях.
        """
        query = "SELECT COUNT(*) FROM vacancies"
        return self.execute_query(query)[0][0]

    def get_avg_salary(self):
        """
        Получает среднюю зарплату по вакансиям.
        :return: Средняя зарплата.
        """
        query = "SELECT ROUND(AVG(CAST(salary AS numeric)), 0) FROM vacancies WHERE salary <> '';"
        return self.execute_query(query)[0][0]

    def get_vacancies_with_higher_salary(self):
        """
        Получает список всех вакансий, у которых зарплата выше заданного порога.
        :param threshold: Пороговое значение зарплаты.
        :return: Список с информацией о вакансиях.
        """
        avg_salary = self.get_avg_salary()

        query = "SELECT * FROM vacancies WHERE salary::numeric > %s AND salary != ''"
        return self.execute_query(query, (avg_salary,))

    def get_vacancies_with_keyword(self, keyword):
        """
        Получает список всех вакансий, в названии которых содержатся заданные ключевые слова.
        :param keyword: Ключевые слова для поиска.
        :return: Список с информацией о вакансиях.
        """
        query = "SELECT * FROM vacancies WHERE \"vacancy name\" ILIKE %s"
        return self.execute_query(query, (f"%{keyword}%",))
