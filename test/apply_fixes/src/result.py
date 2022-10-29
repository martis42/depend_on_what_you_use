from abc import ABC, abstractmethod


class Result(ABC):
    def __init__(self, error: str = "") -> None:
        self.error = error

    @abstractmethod
    def is_success(self) -> bool:
        pass


class Error(Result):
    def __init__(self, error: str) -> None:
        super().__init__(error)

    def is_success(self) -> bool:
        return False


class Success(Result):
    def __init__(self) -> None:
        super().__init__()

    def is_success(self) -> bool:
        return True
