from dataclasses import dataclass

@dataclass
class Material:
    id: int
    unit_of_weight: str
    material_type_name: str