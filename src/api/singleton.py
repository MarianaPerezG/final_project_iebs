from api.mock_api import MockCourseAPI


class CourseSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api = MockCourseAPI()
        return cls._instance

    def get_api(self) -> MockCourseAPI:
        return self.api


def get_courses_api() -> MockCourseAPI:
    singleton = CourseSingleton()
    return singleton.get_api()
