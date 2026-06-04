from enum import StrEnum

from pydantic import BaseModel


class AssetType(StrEnum):
    HAUL_TRUCK = "haul_truck"
    EXCAVATOR = "excavator"
    DRILL = "drill"
    DOZER = "dozer"
    GRADER = "grader"


class Asset(BaseModel):
    id: str
    name: str
    asset_type: AssetType

