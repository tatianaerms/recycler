from dataclasses import dataclass

@dataclass
class RecycleRecord:
    id: int
    user_id: int
    created_at: str
    comments: str
