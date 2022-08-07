## Assumptions

### Funnel
* A good funnel is: `(a impression -> a redirect) * n`
    * User checked out the same job at the employer multiple times, always starting from Bright.
    * The larger `n`, probably the more relevant the job for the user (strong assumption).
    * If `n == 1`, maybe the user did not like the job after looking at it in from the employer's site (weak assumption).
* An efficient funnel is: `(a impression -> b redirect) * n` where a < b
    * User might have bookmarked employers job page.
* An inefficient funnel is: `(a impression -> b redirect) * n` where a > b
    * User might have missed the impression several times.
    * User was not initially attracted to the job (last resort).
    * User applied to the job, but impressions kept being shown to him/her in subsequent searches.
* A bad funnel is: `(1 impression -> 0 redirect) * n`
    * User is not finding anything attractive.
    * User is being engaged at the wrong moment (e.g. doesn't have time to redirect and dive deeper).
* A strange funnel is: `(0 impression -> 1 redirect) * n`
    * 813 users redirected to a specific job without having a tracked impression.
    * 22 jobs had redirections without having tracked impressions.

### Scaling Implicit Feedback
* `max(impression) == 10`
* `max(redirect) == 10`
* `scaled_redirect = redirect * 2`
* `overexposure_penalty = impressions - redirects` where `0 < impressions - redirects`
* `implicit_score = scaled_redirect + impression - (impression - redirect)`
* `min(implicit_score) == 2` where `redirect > 0`
* `min(implicit_score) == 1` where `redirect == 0 & impression > 0`

## Data Model for Scored Activities Data
```python
{
    user_id:int: {
        job_id:int {
            impression:str : count:int,
            redirect:str: count:int,
            implicit_score:int score:func(redirect*2 impression - (impression - redirect))
        }
    }
}
```

## Work Breakdown Structure

### Recommendations
* Map size of data: #DONE
    * Number of `user` records. #DONE
    * Number of `job` records. #DONE
    * Number of `activity` records. #DONE
* Count number of `activity` records per `user`-`job`. #DONE
    * i.e. number of times a user performed the same `activity` for an individual `job`. #DONE
    * Perhaps a `user` visited the same `job` more than once. #DONE
* Construct a `user`-`job` matrix. #DONE
* Weigh `user`-`job` matrix. #DONE
    * Set a cutoff for maximum number of `activity.redirect`. #DONE
* Create ALS model. #DONE
* Fit ALS model. #DONE
* Refactor code into `Recommender` class: #DONE
    * read_activity_data() #DONE
    * calculate_implicit_score() #DONE
    * add_implicit_scores() #DONE 
    * generate_user_job_triples() #DONE
    * get_unique_engaged_users() #DONE
    * get_unique_engaged_jobs() #DONE
    * build_sparse_matrix() #DONE
    * train_als_model() #DONE
    * get_job_recommendations_for_single_user() #DONE
    * get_job_recommendations_for_bulk_users() #DONE
    * find_similar_jobs() #DONE
* Build http endpoints: #DONE
    * recommender/jobs_single_user #DONE
    * recommender/jobs_multiple_users #DONE
    * recommender/find_similar_jobs #DONE
* Generate requirements.txt #DONE

### Employer Clustering
* Build lists of `job.description` per `job.employer`. #DONE
    * Lazy reading of `jobs` data. #DONE
    * Remove html tags and escaped characters from `job.description`. #DONE
    * Build `dict` of type `{job.employer: [job.description]}` #DONE
* Build corpus from lists of `job.description`. #TODO
    * Remove specific punctuation (new lines, carriage return, etc.)
    * Convert to lower case. 
    * Remove stopwords.
    * Tokenise.
* Train MWE model on corpus. #TODO
* Identify valuable MWE. #TODO
* Identify valuable unigrams. #TODO
* Reduce corpus vocabulary to selected unigrams and MWE. #TODO

#### K-Means Clustering: Types of Employers
* sklearn.cluster.KMeans #TODO

#### Employer Similarities
* gensim.models.doc2vec #TODO


## Out of Scope / Future Work

### General
* Apply code formatting guidelines/framework.

### Recommender
* Move reading activity data into its own DTO class `ActivityDTO`.
    * Will reduce coupling of `Recommender` class.
    * `Recommender` class consumes and `ActivityDTO`.
    * Will make testing `Recommender` easier by mocking `ActivityDTO` with a small fixture.
* To avoid iterating twice over all `user_id` and `job_id` keys, `generate_user_job_triples` and `add_implicit_scores` can be refactored into single method if `activities` data becomes significantly large. It'll create come coupling between scoring and generating the scored data, but shouldn't cause much overhead or complexity.
* For further efficiencies and code performance, `get_unique_entities` can also be refactored into `generate_user_job_triples` and `add_implicit_scores`. However, this single method would now be having many "side effects".
* Filter job recommendations that are old or no longer available.
* Apply a moving window to activities' data used to train the recommender model, so as to adapt to a user's changing job preferences or expectations across time. 
* Add `users.jsonl` and `activities.jsonl` data to a NoSQL database to retrieve user demographics and job descriptions for enhancing recommendations metadata.
* Create bespoke exceptions and handle incorrect arguments passed to endpoints.
* Create bespoke class for list of user_job_triples used to create scored matrix for recommendation model.
* Create bespoke class for single user recommendations response object.
* Create bespoke class for batch user recommendations response object.
* Create endpoint for retraining recommender model with new/larger data: `recommender/retrain_model`. 

### Text Processing



## Future Ideas

### Enhanced Input Data
* Incorporate data that flags when a user has applied to a job after being redirected to an employer's page, so we can recommend only jobs to which he/she hasn't applied to.
* It would be interesting to have data on users that don't open an email (from Bright), and those who do open the email but don't click through to Bright's website.

### Questions
* How many impressions per user per unit of time?
* How many redirects per user per unit of time?
* How frequently do users use Bright?
    * Do most users use it only once?
    * Do most users use it multiple times during a condensed period of time? (i.e. while job hunting)
    * Can users return to bright after a couple months/years of work experience?

### Research
* Why is AlternatingLeastSquares recommended for implicit feedback?
    * Good initial [source](https://towardsdatascience.com/prototyping-a-recommender-system-step-by-step-part-2-alternating-least-square-als-matrix-4a76c58714a1).
* What other models are also recommended for implicit feedback recommender systems?

## Commands
Start the application:
```bash
uvicorn main:app --reload
```

Request job recommendations for a single user:
```bash
curl -X POST http://127.0.0.1:8000/recommend/jobs_single_user/ -H "Content-Type: application/json" -d '{"user_id": 99955}'
```
Response:
```json
{
    "user_id":99955,
    "jobs":[
        {"job_id":28391,"score":0.6198304891586304},
        {"job_id":16818,"score":0.5988735556602478},
        {"job_id":14709,"score":0.5657774806022644},
        {"job_id":16723,"score":0.4660928547382355},
        {"job_id":23274,"score":0.3648761510848999},
        {"job_id":20517,"score":0.3629113435745239},
        {"job_id":26481,"score":0.3579047620296478},
        {"job_id":20105,"score":0.35438770055770874},
        {"job_id":28504,"score":0.3502712845802307},
        {"job_id":14386,"score":0.34550684690475464}
    ]
}
```

Request job recommendations for a multiple users:
```bash
curl -X POST http://127.0.0.1:8000/recommend/jobs_multiple_users/ -H "Content-Type: application/json" -d '{"user_ids": [99955, 65794, 31004]}'
```
Response:
```json
{
    "99955":[
        {"job_id":28391,"score":0.6198304891586304},
        {"job_id":16818,"score":0.598873496055603},
        {"job_id":14709,"score":0.5657775402069092},
        {"job_id":16723,"score":0.46609288454055786},
        {"job_id":23274,"score":0.36487603187561035},
        {"job_id":20517,"score":0.3629113435745239},
        {"job_id":26481,"score":0.3579047620296478},
        {"job_id":20105,"score":0.35438767075538635},
        {"job_id":28504,"score":0.35027122497558594},
        {"job_id":14386,"score":0.34550684690475464}
    ],
    "65794":[
        {"job_id":3950,"score":1.3044391870498657},
        {"job_id":15219,"score":1.196151614189148},
        {"job_id":16588,"score":1.0560941696166992},
        {"job_id":15062,"score":0.8263643980026245},
        {"job_id":15675,"score":0.818429172039032},
        {"job_id":8078,"score":0.814281702041626},
        {"job_id":14829,"score":0.8116833567619324},
        {"job_id":15218,"score":0.7878887057304382},
        {"job_id":20116,"score":0.7703413963317871},
        {"job_id":14710,"score":0.7347549200057983}
    ],
    "31004":[
        {"job_id":15030,"score":1.0643808841705322},
        {"job_id":14712,"score":0.7925517559051514},
        {"job_id":12969,"score":0.7763451337814331},
        {"job_id":12057,"score":0.7574162483215332},
        {"job_id":13576,"score":0.6788557171821594},
        {"job_id":12068,"score":0.6747690439224243},
        {"job_id":14191,"score":0.6514241099357605},
        {"job_id":15045,"score":0.6504997611045837},
        {"job_id":13721,"score":0.6069185137748718},
        {"job_id":16772,"score":0.5923895239830017}
    ]
}
```

Request similar jobs recommendations from a single job:
```bash
curl -X POST http://127.0.0.1:8000/recommend/find_similar_jobs/ -H "Content-Type: application/json" -d '{"job_id": 23274}'
```
Response:
```json
{
    "job_id":23274,
    "jobs":[
        {"job_id":23274,"score":1.0},
        {"job_id":22294,"score":0.9260625243186951},
        {"job_id":16813,"score":0.9248543381690979},
        {"job_id":26946,"score":0.9047039151191711},
        {"job_id":23896,"score":0.9032652378082275},
        {"job_id":23739,"score":0.8922211527824402},
        {"job_id":28587,"score":0.8813559412956238},
        {"job_id":28599,"score":0.8813554048538208},
        {"job_id":28596,"score":0.8813521862030029},
        {"job_id":28595,"score":0.8813501596450806}
    ]
}
```


<style>
todo { background-color: Yellow; color: SteelBlue }
recurrent { background-color: Gold; color: SteelBlue }
refactor { background-color: SpringGreen; color: DarkGreen }
done { background-color: Green; color: PaleGreen }
test { background-color: Coral; color: DarkRed }
fixme { background-color: Crimson; color: white }
focus { background-color: DeepSkyBlue; color: MediumBlue }
reqspec { background-color: MediumPurple; color: Indigo }
doubt { background-color: #FF00FF; color: Yellow }
wait { background-color: Pink; color: Crimson }
blocked { background-color: Crimson; color: Yellow }
</style>