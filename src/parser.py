import os
import xml.etree.ElementTree as elementTree

from werkzeug.datastructures import FileStorage

from src.models.counterstands import *
from src.models.consumptionvalues import *
from datetime import timedelta
from typing import List
from src.models.consumptionvalues import Observation


class Parser:
    OUTFLOW_DIRECTORY = '../testdata/ESL-Files/'
    INFLOW_DIRECTORY = '../testdata/SDAT-Files/'

    def parse_counterstands(self) -> List[Counterstands]:
        counterstands_dict = {}

        for file in os.listdir(self.OUTFLOW_DIRECTORY):
            try:
                tree = elementTree.parse(os.path.join(self.OUTFLOW_DIRECTORY, file))
                root = tree.getroot()

                # Parsing Header
                header_elem = root.find('Header')
                created_str = header_elem.get('created')
                created = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S")
                created_date = created.date()

                # Check if there is already an entry for this date
                if created_date not in counterstands_dict:
                    counterstands_dict[created_date] = Counterstands(created=created)

                for time_period_elem in root.findall('.//TimePeriod'):
                    time_period = TimePeriod(end=datetime.strptime(time_period_elem.get('end'), "%Y-%m-%dT%H:%M:%S"))

                    # Parsing ValueRows
                    for value_row_elem in time_period_elem.findall('ValueRow'):
                        value_row = ValueRow(
                            obis=value_row_elem.get('obis'),
                            value=float(value_row_elem.get('value')),
                            status=value_row_elem.get('status'),
                            valueTimeStamp=value_row_elem.get('valueTimeStamp')
                        )
                        time_period.valueRows.append(value_row)

                    counterstands_dict[created_date].timePeriods.append(time_period)

            except elementTree.ParseError as e:
                print(f"Error parsing {file}: {e}")
            except Exception as e:
                print(f"Unexpected error with {file}: {e}")

        counterstands_list = list(counterstands_dict.values())
        counterstands_list.sort(key=lambda x: x.created)

        return counterstands_list

    def parse_consumptionvalues(self) -> InflowAndOutflow():
        inflowandoutflowlist = InflowAndOutflow()
        for file in os.listdir(self.INFLOW_DIRECTORY):
            try:
                tree = elementTree.parse(self.INFLOW_DIRECTORY + '/' + file)
                root = tree.getroot()
                ns = {'rsm': 'http://www.strom.ch'}

                consumption_values = Consumptionvalues()

                # Parsing HeaderInformation
                header_info_elem = root.find('rsm:ValidatedMeteredData_HeaderInformation', ns)

                instance_doc_elem = header_info_elem.find('rsm:InstanceDocument', ns)

                consumption_values.DocumentID = str(instance_doc_elem.find('rsm:DocumentID', ns).text),

                # Parsing MeteringData
                metering_data_elem = root.find('rsm:MeteringData', ns)

                observations = []
                for observation_elem in metering_data_elem.findall('rsm:Observation', ns):
                    observation = Observation(
                        Sequence=int(observation_elem.find('rsm:Position/rsm:Sequence', ns).text),
                        Volume=float(observation_elem.find('rsm:Volume', ns).text)
                    )
                    observations.append(observation)
                consumption_values.Observations = observations
                consumption_values.StartDateTime = datetime.strptime(
                    metering_data_elem.find('rsm:Interval/rsm:StartDateTime', ns).text, "%Y-%m-%dT%H:%M:%SZ")
                consumption_values.EndDateTime = datetime.strptime(
                    metering_data_elem.find('rsm:Interval/rsm:EndDateTime', ns).text, "%Y-%m-%dT%H:%M:%SZ")
                consumption_values.Resolution = int(metering_data_elem.find('rsm:Resolution/rsm:Resolution', ns).text)
                consumption_values.Unit = metering_data_elem.find('rsm:Resolution/rsm:Unit', ns).text

                if consumption_values.DocumentID[0].split('_')[-1] == "ID735":
                    if not any(existing.StartDateTime == consumption_values.StartDateTime for existing in
                               inflowandoutflowlist.Outflows):
                        inflowandoutflowlist.Outflows.append(consumption_values)
                elif consumption_values.DocumentID[0].split('_')[-1] == "ID742":
                    if not any(existing.StartDateTime == consumption_values.StartDateTime for existing in
                               inflowandoutflowlist.Inflows):
                        inflowandoutflowlist.Inflows.append(consumption_values)
                else:
                    continue
            except Exception as e:
                continue
        inflowandoutflowlist.Inflows.sort(key=lambda x: x.StartDateTime)
        inflowandoutflowlist.Outflows.sort(key=lambda x: x.StartDateTime)
        return inflowandoutflowlist

    def parse_counterstands_for_upload(self, files: List[FileStorage]) -> List[Counterstands]:
        counterstands_dict = {}

        for file in files:
            try:
                # Read the file content from the FileStorage object
                file_content = file.read()
                tree = elementTree.ElementTree(elementTree.fromstring(file_content))
                root = tree.getroot()

                # Parsing Header
                header_elem = root.find('Header')
                created_str = header_elem.get('created')
                created = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S")
                created_date = created.date()

                # Check if there is already an entry for this date
                if created_date not in counterstands_dict:
                    counterstands_dict[created_date] = Counterstands(created=created)

                for time_period_elem in root.findall('.//TimePeriod'):
                    time_period = TimePeriod(end=datetime.strptime(time_period_elem.get('end'), "%Y-%m-%dT%H:%M:%S"))

                    # Parsing ValueRows
                    for value_row_elem in time_period_elem.findall('ValueRow'):
                        value_row = ValueRow(
                            obis=value_row_elem.get('obis'),
                            value=float(value_row_elem.get('value')),
                            status=value_row_elem.get('status'),
                            valueTimeStamp=value_row_elem.get('valueTimeStamp')
                        )
                        time_period.valueRows.append(value_row)

                    counterstands_dict[created_date].timePeriods.append(time_period)

            except elementTree.ParseError as e:
                print(f"Error parsing {file.filename}: {e}")
            except Exception as e:
                print(f"Unexpected error with {file.filename}: {e}")

        counterstands_list = list(counterstands_dict.values())
        counterstands_list.sort(key=lambda x: x.created)

        return counterstands_list

    def parse_consumptionvalues_for_upload(self, files: List[FileStorage]) -> InflowAndOutflow:
        inflowandoutflowlist = InflowAndOutflow()
        ns = {'rsm': 'http://www.strom.ch'}

        for file in files:
            try:
                # Read the file content from the FileStorage object
                file_content = file.read()
                tree = elementTree.ElementTree(elementTree.fromstring(file_content))
                root = tree.getroot()

                consumption_values = Consumptionvalues()

                # Parsing HeaderInformation
                header_info_elem = root.find('rsm:ValidatedMeteredData_HeaderInformation', ns)
                instance_doc_elem = header_info_elem.find('rsm:InstanceDocument', ns)
                consumption_values.DocumentID = str(instance_doc_elem.find('rsm:DocumentID', ns).text),

                # Parsing MeteringData
                metering_data_elem = root.find('rsm:MeteringData', ns)

                observations = []
                for observation_elem in metering_data_elem.findall('rsm:Observation', ns):
                    observation = Observation(
                        Sequence=int(observation_elem.find('rsm:Position/rsm:Sequence', ns).text),
                        Volume=float(observation_elem.find('rsm:Volume', ns).text)
                    )
                    observations.append(observation)
                consumption_values.Observations = observations
                consumption_values.StartDateTime = datetime.strptime(
                    metering_data_elem.find('rsm:Interval/rsm:StartDateTime', ns).text, "%Y-%m-%dT%H:%M:%SZ")
                consumption_values.EndDateTime = datetime.strptime(
                    metering_data_elem.find('rsm:Interval/rsm:EndDateTime', ns).text, "%Y-%m-%dT%H:%M:%SZ")
                consumption_values.Resolution = int(metering_data_elem.find('rsm:Resolution/rsm:Resolution', ns).text)
                consumption_values.Unit = metering_data_elem.find('rsm:Resolution/rsm:Unit', ns).text

                if consumption_values.DocumentID[0].split('_')[-1] == "ID735":
                    if not any(existing.StartDateTime == consumption_values.StartDateTime for existing in
                               inflowandoutflowlist.Outflows):
                        inflowandoutflowlist.Outflows.append(consumption_values)
                elif consumption_values.DocumentID[0].split('_')[-1] == "ID742":
                    if not any(existing.StartDateTime == consumption_values.StartDateTime for existing in
                               inflowandoutflowlist.Inflows):
                        inflowandoutflowlist.Inflows.append(consumption_values)
                else:
                    continue
            except Exception as e:
                print(f"Error parsing {file.filename}: {e}")
                continue

        inflowandoutflowlist.Inflows.sort(key=lambda x: x.StartDateTime)
        inflowandoutflowlist.Outflows.sort(key=lambda x: x.StartDateTime)
        return inflowandoutflowlist

    def get_nearest_older_observation(self, inflows, start):
        older_observations = [obs for obs in inflows if obs.StartDateTime <= start]

        if not older_observations:
            return None

        nearest_observation = min(older_observations, key=lambda obs: start - obs.StartDateTime)
        return nearest_observation

    def find_closest_time_period(self, counterstands: List[Counterstands], end_date: datetime, obis) -> Optional[dict]:
        closest_time_period = None
        closest_time_diff = timedelta.max

        for counterstand in counterstands:
            for time_period in counterstand.timePeriods:
                obis_set = {row.obis for row in time_period.valueRows}
                if obis.issubset(obis_set):
                    time_diff = end_date - time_period.end
                    if timedelta(0) <= time_diff < closest_time_diff:
                        closest_time_diff = time_diff
                        closest_time_period = time_period

        if closest_time_period:
            filtered_value_rows = [row for row in closest_time_period.valueRows if row.obis in obis]
            total_value = sum(row.value for row in filtered_value_rows)
            return {
                "end": closest_time_period.end,
                "total_value": total_value
            }

        return None

    def get_observations_for_specific_duration(self, start: datetime, end: datetime, flows: []) -> list[Observation]:
        nearest_consumption = self.get_nearest_older_observation(flows, start)
        countofvolums = int((end - start).total_seconds() / 60 / 15)
        volumnstoskip = int((start - nearest_consumption.StartDateTime).seconds / 60 / 15)
        if len(nearest_consumption.Observations) - volumnstoskip >= countofvolums:
            return nearest_consumption.Observations[volumnstoskip:(volumnstoskip + countofvolums)]
        else:
            return nearest_consumption.Observations[
                   volumnstoskip:len(nearest_consumption.Observations)] + self.get_observations_for_specific_duration(
                nearest_consumption.EndDateTime, end, flows)

    def get_counter_stand(self, start: datetime, counterstands: List[Counterstands], flows: [], obis) -> float:
        timeperiod = self.find_closest_time_period(counterstands, start, obis)
        observation_between_last_counterstandand_startdate = self.get_observations_for_specific_duration(
            timeperiod["end"],
            start, flows)
        return timeperiod["total_value"] - sum(obs.Volume for obs in observation_between_last_counterstandand_startdate)
