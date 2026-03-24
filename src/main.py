import logging

from scripts.pipelines import run_pipeline


if __name__ == "__main__":
   
   logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
   )

   logger = logging.getLogger(__name__)
         
   run_pipeline()
    
