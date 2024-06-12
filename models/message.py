from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    from_id: int
    to_id: int
    body: str
    attachment: Optional[str] = None
    seen: bool

