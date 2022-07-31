

## Work Breakdown Structure

### Recommendations
* Map size of data: #DONE
    * Number of `user` records. #DONE
    * Number of `job` records. #DONE
    * Number of `activity` records. #DONE
* Count number of `activity` records per `user`-`job`. #DONE
    * i.e. number of times a user performed the same `activity` for an individual `job`. #DONE
    * Perhaps a `user` visited the same `job` more than once. #DONE
* Construct a `user`-`job` matrix. #FOCUS
* Weigh `user`-`job` matrix.
    * Set a cutoff for maximum number of `activity.redirect`.
* Create ALS model.
* Fit ALS model.

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


## Questions
* How many impressions per user per unit of time?
* How many redirects per user per unit of time?
* How frequently do users use Bright?
    * Do most users use it only once?
    * Do most users use it multiple times during a condensed period of time? (i.e. while job hunting)
    * Can users return to bright after a couple months/years of work experience?


## Future Ideas
* It would be interesting to have data on users that don't open an email (from Bright), and those who do open the email but don't click through to Bright's website.