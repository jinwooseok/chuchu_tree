from abc import ABC, abstractmethod

class PasswordHasher(ABC):
    """도메인에서 정의하는 추상화"""

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass