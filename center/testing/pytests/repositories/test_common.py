import ulid

from center.repositories.postgres import OrganizationPostgresRepository


async def test_positive_exists(organization_in_db):
    assert await OrganizationPostgresRepository().exists(organization_in_db.id)


async def test_negative_exists(organization_in_db):
    assert not await OrganizationPostgresRepository().exists(ulid.ULID())

