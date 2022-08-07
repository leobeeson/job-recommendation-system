from collections import defaultdict
from lxml.html import fromstring
from lxml.html.clean import Cleaner
from smart_open import open

import json


class CorpusBuilder:

    cleaner: Cleaner  = Cleaner(style=True)
    corpus: dict[str:list[str]] = None

    def __init__(self, jobs_filepath: str) -> None:
        self.jobs_filepath = jobs_filepath
        self.read_jobs_data()

    def read_jobs_data(self) -> None:
        corpus = defaultdict(list)
        for job in open(corpus_filepath):
            job = json.loads(job)
            employer = job["employer"]
            job_text = self.process_job(job)
            corpus[employer].append(job_text)
        self.corpus = corpus
    
    @staticmethod
    def process_job(job: dict) -> str:
        title = job["title"]
        description = job["description"]
        description = CorpusBuilder.remove_html_from_text(description)
        job_text = f"{title}\n\n{description}"
        return job_text

    @staticmethod
    def remove_html_from_text(text: str) -> str:
        html_element = fromstring(text)
        html_cleaner = CorpusBuilder.cleaner.clean_html(html_element)
        clean_text = html_cleaner.text_content()
        return clean_text


if __name__ == "__main__":
    corpus_filepath = "../dataset/jobs.jsonl"
    corpus_builder = CorpusBuilder(corpus_filepath)
    corpus_builder.corpus[list(corpus_builder.corpus.keys())[0]]

