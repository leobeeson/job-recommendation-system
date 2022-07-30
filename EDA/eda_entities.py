from collections import defaultdict
import json


jobs = {}
count_jobs = defaultdict(int)
with open("../dataset/jobs.jsonl") as input_file:
    for line in input_file:
        job = json.loads(line)
        job_id = job["job_id"]
        jobs[job_id] = job
        count_jobs[job_id] += 1
        
len(jobs) # 7,184
sum(list(count_jobs.values())) # 7,184


users = {}
count_users = defaultdict(int)
with open("../dataset/users.jsonl") as input_file:
    for line in input_file:
        user = json.loads(line)
        user_id = user["user_id"]
        users[user_id] = user
        count_users[user_id] += 1
        
len(users) # 95,600
sum(list(count_users.values())) # 95,600


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
        
len(count_jobs_impression) # 7,451
jobs_impression_frequency = set(val for val in count_jobs_impression.values()) # 1 - 1,842

len(count_jobs_redirect) # 4,290
jobs_redirect_frequency = set(val for val in count_jobs_redirect.values()) # 1 - 819

len(count_users_impression) # 16,416
users_impression_frequency = set(val for val in count_users_impression.values()) # 1 - 773, 3038

len(count_users_redirect) # 11,562
users_redirect_frequency = set(val for val in count_users_redirect.values()) # 1 - 279, 1,132

for k,v in activity_types.items():
    print(f"{k}: {v/sum(activity_types.values())}")
