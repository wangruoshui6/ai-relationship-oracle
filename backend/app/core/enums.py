from enum import Enum


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class RelationshipTypeEnum(str, Enum):
    EX = "ex"
    CURRENT = "current"
    CRUSH = "crush"
    SPOUSE = "spouse"
    FRIEND = "friend"
    UNKNOWN = "unknown"
