
class CaseInsensitiveMixin:
    """
    Миксин для StrEnum с помощью которого можно конструировать ENUM из сток в независимости от регистра.
    """
    # @classmethod
    # def _missing_(cls, value: str) -> str | None:
    #     value = value.lower()
    #     for member in cls:
    #         if member.value == value:
    #             return member
    #     return None

    @classmethod
    def _missing_(cls, value: str) -> str | None:
        return cls.__members__.get(value.upper(), None)
