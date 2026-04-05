import logging
import sys
from pathlib import Path

from scripts.pipelines import run_pipeline
from api.singleton import get_job_api

sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    get_job_api()
    logging.info("Job API initialized")

    run_pipeline()
