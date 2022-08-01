from recommender import Recommender

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    
class Users(BaseModel):
    user_ids: list[int]

class Job(BaseModel):
    job_id: int


recommender = Recommender("dataset/activities.jsonl")
recommender.build_sparse_matrix()
recommender.train_als_model()

app = FastAPI()

@app.post("/recommend/jobs_single_user/") 
def recommend_jobs_single_user(user: User):
    response = recommender.get_job_recommendations_for_single_user(user.user_id)
    single_user_job_recommendations = {"user_id": user.user_id, "jobs":response}
    return single_user_job_recommendations

@app.post("/recommend/jobs_multiple_users/") 
def recommend_jobs_bulk_users(users: Users):
    response = recommender.get_job_recommendations_for_bulk_users(users.user_ids)
    multi_user_job_recommendations = response
    return multi_user_job_recommendations

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)