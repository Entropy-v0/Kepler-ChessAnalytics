from config.settings import setup_environment
from controllers.ingestion_controller import IngestionController

def main():
    setup_environment()
    controller = IngestionController()
    controller.run_pipeline()

if __name__ == "__main__":
    main()