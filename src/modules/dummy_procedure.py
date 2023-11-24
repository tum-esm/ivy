import src
from .module_base_class import ModuleBaseClass


class DummyProcedureModule(ModuleBaseClass):
    def __init__(self, config: src.types.Config) -> None:
        self.config = config
        self.logger = src.utils.Logger(
            config=self.config, origin="dummy-procedure"
        )

    def run(self) -> None:
        """Fetches the weather from a weather API. You can simply remov"""

        # TODO: fetch weather from API
        # TODO: log progress
        # TODO: send out data

        pass

    def teardown(self) -> None:
        self.logger.debug("nothing to tear down")
