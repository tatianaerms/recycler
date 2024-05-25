from dataclasses import dataclass

@dataclass
class MaterialToRecord:
    id: int
    record_id: int
    material_type_name: str
    count: int