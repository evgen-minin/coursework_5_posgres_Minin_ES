import pytest
from unittest.mock import patch

from src.search_employer_api import EmployerSearch


@pytest.fixture
def employer_search():
    return EmployerSearch()


@patch('src.search_employer_api.requests.get')
def test_get_employers(requests_mock, employer_search):
    employer_name = 'Example Employer'
    response_data = {
        'items': [
            {
                'id': '1',
                'name': 'Employer 1',
                'alternate_url': 'https://example.com/employer/1',
                'open_vacancies': 10
            },
            {
                'id': '2',
                'name': 'Employer 2',
                'alternate_url': 'https://example.com/employer/2',
                'open_vacancies': 5
            }
        ]
    }
    requests_mock.return_value.json.return_value = response_data

    employers = employer_search.get_employers(employer_name)

    assert len(employers) == 2
    assert employers[0]['name'] == 'Employer 1'
    assert employers[1]['name'] == 'Employer 2'


@patch('src.search_employer_api.requests.get')
def test_get_employers_error(requests_mock, employer_search):
    employer_name = 'Example Employer'
    requests_mock.side_effect = Exception('Network Error')

    with pytest.raises(Exception):
        employer_search.get_employers(employer_name)


@patch('src.search_employer_api.csv.DictWriter')
def test_save_employers_to_csv(csv_mock, employer_search):
    employers = [
        {
            'id': '1',
            'name': 'Employer 1',
            'alternate_url': 'https://example.com/employer/1',
            'open_vacancies': 10
        },
        {
            'id': '2',
            'name': 'Employer 2',
            'alternate_url': 'https://example.com/employer/2',
            'open_vacancies': 5
        }
    ]
    filename = 'employers.csv'

    with patch('builtins.open', create=True) as open_mock:
        employer_search.save_employers_to_csv(employers, filename)

        open_mock.assert_called_once_with(
            filename, 'w', newline='', encoding='utf-8'
        )
        csv_mock.assert_called_once_with(
            open_mock().__enter__.return_value,
            fieldnames=['employer_id', 'name', 'website', 'count_open_vacancies']
        )
        writer_mock = csv_mock.return_value
        writer_mock.writeheader.assert_called_once()
        assert writer_mock.writerow.call_count == 2
