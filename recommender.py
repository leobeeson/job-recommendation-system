from utils.utils import nested_default_dict

from enum import Enum

import json
import time
import numpy
import pandas
import scipy
from implicit.als import AlternatingLeastSquares


class Recommender:

    user_id_key: str = "user_id"
    job_id_key: str = "job_id"
    activity_type_key:str = "type"
    implicit_score_key: str = "implicit_score"
    recommendation_score_key: str = "score"
    
    def __init__(self, activities_filepath: str) -> None:
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
    def generate_user_job_triple(cls, user_id: int, job_id: int, implicit_score: int) -> dict:
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

    def train_als_model(self) -> None:
        als_model = AlternatingLeastSquares(factors=64, regularization=0.05)
        print("Start recommender model training. Should take ~ 15 seconds.")
        t0 = time.time()
        als_model.fit(2 * self.matrix_csr)
        t1 = time.time()
        print(f"Model training duration (seconds): {t1 - t0}") 
        self.als_model = als_model

    def get_job_recommendations_for_single_user(self, user_id: int, number_of_recommendations: int = 10) -> list[dict]:
        response = []
        if isinstance(user_id, int) and user_id in self.entity_indices["unique_users"]:
            user_matrix_row_idx = self.matrix_row_user_index.get_loc(user_id)
            ids, scores = self.als_model.recommend(
                user_matrix_row_idx, 
                self.matrix_csr[user_matrix_row_idx], 
                N=number_of_recommendations, 
                filter_already_liked_items=False
            )
            for job_idx, score in zip(ids, scores):
                recommendation = {
                    Recommender.job_id_key: self.matrix_column_job_index[job_idx].item(),
                    Recommender.recommendation_score_key: score.item() 
                    }
                response.append(recommendation)
        return response

    def get_job_recommendations_for_bulk_users(self, user_ids: list[int], number_of_recommendations: int = 10) -> dict:
        response = {}
        if isinstance(user_ids, list) and all(isinstance(x, int) for x in user_ids):
            user_ids_verified = [user_id for user_id in user_ids if user_id in self.entity_indices["unique_users"]]
            user_matrix_row_idx = [self.matrix_row_user_index.get_loc(user_id) for user_id in user_ids_verified]
            ids, scores = self.als_model.recommend(
                user_matrix_row_idx, 
                self.matrix_csr[user_matrix_row_idx], 
                N=number_of_recommendations, 
                filter_already_liked_items=False
            )
            
            for user_id, job_ids, scores in zip(user_ids_verified, ids, scores):
                user_response = []
                for job_idx, score in zip(job_ids, scores):
                    recommendation = {
                        Recommender.job_id_key: self.matrix_column_job_index[job_idx].item(),
                        Recommender.recommendation_score_key: score.item() 
                        }
                    user_response.append(recommendation)    
                response[user_id] = user_response
        return response

    def find_similar_jobs(self, job_id: int) -> list[dict]:
        response = []
        if isinstance(job_id, int) and job_id in self.entity_indices["unique_jobs"]:
            job_idx = self.matrix_column_job_index.get_loc(job_id)
            similar_jobs_idx, scores = self.als_model.similar_items(job_idx)
            for job_idx, score in zip(similar_jobs_idx, scores):
                recommendation = {
                    Recommender.job_id_key: self.matrix_column_job_index[job_idx].item(),
                    Recommender.recommendation_score_key: score.item()
                    }
                response.append(recommendation)
        return response


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
    recommender.train_als_model()
    response = recommender.get_job_recommendations_for_single_user(99955)
    response = recommender.get_job_recommendations_for_bulk_users([99955, 65794, 31004]) 
    response = recommender.find_similar_jobs(23274)

    