from utils.utils import nested_default_dict

from enum import Enum

import json


class Recommender:

    user_id_key: str = "user_id"
    job_id_key: str = "job_id"
    activity_type_key:str = "type"
    
    def __init__(self, activities_filepath) -> None:
        self.activities_filepath = activities_filepath
        self.activities = nested_default_dict()
        self.read_activity_data()

    def read_activity_data(self) -> None:
        with open(self.activities_filepath) as input_file:
            for line in input_file:
                activity = json.loads(line)
                user_id = activity[self.user_id_key]
                job_id = activity[self.job_id_key]
                activity_type = activity[self.activity_type_key]
                try:
                    self.activities[user_id][job_id][activity_type] = self.activities[user_id][job_id][activity_type] + 1
                except TypeError:
                    self.activities[user_id][job_id][activity_type] = 1      


class Activity(Enum):
    IMPRESSION = 1
    REDIRECT = 2


if __name__ == "__main__":
    recommender = Recommender("dataset/activities.jsonl")
    recommender.activities

