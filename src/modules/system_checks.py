import datetime
import psutil
import src


class SystemCheckModule(src.utils.ModuleBaseClass):
    def __init__(self, config: src.types.Config) -> None:
        self.config = config
        self.logger = src.utils.Logger(
            config=self.config, origin="system-checks"
        )

    def run(self) -> None:
        """Logs the system load and last boot time."""

        loads = psutil.getloadavg()
        load_last_1_min = round(loads[0], 2)
        load_last_5_min = round(loads[1], 2)
        load_last_15_min = round(loads[2], 2)
        self.logger.debug(
            "Average system load (last 1/5/15 minutes) [%]:" +
            f" {load_last_1_min}/{load_last_5_min}/{load_last_15_min}"
        )

        if load_last_5_min > 70:
            self.logger.warning(
                "System load is very high (above 70% in the last 50 minutes)"
            )

        last_boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        self.logger.debug(f"Last boot time: {last_boot_time}")

    def teardown(self) -> None:
        self.logger.debug("nothing to tear down")
