import pytest
import logging
from client.api_client import get_location
from data.test_data import TEST_CASES

logger = logging.getLogger(__name__)


def build_params():
    params = []
    for tc in TEST_CASES:
        marks = [getattr(pytest.mark, m) for m in tc.get('marks', [])]
        params.append(pytest.param(
            tc['country_code'],
            tc['zip_code'],
            tc['expected_status'],
            tc['expected_place'],
            id=tc['id'],
            marks=marks
        ))
    return params


@pytest.mark.parametrize(
    'country_code, zip_code, expected_status, expected_place',
    build_params()
)
def test_get_location_by_zip(country_code, zip_code, expected_status, expected_place, request):
    test_id = request.node.name.split('[')[-1].rstrip(']')
    logger.info('=' * 60)
    logger.info(f'{test_id}')
    logger.info('=' * 60)

    response = get_location(country_code, zip_code)

    assert response.status_code == expected_status, (
        f'[FAIL] Status code mismatch - Expected {expected_status} '
        f'but got {response.status_code} for {country_code}/{zip_code}'
    )
    logger.info('Status code validation passed')

    if expected_status == 200:
        data = response.json()

        actual_place = data['places'][0]['place name']
        logger.info(f"Validating place name - Expected: '{expected_place}', Got: '{actual_place}'")
        assert actual_place == expected_place, (
            f"[FAIL] Place name mismatch - Expected '{expected_place}' but got '{actual_place}'"
        )
        logger.info('Place name validation passed')

        logger.info("Validating 'post code' key exists in response")
        assert 'post code' in data, "[FAIL] Response missing 'post code' field"
        logger.info(f"'post code' found: {data['post code']}")

    elif expected_status == 404:
        logger.info(f'Correctly received 404 for invalid input: {country_code}/{zip_code}')
