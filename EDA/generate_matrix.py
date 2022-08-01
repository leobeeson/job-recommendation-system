from collections import defaultdict
import json
import time
import pandas
import numpy
import gc
import scipy
from implicit.als import AlternatingLeastSquares

def nested_default_dict():
    return defaultdict(nested_default_dict)

activities = nested_default_dict()
t0 = time.time()
with open("dataset/activities.jsonl") as input_file:
    for line in input_file:
        activity = json.loads(line)
        user_id = activity["user_id"]
        job_id = activity["job_id"]
        type_ = activity["type"]
        try:
            activities[user_id][job_id][type_] = activities[user_id][job_id][type_] + 1
        except TypeError:
            activities[user_id][job_id][type_] = 1
t1 = time.time()
t1 - t0 # 1.9 secs

def calculate_implicit_score(impressions: int, redirects: int) -> int:
    impressions = impressions if impressions is not None else 0
    redirects = redirects if redirects is not None else 0
    clipped_impressions = 10 if impressions > 10 else impressions
    clipped_redirects = 10 if redirects > 10 else redirects
    scaled_redirects = clipped_redirects * 2
    overexposure_penalty = clipped_impressions - clipped_redirects
    score = scaled_redirects + clipped_impressions - overexposure_penalty
    if score < 2 and redirects > 0:
        score = 2
    if score < 1 and impressions > 0:
        score = 1
    return score

t0 = time.time()
for user_id in activities.keys():
    for job_id in activities[user_id].keys():
        impression = activities[user_id][job_id].get("impression")
        redirect = activities[user_id][job_id].get("redirect")
        implicit_score = calculate_implicit_score(impression, redirect)
        activities[user_id][job_id]["implicit_score"] = implicit_score
t1 = time.time()
t1 - t0 # 0.22 secs


user_job_implicit_scores = []
t0 = time.time()
for user_id in activities.keys():
    for job_id in activities[user_id].keys():
        implicit_score = activities[user_id][job_id].get("implicit_score")
        if implicit_score:
            user_job_dict = {"user_id": user_id, "job_id": job_id, "implicit_score": implicit_score}
            user_job_implicit_scores.append(user_job_dict)
t1 = time.time()
t1 - t0 # 0.13 secs
len(user_job_implicit_scores)




activities_df = pandas.read_json("dataset/activities.jsonl", lines=True)
impressions_df = activities_df[activities_df["type"] == "impression"]
redirects_df = activities_df[activities_df["type"] == "redirect"]
del activities_df
gc.collect()

users_impressions = impressions_df["user_id"].unique()
jobs_impressions = impressions_df["job_id"].unique()
users_redirects = redirects_df["user_id"].unique()
jobs_redirects = redirects_df["job_id"].unique()
total_users_engaged = list(set(list(users_impressions) + list(users_redirects)))
total_users_engaged.sort()
total_jobs_engaged = list(set(list(jobs_impressions) + list(jobs_redirects)))
total_jobs_engaged.sort()

zeroes_data = numpy.zeros((len(total_users_engaged), len(total_jobs_engaged)))
user_job_implicit_scores_df = pandas.DataFrame(zeroes_data, index=total_users_engaged, columns=total_jobs_engaged, dtype=int)

t0 = time.time()
for user_job_score in user_job_implicit_scores:
    user_id = user_job_score["user_id"]
    job_id = user_job_score["job_id"]
    implicit_score = user_job_score["implicit_score"]
    user_job_implicit_scores_df.loc[user_id, job_id] = implicit_score
t1 = time.time()
t1 - t0 # 8.30 secs

user_ids = user_job_implicit_scores_df.index
job_id = user_job_implicit_scores_df.columns
user_job_implicit_scores = user_job_implicit_scores_df.to_numpy()
len(user_job_implicit_scores)

activities_sparce = scipy.sparse.csr_matrix(user_job_implicit_scores)
activities_sparce.shape

model = AlternatingLeastSquares(factors=64, regularization=0.05)
t0 = time.time()
model.fit(2 * activities_sparce)
t1 = time.time()
print(t1 - t0) # 6.36 secs

# Get recommendations for the a single user
user_id = 99955
user_idx = user_ids.get_loc(99955)
ids, scores = model.recommend(
    user_idx, 
    activities_sparce[user_idx], 
    N=10, 
    filter_already_liked_items=False
    )


