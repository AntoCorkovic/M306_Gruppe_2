from src.models.outflow import Outflow, TimePeriod, ValueRow, Header, Meter
import xml.etree.ElementTree as ET


class Parser:
    def parse_Outflow(self, file_path: str) -> Outflow:
        tree = ET.parse(file_path)
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

        return Outflow(header=header, meters=meters)
