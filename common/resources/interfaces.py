from abc import ABC, abstractmethod


class HealthCheckable(ABC):

    @abstractmethod
    async def check_health(self) -> bool:
        pass

    @property
    @abstractmethod
    def service_name(self) -> str:
        pass
