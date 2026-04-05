from api.mock_api import MockJobAPI


class JobAPISingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api = MockJobAPI()
        return cls._instance

    def get_api(self) -> MockJobAPI:
        return self.api


def get_job_api() -> MockJobAPI:
    singleton = JobAPISingleton()
    return singleton.get_api()
