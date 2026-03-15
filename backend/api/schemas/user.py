from pydantic import BaseModel
from typing import Optional

class UserProfile(BaseModel):
    id: int
    username: Optional[str]
    role: str
    bonus_balance: float
    loyalty_level: str
    total_spent: float
