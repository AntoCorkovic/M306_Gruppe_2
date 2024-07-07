import csv
import json
from io import StringIO
from typing import List, BinaryIO
from src.models.counterstands import Counterstands
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class Converter:
    def export_counterstands_to_csv(self, counterstands_list: List[Counterstands], file: BinaryIO) -> None:
        output = StringIO()
        writer = csv.writer(output)
        # Writing headers
        writer.writerow(['Created', 'End', 'OBIS', 'Value', 'Status', 'ValueTimeStamp'])

        for counterstand in counterstands_list:
            for period in counterstand.timePeriods:
                for value_row in period.valueRows:
                    writer.writerow([
                        counterstand.created.strftime("%Y-%m-%dT%H:%M:%S"),
                        period.end,
                        value_row.obis,
                        value_row.value,
                        value_row.status,
                        value_row.valueTimeStamp
                    ])

        file.write(output.getvalue().encode('utf-8'))

    def export_counterstands_to_json(self, counterstands_list: List[Counterstands], file: BinaryIO) -> None:
        json_data = []
        for counterstand in counterstands_list:
            entry = {
                'created': counterstand.created,  # No need to convert to string here
                'timePeriods': [
                    {
                        'end': period.end,
                        'valueRows': [
                            {
                                'obis': value_row.obis,
                                'value': value_row.value,
                                'status': value_row.status,
                                'valueTimeStamp': value_row.valueTimeStamp
                            } for value_row in period.valueRows
                        ]
                    } for period in counterstand.timePeriods
                ]
            }
            json_data.append(entry)

        json_string = json.dumps(json_data, cls=DateTimeEncoder, indent=4)
        file.write(json_string.encode('utf-8'))
