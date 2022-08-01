from utils.utils import nested_default_dict

from enum import Enum

import json
import numpy
import pandas
import scipy


class Recommender:

    user_id_key: str = "user_id"
    job_id_key: str = "job_id"
    activity_type_key:str = "type"
    implicit_score_key: str = "implicit_score"
    
    def __init__(self, activities_filepath) -> None:
        self.activities_filepath = activities_filepath
        self.activities = nested_default_dict()
        self.read_activity_data()
        self.add_implicit_scores()
        self.generate_user_job_triples()
        self.get_unique_entities()

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

    def add_implicit_scores(self) -> None:
        for user_id in self.activities.keys():
            for job_id in self.activities[user_id].keys():
                impression = self.activities[user_id][job_id].get(Activity.IMPRESSION.name.lower())
                redirect = self.activities[user_id][job_id].get(Activity.REDIRECT.name.lower())
                implicit_score = Recommender.calculate_implicit_score(impression, redirect)
                self.activities[user_id][job_id][self.implicit_score_key] = implicit_score

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

    def generate_user_job_triples(self) -> None:
        user_job_implicit_scores = []
        for user_id in self.activities.keys():
            for job_id in self.activities[user_id].keys():
                implicit_score = self.activities[user_id][job_id].get(self.implicit_score_key)
                if implicit_score:
                    user_job_triple = Recommender.generate_user_job_triple(user_id, job_id, implicit_score)
                    user_job_implicit_scores.append(user_job_triple)
        self.user_job_implicit_scores = user_job_implicit_scores

    @classmethod
    def generate_user_job_triple(cls, user_id, job_id, implicit_score) -> dict:
        user_job_triple = {
                            cls.user_id_key: user_id, 
                            cls.job_id_key: job_id, 
                            cls.implicit_score_key: implicit_score
                        }
        return user_job_triple

    def get_unique_entities(self) -> None:
        unique_user_ids = set()
        unique_job_ids = set()
        for triple in self.user_job_implicit_scores:
            unique_user_ids.add(triple[self.user_id_key])
            unique_job_ids.add(triple[self.job_id_key])
        unique_user_ids = list(unique_user_ids)
        unique_user_ids.sort()
        unique_job_ids = list(unique_job_ids)
        unique_job_ids.sort()
        entity_indices = {"unique_users": unique_user_ids, "unique_jobs": unique_job_ids}
        self.entity_indices = entity_indices

    def build_sparse_matrix(self) -> None:
        zeroes_data = numpy.zeros((
            len(self.entity_indices["unique_users"]), 
            len(self.entity_indices["unique_jobs"])
            ))
        user_job_implicit_scores_df = pandas.DataFrame(
            zeroes_data, 
            index=self.entity_indices["unique_users"], 
            columns=self.entity_indices["unique_jobs"], 
            dtype=int
            )
        for user_job_score in self.user_job_implicit_scores:
            user_id = user_job_score[Recommender.user_id_key]
            job_id = user_job_score[Recommender.job_id_key]
            implicit_score = user_job_score[Recommender.implicit_score_key]
            user_job_implicit_scores_df.loc[user_id, job_id] = implicit_score

        self.matrix_row_user_index = user_job_implicit_scores_df.index
        self.matrix_column_job_index = user_job_implicit_scores_df.columns
        matrix_implicit_scores = user_job_implicit_scores_df.to_numpy()
        self.matrix_csr = scipy.sparse.csr_matrix(matrix_implicit_scores)


class Activity(Enum):
    IMPRESSION = 1
    REDIRECT = 2


if __name__ == "__main__":
    recommender = Recommender("dataset/activities.jsonl")
    
    recommender.calculate_implicit_score(5, 3)
    
    recommender.activities[65794][20116].get(Recommender.implicit_score_key) # 1
    
    recommender.user_job_implicit_scores[0]

    recommender.entity_indices["unique_users"][0:10]
    recommender.entity_indices["unique_jobs"][0:10]

    recommender.build_sparse_matrix()
    recommender.matrix_csr.shape
    

    
    



