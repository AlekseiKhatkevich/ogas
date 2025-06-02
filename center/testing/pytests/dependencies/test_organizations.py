import pytest

from center.faststream.dependencies import organization
from common.exceptions.app import AuthMessageException, NoOrganizationIdentityException


async def test_organization_dependency_negative_no_input():
    expected_err_msg = 'Не указаны organization_id или organization_name. Укажите одно из двух.'

    with pytest.raises(NoOrganizationIdentityException, match=expected_err_msg):
        await organization(token='random_str', organization_id=None, organization_name=None)


async def test_organization_dependency_negative_no_organization(organization_in_db, organization_repo):
    expected_err_msg = (f'Компания с названием "{organization_in_db.name}" и id "{organization_in_db.id}" не '
                        f'существует или токен не валиден.')

    with pytest.raises(AuthMessageException, match=expected_err_msg):
        await organization(
            token='random_str',
            organization_id=organization_in_db.id,
            organization_name=organization_in_db.name,
            repo=organization_repo,
        )


async def test_organization_dependency_positive(organization_in_db, organization_repo, organization_token):
    organization_instance = await organization(
        token=organization_token,
        organization_id=organization_in_db.id,
        organization_name=organization_in_db.name,
        repo=organization_repo,
    )

    assert organization_instance == organization_in_db
