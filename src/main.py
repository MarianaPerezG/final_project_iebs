import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse
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

    parser = argparse.ArgumentParser(description="Run the data processing pipeline")
    parser.add_argument(
        "--env", type=str, default="dev", help="Set the environment (dev or prod)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in testing mode (skip data downloads, only recommendations)",
    )
    args = parser.parse_args()

    env = args.env.lower()
    recommendation_testing_mode_on = args.test

    __main__.DEV_MODE = env == "dev"
    __main__.RECOMMENDATION_TESTING_MODE_ON = recommendation_testing_mode_on

    if __main__.DEV_MODE:
        logger.warning("⚡ DEVELOPMENT MODE ON")
    if __main__.RECOMMENDATION_TESTING_MODE_ON:
        logger.warning("RECOMMENDATION TESTING MODE ON - Skipping data downloads")

    get_courses_api()
    logging.info("Course API initialized")

    run_pipeline()
