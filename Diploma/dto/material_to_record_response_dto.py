from dataclasses import dataclass

@dataclass
class MaterialToRecordResponseDto:
    material_type_name: str
    count: int