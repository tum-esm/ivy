import abc
import src


class ModuleBaseClass(abc.ABC):
    @abc.abstractmethod
    def __init__(self, config: src.types.Config) -> None:
        pass

    @abc.abstractmethod
    def run(self) -> None:
        pass

    @abc.abstractmethod
    def teardown(self) -> None:
        pass
