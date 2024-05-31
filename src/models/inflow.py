from dataclasses import dataclass, field
from typing import List


@dataclass
class EICID:
    value: str
    schemeAgencyID: str

@dataclass
class Sender:
    EICID: EICID
    Role: str

@dataclass
class Receiver:
    EICID: EICID
    Role: str

@dataclass
class InstanceDocument:
    DictionaryAgencyID: str
    VersionID: str
    DocumentID: str
    ebIXCode: str
    Creation: str
    Status: str

@dataclass
class BusinessScopeProcess:
    BusinessReasonType: str
    BusinessDomainType: str
    BusinessSectorType: str
    StartDateTime: str
    EndDateTime: str
    isIntelligibleCheckRequired: bool

@dataclass
class HeaderInformation:
    HeaderVersion: str
    Sender: Sender
    Receiver: Receiver
    InstanceDocument: InstanceDocument
    BusinessScopeProcess: BusinessScopeProcess

@dataclass
class Observation:
    Sequence: int
    Volume: float

@dataclass
class MeteringData:
    DocumentID: str
    StartDateTime: str
    EndDateTime: str
    Resolution: int
    Unit: str
    VSENationalID: str
    schemeID: str
    schemeAgencyID: str
    ProductID: str
    MeasureUnit: str
    Observations: List[Observation] = field(default_factory=list)




@dataclass
class Inflow:
    HeaderInformation: HeaderInformation
    MeteringData: MeteringData
