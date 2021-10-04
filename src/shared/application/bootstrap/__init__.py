from __future__ import annotations

import os
import time
from importlib import util

from shared.infrastructure.environment.settings import Settings
from shared.infrastructure.logging.file.logger import FileLogger
import shared.infrastructure.environment.globalvars as glob
import shared.infrastructure.dic.container as container


class Bootstrap:
    def __init__(self):
        glob.settings = Settings(
            os.environ.get("SITE"),
            os.environ.get("ENVIRONMENT", "development"),
        )

        glob.container = container.create_container(glob.settings)
        os.environ["TZ"] = glob.settings.time_zone()
        time.tzset()

        self.logger = FileLogger()
        self.settings = glob.settings

        self.generate_db_maps()

    def generate_db_maps(self) -> Bootstrap:
        self.logger.info("Generating database tables mappings")
        for mapping_class in glob.settings.db_mapping_classes():
            module_name, class_name = mapping_class.rsplit(".", 1)

            try:
                spec = util.find_spec(module_name)
                module = util.module_from_spec(spec)
                spec.loader.exec_module(module)

                class_ = getattr(module, class_name)
                mapper = class_()
                mapper.map_entities()

                self.logger.info("Database tables mappings generated")
            except (ModuleNotFoundError, AttributeError):
                continue

        return self
