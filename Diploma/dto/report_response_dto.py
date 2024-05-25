from dataclasses import dataclass
from typing import List

from dto.material_to_record_response_dto import MaterialToRecordResponseDto


@dataclass
class ReportResponseDto:
    user_id: int
    materials: List[MaterialToRecordResponseDto]
    comments: str
