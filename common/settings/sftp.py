from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class SFTPSettings(BaseSettings):
    SFTP_HOST: Annotated[
        str,
        Field(description='Хост для SFTP.', ),
    ]
    SFTP_USERNAME: Annotated[
        str,
        Field(description='Юзернайм для SFTP.', )
    ]
    SFTP_PASSWORD: Annotated[
        SecretStr,
        Field(description='Пароль для SFTP.', repr=False)
    ]
