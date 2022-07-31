from collections import defaultdict
import json
import pandas


# Count jobs and verify no duplication of ids:
jobs = {}
count_jobs = defaultdict(int)
with open("../dataset/jobs.jsonl") as input_file:
    for line in input_file:
        job = json.loads(line)
        job_id = job["job_id"]
        jobs[job_id] = job
        count_jobs[job_id] += 1
        
total_jobs = len(jobs) # 7,184
sum(list(count_jobs.values())) # 7,184


# Count users and verify no duplication of ids:
users = {}
count_users = defaultdict(int)
with open("../dataset/users.jsonl") as input_file:
    for line in input_file:
        user = json.loads(line)
        user_id = user["user_id"]
        users[user_id] = user
        count_users[user_id] += 1
        
total_users = len(users) # 95,600
sum(list(count_users.values())) # 95,600


# Count impressions by type and get frequency distribution:
count_jobs_impression = defaultdict(int)
count_jobs_redirect = defaultdict(int)
count_users_impression = defaultdict(int)
count_users_redirect = defaultdict(int)
activity_types = defaultdict(int)
with open("../dataset/activities.jsonl") as input_file:
    for line in input_file:
        activity = json.loads(line)
        type_ = activity["type"]
        activity_types[type_] += 1
        if type_ == "impression":
            count_jobs_impression[activity["job_id"]] += 1
            count_users_impression[activity["user_id"]] += 1
        elif type_ == "redirect":
            count_jobs_redirect[activity["job_id"]] += 1
            count_users_redirect[activity["user_id"]] += 1
        else:
            print(f"Unexpected Activity:\n{activity}")
        

total_activity_records = sum(activity_types.values()) # 382,815
total_impression_records = activity_types["impression"] # 301,517
total_redirect_records = activity_types["redirect"] # 81,298

# Frequency of activity per activity type:
len(count_jobs_impression) # 7,451
jobs_impression_frequency = set(val for val in count_jobs_impression.values()) # 1 - 1,842

len(count_jobs_redirect) # 4,290
jobs_redirect_frequency = set(val for val in count_jobs_redirect.values()) # 1 - 819

len(count_users_impression) # 16,416
users_impression_frequency = set(val for val in count_users_impression.values()) # 1 - 773, 3038

len(count_users_redirect) # 11,562
users_redirect_frequency = set(val for val in count_users_redirect.values()) # 1 - 279, 1,132

# Activity types %:
for k,v in activity_types.items():
    print(f"{k}: {v/sum(activity_types.values())}")
# impression: 0.7876
# redirect: 0.2124


# Upper bound statistics of user-job interactions:
activities_df = pandas.read_json("../dataset/activities.jsonl", lines=True)
len(activities_df) == total_activity_records
user_job_total_cooccurrences = pandas.crosstab(activities_df.user_id, activities_df.job_id)
user_job_total_max_interactions = user_job_total_cooccurrences.max() 
user_job_total_max_interactions_mean = user_job_total_max_interactions.mean() # 4.32
user_job_total_max_interactions_p50 = user_job_total_max_interactions.quantile(q=0.5) # 3
user_job_total_max_interactions_p95 = user_job_total_max_interactions.quantile(q=0.95) # 12
user_job_total_max_interactions_p99 = user_job_total_max_interactions.quantile(q=0.99) # 24
user_job_total_max_interactions_max = user_job_total_max_interactions.max() # 182

impressions_df = activities_df[activities_df["type"] == "impression"]
len(impressions_df) == total_impression_records
user_job_impressions_cooccurrences = pandas.crosstab(impressions_df.user_id, impressions_df.job_id)
user_job_impressions_max_interactions = user_job_impressions_cooccurrences.max() 
user_job_impressions_max_interactions_mean = user_job_impressions_max_interactions.mean() # 3.54
user_job_impressions_max_interactions_p50 = user_job_impressions_max_interactions.quantile(q=0.5) # 2
user_job_impressions_max_interactions_p95 = user_job_impressions_max_interactions.quantile(q=0.95) # 10
user_job_impressions_max_interactions_p99 = user_job_impressions_max_interactions.quantile(q=0.99) # 20
user_job_impressions_max_interactions_max = user_job_impressions_max_interactions.max() # 181

redirects_df = activities_df[activities_df["type"] == "redirect"]
len(redirects_df) == total_redirect_records
user_job_redirects_cooccurrences = pandas.crosstab(redirects_df.user_id, redirects_df.job_id)
user_job_redirects_max_interactions = user_job_redirects_cooccurrences.max() 
user_job_redirects_max_interactions_mean = user_job_redirects_max_interactions.mean() # 2.26
user_job_redirects_max_interactions_p50 = user_job_redirects_max_interactions.quantile(q=0.5) # 2
user_job_redirects_max_interactions_p95 = user_job_redirects_max_interactions.quantile(q=0.95) # 5
user_job_redirects_max_interactions_p99 = user_job_redirects_max_interactions.quantile(q=0.99) # 8
user_job_redirects_max_interactions_max = user_job_redirects_max_interactions.max() # 31
