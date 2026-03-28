from pydantic import BaseModel
from typing import Optional, List

class OrderCreate(BaseModel):
    client_id: int
    work_type: str
    subject: str
    topic: str
    teacher: Optional[str] = None
    requirements: Optional[str] = None
    antiplagiat_percent: Optional[int] = None
    deadline: Optional[str] = None
    urgency: Optional[str] = None
    attachments: Optional[List[str]] = []
