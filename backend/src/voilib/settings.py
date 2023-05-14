# Copyright (c) 2022-2023 Pablo González Carrizo
# All rights reserved.

"""App configuration values.

Settings class will try to obtain, from environment variables, the
value for each configuration parameter, using the default value
defined in the class if a specific value is not found.
"""
import enum
import pathlib
import logging
import pydantic
import redis  # type: ignore
from rq import Queue  # type: ignore

CODE_DIR = pathlib.Path(__file__).parent
BACKEND_DIR = CODE_DIR.parent.parent
REPO_DIR = BACKEND_DIR.parent

logger = logging.getLogger(__name__)


class Environment(enum.Enum):
    test = "test"
    development = "development"
    production = "production"


class Settings(pydantic.BaseSettings):
    # these default values will usually apply to local (non-Docker) development
    environment: str = Environment.development.value
    code_dir: pydantic.DirectoryPath = CODE_DIR
    repo_dir: pydantic.DirectoryPath = REPO_DIR
    media_folder_name: str = "media"
    redis_host: str = "redis"
    # this user, during creation, will be automatically assigned admin
    # priviledges
    admin_username: str = "voilib-admin"
    # you can generate it with: openssl rand -hex 32
    secret_key: str = ""

    @property
    def data_dir(self) -> pathlib.Path:
        if self.environment == Environment.test.value:
            return self.repo_dir / "data-test"
        return self.repo_dir / "data"


def create_queue(settings: Settings) -> Queue:
    redis_conn = redis.Redis(settings.redis_host)
    return Queue(connection=redis_conn)


settings = Settings()
queue = create_queue(settings)
settings.data_dir.mkdir(exist_ok=True)
