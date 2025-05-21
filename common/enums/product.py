import enum

from utils.enums import CaseInsensitiveMixin


class ProductUnit(CaseInsensitiveMixin, enum.StrEnum):
    """
    Варианты упаковки продукта.
    """
    BOX = enum.auto()
    PACKET = enum.auto()
    PLASTIC_BOTTLE = enum.auto()
    GLASS_BOTTLE = enum.auto()
    PALLET = enum.auto()
    IN_BULK = enum.auto()
    CONTAINER = enum.auto()
    CISTERN = enum.auto()
    WITHOUT_PACKAGE = enum.auto()
