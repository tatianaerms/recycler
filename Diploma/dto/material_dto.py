from dataclasses import dataclass

@dataclass
class MaterialDto:
    material_type_name: str
    cnt: int