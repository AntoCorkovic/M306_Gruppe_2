import csv
import json
from typing import List, BinaryIO
from src.models.counterstands import Counterstands
from io import StringIO


class Converter:
    def __init__(self):
        self.sensor_ids = ["ID742", "ID735"]

    def _prepare_data(self, counterstands_list: List[Counterstands]) -> dict:
        data = {sensor_id: [] for sensor_id in self.sensor_ids}

        for counterstand in counterstands_list:
            for period in counterstand.timePeriods:
                for value_row in period.valueRows:
                    sensor_id = "ID742" if value_row.obis in ["1-1:1.8.1", "1-1:1.8.2"] else "ID735"
                    timestamp = int(period.end.timestamp())
                    value = value_row.value

                    data[sensor_id].append({
                        "ts": timestamp,
                        "value": value
                    })

        return data

    def export_to_json(self, counterstands_list: List[Counterstands], file: BinaryIO) -> None:
        data = self._prepare_data(counterstands_list)

        json_data = [
            {
                "sensorId": sensor_id,
                "data": sensor_data
            } for sensor_id, sensor_data in data.items()
        ]

        # Convert to JSON string
        json_string = json.dumps(json_data, indent=2)

        # Write the JSON string as bytes to the file
        file.write(json_string.encode('utf-8'))

    def export_to_csv(self, counterstands_list: List[Counterstands], file: BinaryIO, sensor_id: str) -> None:
        data = self._prepare_data(counterstands_list)

        # Create a text stream
        text_stream = StringIO()
        writer = csv.writer(text_stream)
        writer.writerow(["timestamp", "value"])
        for entry in data[sensor_id]:
            writer.writerow([entry["ts"], entry["value"]])

        # Get the CSV as a string and encode it to bytes
        csv_bytes = text_stream.getvalue().encode('utf-8')

        # Write the bytes to the file
        file.write(csv_bytes)