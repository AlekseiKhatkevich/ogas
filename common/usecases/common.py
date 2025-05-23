import abc


class AbstractUseCase(abc.ABC):
    @abc.abstractmethod
    async def execute(self):
        pass
