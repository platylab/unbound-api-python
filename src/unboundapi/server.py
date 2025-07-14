import os
import sys
from subprocess import run


def start():
    config_path = os.path.join(os.path.dirname(__file__), "gunicorn_config.py")
    run(
        [
            sys.executable,
            "-m",
            "gunicorn",
            "--config",
            config_path,
            "unboundapi.app:app",
        ],
    )


if __name__ == "__main__":
    start()
