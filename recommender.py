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

    @staticmethod
    def calculate_implicit_score(impressions: int, redirects: int) -> int:    
        impressions = impressions if impressions is not None else 0
        redirects = redirects if redirects is not None else 0
        clipped_impressions = 10 if impressions > 10 else impressions
        clipped_redirects = 10 if redirects > 10 else redirects
        scaled_redirects = clipped_redirects * 2
        overexposure_penalty = 0 if clipped_impressions - clipped_redirects < 0 else clipped_impressions - clipped_redirects
        score = scaled_redirects + clipped_impressions - overexposure_penalty
        if score < 2 and redirects > 0:
            score = 2
        if score < 1 and impressions > 0:
            score = 1
        return score


class Activity(Enum):
    IMPRESSION = 1
    REDIRECT = 2


if __name__ == "__main__":
  
    recommender = Recommender("dataset/activities.jsonl")
    recommender.calculate_implicit_score(5, 3)
    



