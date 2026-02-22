from sqlalchemy import Column, BigInteger, String, Enum
from db.database import Base
import enum

class UserRole(str, enum.Enum):
    client = "client"
    executor = "executor"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.client)

