import csv
import json
from typing import List
from src.models.counterstands import Counterstands
from src.models.consumptionvalues import InflowAndOutflow


class Converter:
    def export_counterstands_to_csv(self, counterstands_list: List[Counterstands], filename: str) -> None:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
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

    def export_counterstands_to_json(self, counterstands_list: List[Counterstands], filename: str) -> None:
        with open(filename, mode='w') as file:
            json_data = []
            for counterstand in counterstands_list:
                entry = {
                    'created': counterstand.created.strftime("%Y-%m-%dT%H:%M:%S"),
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
            json.dump(json_data, file, indent=4)

    def export_inflow_and_outflow_to_csv(self, inflow_and_outflow: InflowAndOutflow, filename: str) -> None:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Writing headers for Inflows and Outflows
            writer.writerow(
                ['Type', 'DocumentID', 'StartDateTime', 'EndDateTime', 'Resolution', 'Unit', 'Sequence', 'Volume'])

            for inflow in inflow_and_outflow.Inflows:
                for observation in inflow.Observations:
                    writer.writerow([
                        'Inflow',
                        inflow.DocumentID,
                        inflow.StartDateTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        inflow.EndDateTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        inflow.Resolution,
                        inflow.Unit,
                        observation.Sequence,
                        observation.Volume
                    ])

            for outflow in inflow_and_outflow.Outflows:
                for observation in outflow.Observations:
                    writer.writerow([
                        'Outflow',
                        outflow.DocumentID,
                        outflow.StartDateTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        outflow.EndDateTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        outflow.Resolution,
                        outflow.Unit,
                        observation.Sequence,
                        observation.Volume
                    ])

    def export_inflow_and_outflow_to_json(self, inflow_and_outflow: InflowAndOutflow, filename: str) -> None:
        with open(filename, mode='w') as file:
            json_data = {
                'Inflows': [
                    {
                        'DocumentID': inflow.DocumentID,
                        'StartDateTime': inflow.StartDateTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'EndDateTime': inflow.EndDateTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'Resolution': inflow.Resolution,
                        'Unit': inflow.Unit,
                        'Observations': [
                            {
                                'Sequence': observation.Sequence,
                                'Volume': observation.Volume
                            } for observation in inflow.Observations
                        ]
                    } for inflow in inflow_and_outflow.Inflows
                ],
                'Outflows': [
                    {
                        'DocumentID': outflow.DocumentID,
                        'StartDateTime': outflow.StartDateTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'EndDateTime': outflow.EndDateTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'Resolution': outflow.Resolution,
                        'Unit': outflow.Unit,
                        'Observations': [
                            {
                                'Sequence': observation.Sequence,
                                'Volume': observation.Volume
                            } for observation in outflow.Observations
                        ]
                    } for outflow in inflow_and_outflow.Outflows
                ]
            }
            json.dump(json_data, file, indent=4)