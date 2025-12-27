from pydantic import BaseModel


class DedupPairOut(BaseModel):
    a_id: int
    b_id: int
    a_name: str
    b_name: str
    score: float
    reason: str