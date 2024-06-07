from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class Observation:
    Sequence: int
    Volume: float

@dataclass
class Consumptionvalues:
    DocumentID: str = ""
    StartDateTime: datetime = field(default_factory=datetime.now)
    EndDateTime: datetime = field(default_factory=datetime.now)
    Resolution: int = 0
    Unit: str = ""
    Observations: List[Observation] = field(default_factory=list)

@dataclass
class InflowAndOutflow:
    Inflows: List[Consumptionvalues] = field(default_factory=list)
    Outflows: List[Consumptionvalues] = field(default_factory=list)


