from dataclasses import dataclass, field
from datetime import datetime
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
class Counterstands:
    created: datetime = field(default_factory=datetime.now)
    timePeriods: List[TimePeriod] = field(default_factory=list)
