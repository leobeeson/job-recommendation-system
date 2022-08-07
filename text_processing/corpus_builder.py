from smart_open import open
from collections import defaultdict
from lxml.html import fromstring
from lxml.html.clean import Cleaner

import json


corpus_filepath = "../dataset/jobs.jsonl"

cleaner = Cleaner(style=True)

def process_job(job: dict) -> str:
    title = job["title"]
    description = job["description"]
    description = remove_html_from_text(description)
    job_text = f"{title}\n\n{description}"
    return job_text
 

def remove_html_from_text(text: str) -> str:
    html_element = fromstring(text)
    html_cleaner = cleaner.clean_html(html_element)
    clean_text = html_cleaner.text_content()
    return clean_text


corpus = defaultdict(list)
for job in open(corpus_filepath):
    job = json.loads(job)
    employer = job["employer"]
    job_text = process_job(job)
    corpus[employer].append(job_text)


