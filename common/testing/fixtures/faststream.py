from typing import AsyncGenerator

import pytest
from faststream.kafka import KafkaBroker, TestKafkaBroker

from faststream_serve import broker


@pytest.fixture
async def kafka_broker() -> AsyncGenerator[KafkaBroker]:
    async with TestKafkaBroker(broker) as br:
        yield br
