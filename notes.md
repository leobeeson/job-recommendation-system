

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
* Refactor code into `Recommender` class: #FOCUS
    * read_activity_data() #DONE
    * calculate_implicit_score() #DONE
    * add_implicit_scores() #DONE 
    * generate_user_job_triples() #DONE
    * get_unique_engaged_users() #DONE
    * get_unique_engaged_jobs() #DONE
    * build_sparse_matrix()
    * train_als_model()
    * get_recommendations_single()
    * get_recommendations_bulk()
* Build http endpoints:
    * recommender/retrain_model
    * recommender/recommend
    * recommender/recommend_bulk

### Employer Clustering
* Build lists of `job.description` per `job.employer`.
* Build corpus from lists of `job.description`.
* Train MWE model on corpus.
* Identify valuable MWE.
* Identify valuable unigrams.
* Reduce corpus vocabulary to selected unigrams and MWE.

#### K-Means Clustering: Types of Employers
* sklearn.cluster.KMeans

#### Employer Similarities
* gensim.models.doc2vec


## Out of Scope / Future Work

### General
* Apply code formatting guidelines/framework.

### Recommender
* Move reading activity data into its own DTO class `ActivityDTO`.
    * Will reduce coupling of `Recommender` class.
    * `Recommender` class consumes and `ActivityDTO`.
    * Will make testing `Recommender` easier by mocking `ActivityDTO` with a small fixture.
* Create bespoke class for list of user_job_triples used to create scored matrix for recommendation model.
* To avoid iterating twice over all `user_id` and `job_id` keys, `generate_user_job_triples` and `add_implicit_scores` can be refactored into single method if `activities` data becomes significantly large. It'll create come coupling between scoring and generating the scored data, but shouldn't cause much overhead or complexity.


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

### Scaling
* `max(impression) == 10`
* `max(redirect) == 10`
* `scaled_redirect == redirect * 2`
* `implicit_score == scaled_redirect + impression - (impression - redirect)`
* `min(implicit_score) == 2 where redirect > 0`
* `min(implicit_score) == 1 where redirect == 0 & impression > 0`


## Data Models

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

## Questions
* How many impressions per user per unit of time?
* How many redirects per user per unit of time?
* How frequently do users use Bright?
    * Do most users use it only once?
    * Do most users use it multiple times during a condensed period of time? (i.e. while job hunting)
    * Can users return to bright after a couple months/years of work experience?

## Research
* Why is AlternatingLeastSquares recommended for implicit feedback?


## Future Ideas
* It would be interesting to have data on users that don't open an email (from Bright), and those who do open the email but don't click through to Bright's website.