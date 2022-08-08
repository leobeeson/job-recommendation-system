from collections import defaultdict
from collections import OrderedDict
import time
from tracemalloc import stop
from lxml.html import fromstring
from lxml.html.clean import Cleaner
from smart_open import open


from gensim.parsing.preprocessing import preprocess_string, strip_tags, strip_punctuation, strip_multiple_whitespaces, remove_stopwords, strip_short

import json
import re
from re import Pattern




class CorpusBuilder:

    
    cleaner: Cleaner  = Cleaner(style=True)
    pattern_control_chars: Pattern = re.compile("\xa0|\xad")
    pattern_undesirable_chars: Pattern = re.compile("‘|’|…|“|”")
    custom_filter = [lambda x: x.lower(), strip_tags, strip_punctuation, strip_multiple_whitespaces]
    

    corpus_raw: dict[str:list[str]] = None #TODO Convert to Dataclass
    corpus_tokenised: dict[str:list[list[str]]] = None #TODO Convert to Dataclass
    corpus_tokenised_flat: list[list[str]] = None #TODO Convert to Dataclass


    def __init__(self, jobs_filepath: str) -> None:
        self.jobs_filepath = jobs_filepath
        self.read_jobs_data()
        self.tokenise_text(self.corpus_raw)
        self.flatten_corpus(self.corpus_tokenised)


    def read_jobs_data(self) -> None:
        corpus = defaultdict(list)
        job_index = {}
        for job in open(corpus_filepath):
            job = json.loads(job)
            employer = job["employer"]
            job_text = self.process_job(job)
            corpus[employer].append(job_text)
            
            job_id = job["job_id"]
            job_title = job["title"]
            job_index_pos = len(corpus[employer]) - 1
            job_index[job_id] = {"employer": employer, "index": job_index_pos, "job_title": job_title}
        self.corpus_raw = corpus
        self.job_index = job_index


    @staticmethod
    def process_job(job: dict) -> str:
        title = job["title"]
        description = job["description"]
        description = CorpusBuilder.remove_html_from_text(description)
        description = CorpusBuilder.remove_control_characters(description)
        job_text = f"{title}\n\n{description}"
        return job_text


    @staticmethod
    def remove_html_from_text(text: str) -> str:
        html_element = fromstring(text)
        html_cleaner = CorpusBuilder.cleaner.clean_html(html_element)
        clean_text = html_cleaner.text_content()
        return clean_text


    @staticmethod
    def remove_control_characters(text: str) -> str:
        return re.sub(CorpusBuilder.pattern_control_chars, "", text)


    @staticmethod
    def remove_undesirable_chars(text: str) -> str:
        return re.sub(CorpusBuilder.pattern_undesirable_chars, " ", text)


    def tokenise_text(self, corpus_raw: dict[str:list[str]]) -> None:
        corpus_tokenised: dict[str:list[list[str]]] = defaultdict(list)
        for employer, job_descriptions in corpus_raw.items():
            for job_description in job_descriptions:
                job_preprocessed = self.remove_undesirable_chars(job_description)
                job_preprocessed = preprocess_string(job_preprocessed, CorpusBuilder.custom_filter)
                corpus_tokenised[employer].append(job_preprocessed)
        self.corpus_tokenised = corpus_tokenised


    def flatten_corpus(self, corpus_tokenised: dict[str:list[list[str]]]) -> None:
        corpus_tokenised_flat: list[list[str]] = []
        for _, job_descriptions in corpus_tokenised.items():
            for job_description in job_descriptions:
                corpus_tokenised_flat.append(job_description)
        self.corpus_tokenised_flat = corpus_tokenised_flat


if __name__ == "__main__":
    corpus_filepath = "../dataset/jobs.jsonl"
    corpus_builder = CorpusBuilder(corpus_filepath)
    
    corpus_builder.corpus_raw[list(corpus_builder.corpus_raw.keys())[0]]
    corpus_builder.job_index[list(corpus_builder.job_index.keys())[1000]]
    corpus_builder.corpus_raw["BMW Group"][10]
    corpus_builder.corpus_tokenised["BMW Group"][10]
    len(corpus_builder.corpus_tokenised) # 894
    
    type(corpus_builder.corpus_tokenised_flat)
    len(corpus_builder.corpus_tokenised_flat) # 7,184 == total jobs in jobs.jsonl
