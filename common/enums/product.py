import enum


class ProductUnit(str, enum.Enum):
    """
    Варианты упаковки продукта.
    """
    BOX = 'box'
    PACKET = 'packet'
    PLASTIC_BOTTLE = 'plastic_bottle'
    GLASS_BOTTLE = 'glass_bottle'
    PALLET = 'pallet'
    IN_BULK = 'in_bulk'
    CONTAINER = 'container'
    CISTERN = 'cistern'
    WITHOUT_PACKAGE = 'without_package'
