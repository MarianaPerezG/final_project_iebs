import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import __main__

from scripts.pipelines import run_pipeline
from api.singleton import get_courses_api

sys.path.append(str(Path(__file__).parent))

load_dotenv()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    env = os.getenv("ENV", "dev").lower()
    logger.warning(f"ENV: {env}")
    __main__.DEV_MODE = env == "dev"
    if __main__.DEV_MODE:
        logger.warning("DEVELOPMENT MODE ON")

    get_courses_api()
    logging.info("Course API initialized")

    run_pipeline()
