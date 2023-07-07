from create_tables.create_employers_table import create_table_from_csv
from src.search_employer_api import EmployerSearch
from src.vacancies_search_id import VacancySearch
from dotenv import dotenv_values

from src.working_with_database import DBManager


def main():
    config = dotenv_values('.env')

    employer_search = EmployerSearch()
    vacancy_search = VacancySearch()

    employer_name = input("Введите название компании: ")
    employers = employer_search.get_employers(employer_name)
    employer_search.save_employers_to_csv(employers, 'data_file/data_employers.csv')
    create_table_from_csv(config, 'employers', 'data_file/data_employers.csv')

    employer_id = input("Введите ID компании. "
                        "ID можно посмотреть в файле 'data_file/data_employers.csv': ")

    vacancies = vacancy_search.get_vacancies(employer_id)
    vacancy_search.save_vacancies_to_csv(vacancies, 'data_file/data_vacancies.csv')
    create_table_from_csv(config, 'vacancies', 'data_file/data_vacancies.csv')

    db_manager = DBManager(config)

    # Проверка наличия таблиц employers и vacancies
    if not db_manager.table_exists('employers') or not db_manager.table_exists('vacancies'):
        print("Таблицы пустые. Добавьте сначала данные для работы с ними.")
        return

    print("\nРезультаты:")
    print("------------")
    companies_and_vacancies = db_manager.get_companies_and_vacancies_count()
    for company in companies_and_vacancies:
        print(f"Компания: {company[1]}\nКоличество вакансий: {company[3]}")
        print("------------")

    all_vacancies_count = db_manager.get_all_vacancies_count()
    print(f"Общее количество вакансий: {all_vacancies_count}")
    print("------------")

    avg_salary = db_manager.get_avg_salary()
    print(f"Средняя зарплата: {avg_salary}")
    print("------------")

    higher_salary_vacancies = db_manager.get_vacancies_with_higher_salary()

    for vacancy in higher_salary_vacancies:
        print(f"Вакансия: {vacancy[0]}\nЗарплата: {vacancy[3]}")
        print("------------")

    keyword = input("Введите ключевое слово для поиска вакансий: ")
    keyword_vacancies = db_manager.get_vacancies_with_keyword(keyword)
    for vacancy in keyword_vacancies:
        print(f"Вакансия: {vacancy[0]}\nЗарплата: {vacancy[3]}")
        print("------------")


if __name__ == '__main__':
    main()
