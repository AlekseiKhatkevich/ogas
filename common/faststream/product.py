from faststream.kafka import KafkaRouter
from pydantic import Field

from common.enums.product import ProductUnit
from common.faststream.filters import contentype_json
from common.usecases.product import UpsertProductUseCase

router = KafkaRouter(prefix='products_')


@router.subscriber('in', filter=contentype_json, title='add-update-product',)
async def create_or_update_product(
    name: str = Field(description='Название продукта',),
    unit: ProductUnit = Field(description='Вариант упаковки продукта',),
    standard_code: str = Field(description='ГОСТ',),
    categories: set[str] = Field(description='Категории продукта', default_factory=set),
) -> None:
    await UpsertProductUseCase(name, unit, standard_code, categories).execute()
