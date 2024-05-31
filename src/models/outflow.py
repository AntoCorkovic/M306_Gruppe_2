from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValueRow:
    obis: str
    value: float
    status: str
    valueTimeStamp: Optional[str] = None


@dataclass
class TimePeriod:
    end: str
    valueRows: List[ValueRow] = field(default_factory=list)


@dataclass
class Meter:
    factoryNo: str
    internalNo: str
    timePeriods: List[TimePeriod] = field(default_factory=list)


@dataclass
class Header:
    version: str
    created: str
    swSystemNameFrom: str
    swSystemNameTo: str


@dataclass
class Outflow:
    header: Header
    meters: List[Meter] = field(default_factory=list)
