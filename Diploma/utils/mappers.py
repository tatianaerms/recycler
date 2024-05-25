import json
from typing import List
from dataclasses import asdict

from dto.material_dto import MaterialDto


def parse_materials(json_str: str) -> List[MaterialDto]:
    # Замена одинарных кавычек на двойные
    json_str = json_str.replace("'", '"')

    # Парсинг JSON строки в список словарей
    materials_data = json.loads(json_str)

    # Преобразование списка словарей в список объектов MaterialDto
    materials = [MaterialDto(**material) for material in materials_data]

    return materials

def custom_serializer(obj):
    if isinstance(obj, bytes):
        return obj.decode('utf-8')
    if hasattr(obj, '__dataclass_fields__'):
        return asdict(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
