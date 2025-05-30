import typing

import pytest

if typing.TYPE_CHECKING:
    import ulid
    from center.orm_models import OrganizationORM
    from center.repositories.postgres import OrganizationPostgresRepository


@pytest.fixture
def parametrize_identity(request: pytest.FixtureRequest, organization_in_db: 'OrganizationORM') -> (
        tuple['ulid.ULID', None] | tuple[None, 'ulid.ULID']):
    use_id, use_name = request.param
    return (
        organization_in_db.id if use_id else None,
        organization_in_db.name if use_name else None,
    )


@pytest.mark.parametrize('parametrize_identity', [(True, False), (False, True)], indirect=True)
async def test_get_organization_by_token_positive(
        parametrize_identity: tuple['ulid.ULID', None] | tuple[None, 'ulid.ULID'],
        organization_repo: 'OrganizationPostgresRepository',
        organization_in_db: 'OrganizationORM',
        organization_token: str,
):
    _id, name = parametrize_identity
    org = await organization_repo.get_organization_by_token(_id, name, organization_token)
    assert org == organization_in_db