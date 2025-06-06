import typing

import pytest
import ulid

if typing.TYPE_CHECKING:
    from center.orm_models import OrganizationORM
    from center.repositories.postgres import OrganizationPostgresRepository
    from center.testing.factories import OrganizationUpdateInFactory
    from center.serializers import OrganizationUpdateIn


@pytest.fixture(params=[{'use_id': True, 'use_name': False}, {'use_id': False, 'use_name': True}])
def parametrize_identity(request: pytest.FixtureRequest, organization_in_db: 'OrganizationORM') -> (
        tuple[ulid.ULID, None] | tuple[None, str]):
    use_id, use_name = request.param
    return (
        organization_in_db.id if use_id else None,
        organization_in_db.name if use_name else None,
    )


async def test_get_organization_by_token_positive(
        parametrize_identity: tuple[ulid.ULID, None] | tuple[None, str],
        organization_repo: 'OrganizationPostgresRepository',
        organization_in_db: 'OrganizationORM',
        organization_token: str,
):
    _id, name = parametrize_identity
    org = await organization_repo.get_organization_by_token(_id, name, organization_token)
    assert org == organization_in_db


@pytest.mark.parametrize('use_real_id', [True, False])
async def test_get_organization_by_token_negative_wrong_token_or_no_user(
        use_real_id,
        organization_repo,
        organization_in_db,
):
    org = await organization_repo.get_organization_by_token(
        organization_in_db.id if use_real_id else ulid.ULID(),
        None,
        'random_string',
    )

    assert org is None


@pytest.fixture
def input_data(
        request: pytest.FixtureRequest,
        organization_update_in_factory: 'OrganizationUpdateInFactory',
) -> 'OrganizationUpdateIn':
    use_name, use_token = request.param
    if use_token and not use_name:
        return organization_update_in_factory.build(new_name=None)
    elif not use_token and use_name:
        return organization_update_in_factory.build(new_token=None)
    elif not use_token and not use_name:
        return organization_update_in_factory.build(new_token=None, new_name=None)
    else:
        return organization_update_in_factory.build()


@pytest.mark.parametrize(
    'input_data',
    ([True, True], [True, False], [False, True], [False, False],),
    indirect=True,
)
async def test_update_organization_positive_token_and_name(
        input_data,
        organization_in_db,
        organization_repo,
        organization_token,
):
    await organization_repo.update_organization(
        name=organization_in_db.name,
        data=input_data,
    )

    assert await organization_repo.get_organization_by_token(
        _id=None,
        name=input_data.new_name or organization_in_db.name,
        token=input_data.new_token.get_secret_value() if input_data.new_token else organization_token,
    )

