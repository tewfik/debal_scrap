import os

import dotenv

ENVVARS = [
    "DEBAL_EMAIL",
    "DEBAL_PASSWORD",
    "DEBAL_TOKEN_FIELDS",
    "DEBAL_TOKEN_KEY",
]


def get_config(**config) -> dict:
    dotenv.load_dotenv()

    for envvar in ENVVARS:
        if os.environ[envvar]:
            config[envvar] = os.environ.get(envvar)
    return config
