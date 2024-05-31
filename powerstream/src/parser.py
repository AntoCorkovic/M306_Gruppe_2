import os
import xml.etree.ElementTree as ET

from powerstream.src.models.outflow import *
from powerstream.src.models.inflow import *


class Parser:
    OUTFLOW_DIRECTORY = '../../testdata/ESL-Files/'
    INFLOW_DIRECTORY = '../../testdata/SDAT-Files/'

    def parse_Outflow(self) -> List[Outflow]:
        outflowlist = []
        for file in os.listdir(self.OUTFLOW_DIRECTORY):
            tree = ET.parse(self.OUTFLOW_DIRECTORY + '/' + file)
            root = tree.getroot()

            # Parsing Header
            header_elem = root.find('Header')
            header = Header(
                version=header_elem.get('version'),
                created=header_elem.get('created'),
                swSystemNameFrom=header_elem.get('swSystemNameFrom'),
                swSystemNameTo=header_elem.get('swSystemNameTo')
            )

            # Parsing Meters
            meters = []
            for meter_elem in root.findall('Meter'):
                meter = Meter(
                    factoryNo=meter_elem.get('factoryNo'),
                    internalNo=meter_elem.get('internalNo')
                )

                # Parsing TimePeriods
                for time_period_elem in meter_elem.findall('TimePeriod'):
                    time_period = TimePeriod(end=time_period_elem.get('end'))

                    # Parsing ValueRows
                    for value_row_elem in time_period_elem.findall('ValueRow'):
                        value_row = ValueRow(
                            obis=value_row_elem.get('obis'),
                            value=float(value_row_elem.get('value')),
                            status=value_row_elem.get('status'),
                            valueTimeStamp=value_row_elem.get('valueTimeStamp')
                        )
                        time_period.valueRows.append(value_row)

                    meter.timePeriods.append(time_period)
                meters.append(meter)

            outflowlist.append(Outflow(header=header, meters=meters))
        return outflowlist

    def parse_Inflow(self) -> List[Inflow]:
        inflowlist = []
        for file in os.listdir(self.INFLOW_DIRECTORY):
            try:
                tree = ET.parse(self.INFLOW_DIRECTORY + '/' + file)
                root = tree.getroot()
                ns = {'rsm': 'http://www.strom.ch'}

                # Parsing HeaderInformation
                header_info_elem = root.find('rsm:ValidatedMeteredData_HeaderInformation', ns)

                sender_elem = header_info_elem.find('rsm:Sender', ns)
                sender = Sender(
                    EICID=EICID(
                        value=sender_elem.find('rsm:ID/rsm:EICID', ns).text,
                        schemeAgencyID=sender_elem.find('rsm:ID/rsm:EICID', ns).attrib['schemeAgencyID']
                    ),
                    Role=sender_elem.find('rsm:Role', ns).text
                )

                receiver_elem = header_info_elem.find('rsm:Receiver', ns)
                receiver = Receiver(
                    EICID=EICID(
                        value=receiver_elem.find('rsm:ID/rsm:EICID', ns).text,
                        schemeAgencyID=receiver_elem.find('rsm:ID/rsm:EICID', ns).attrib['schemeAgencyID']
                    ),
                    Role=receiver_elem.find('rsm:Role', ns).text
                )

                instance_doc_elem = header_info_elem.find('rsm:InstanceDocument', ns)
                instance_document = InstanceDocument(
                    DictionaryAgencyID=instance_doc_elem.find('rsm:DictionaryAgencyID', ns).text,
                    VersionID=instance_doc_elem.find('rsm:VersionID', ns).text,
                    DocumentID=instance_doc_elem.find('rsm:DocumentID', ns).text,
                    ebIXCode=instance_doc_elem.find('rsm:DocumentType/rsm:ebIXCode', ns).text,
                    Creation=instance_doc_elem.find('rsm:Creation', ns).text,
                    Status=instance_doc_elem.find('rsm:Status', ns).text
                )

                business_scope_elem = header_info_elem.find('rsm:BusinessScopeProcess', ns)
                business_scope_process = BusinessScopeProcess(
                    BusinessReasonType=business_scope_elem.find('rsm:BusinessReasonType/rsm:ebIXCode', ns).text,
                    BusinessDomainType=business_scope_elem.find('rsm:BusinessDomainType', ns).text,
                    BusinessSectorType=business_scope_elem.find('rsm:BusinessSectorType', ns).text,
                    StartDateTime=business_scope_elem.find('rsm:ReportPeriod/rsm:StartDateTime', ns).text,
                    EndDateTime=business_scope_elem.find('rsm:ReportPeriod/rsm:EndDateTime', ns).text,
                    isIntelligibleCheckRequired=
                    business_scope_elem.find('rsm:BusinessService/rsm:ServiceTransaction', ns).attrib[
                        'isIntelligibleCheckRequired'] == 'true'
                )

                header_information = HeaderInformation(
                    HeaderVersion=header_info_elem.find('rsm:HeaderVersion', ns).text,
                    Sender=sender,
                    Receiver=receiver,
                    InstanceDocument=instance_document,
                    BusinessScopeProcess=business_scope_process
                )

                # Parsing MeteringData
                metering_data_elem = root.find('rsm:MeteringData', ns)

                observations = []
                for observation_elem in metering_data_elem.findall('rsm:Observation', ns):
                    observation = Observation(
                        Sequence=int(observation_elem.find('rsm:Position/rsm:Sequence', ns).text),
                        Volume=float(observation_elem.find('rsm:Volume', ns).text)
                    )
                    observations.append(observation)

                metering_data = MeteringData(
                    DocumentID=metering_data_elem.find('rsm:DocumentID', ns).text,
                    StartDateTime=metering_data_elem.find('rsm:Interval/rsm:StartDateTime', ns).text,
                    EndDateTime=metering_data_elem.find('rsm:Interval/rsm:EndDateTime', ns).text,
                    Resolution=int(metering_data_elem.find('rsm:Resolution/rsm:Resolution', ns).text),
                    Unit=metering_data_elem.find('rsm:Resolution/rsm:Unit', ns).text,
                    VSENationalID=metering_data_elem.find('rsm:ProductionMeteringPoint/rsm:VSENationalID', ns).text,
                    schemeID=metering_data_elem.find('rsm:ProductionMeteringPoint/rsm:VSENationalID', ns).attrib[
                        'schemeID'],
                    schemeAgencyID=metering_data_elem.find('rsm:ProductionMeteringPoint/rsm:VSENationalID', ns).attrib[
                        'schemeAgencyID'],
                    ProductID=metering_data_elem.find('rsm:Product/rsm:ID', ns).text,
                    MeasureUnit=metering_data_elem.find('rsm:Product/rsm:MeasureUnit', ns).text,
                    Observations=observations
                )

                inflowlist.append(Inflow(HeaderInformation=header_information, MeteringData=metering_data))
            except Exception as e:
                continue;
        return inflowlist
