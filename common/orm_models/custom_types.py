import ulid
from sqlalchemy.types import UserDefinedType


class ULID(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return 'ULID'

    def bind_processor(self, dialect):
        def process(value):
            return str(value)

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return ulid.ULID.from_str(value) if value is not None else value

        return process
