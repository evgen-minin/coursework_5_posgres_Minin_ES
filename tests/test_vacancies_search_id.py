import csv

import pytest
from unittest.mock import patch
from src.vacancies_search_id import VacancySearch


@pytest.fixture
def vacancy_search():
    return VacancySearch()


@patch('src.vacancies_search_id.requests.get')
def test_get_vacancies(requests_mock, vacancy_search):
    employer_id = '123456'
    response_data = {
        'items': [
            {
                'name': 'Vacancy 1',
                'id': '1',
                'area': {'name': 'Location 1'},
                'salary': {'from': 50000},
                'alternate_url': 'https://example.com/vacancy/1',
                'employer': {'id': '123', 'name': 'Employer 1'},
                'snippet': {'requirement': 'Requirements 1', 'responsibility': 'Responsibilities 1'},
                'experience': {'name': 'Experience 1'}
            },
            {
                'name': 'Vacancy 2',
                'id': '2',
                'area': {'name': 'Location 2'},
                'salary': {'to': 60000},
                'alternate_url': 'https://example.com/vacancy/2',
                'employer': {'id': '123', 'name': 'Employer 1'},
                'snippet': {'requirement': 'Requirements 2', 'responsibility': 'Responsibilities 2'},
                'experience': {'name': 'Experience 2'}
            }
        ]
    }
    requests_mock.return_value.json.return_value = response_data

    vacancies = vacancy_search.get_vacancies(employer_id)
    print(vacancies)

    assert len(vacancies) == 2


def test_save_vacancies_to_csv(tmp_path, vacancy_search):
    vacancies = [
        {
            'name': 'Vacancy 1',
            'id': '1',
            'area': {'name': 'Location 1'},
            'salary': {'from': 50000},
            'alternate_url': 'https://example.com/vacancy/1',
            'employer': {'id': '123', 'name': 'Employer 1'},
            'snippet': {'requirement': 'Requirements 1', 'responsibility': 'Responsibilities 1'},
            'experience': {'name': 'Experience 1'}
        },
        {
            'name': 'Vacancy 2',
            'id': '2',
            'area': {'name': 'Location 2'},
            'salary': {'to': 60000},
            'alternate_url': 'https://example.com/vacancy/2',
            'employer': {'id': '123', 'name': 'Employer 1'},
            'snippet': {'requirement': 'Requirements 2', 'responsibility': 'Responsibilities 2'},
            'experience': {'name': 'Experience 2'}
        }
    ]

    filename = tmp_path / 'vacancies.csv'

    vacancy_search.save_vacancies_to_csv(vacancies, str(filename))

    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        saved_vacancies = list(reader)

    assert len(saved_vacancies) == 2
    assert saved_vacancies[0]['vacancy name'] == 'Vacancy 1'
    assert saved_vacancies[1]['vacancy id'] == '2'
