import typing

import pytest
import ulid

if typing.TYPE_CHECKING:
    from center.orm_models import OrganizationORM
    from center.repositories.postgres import OrganizationPostgresRepository


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
