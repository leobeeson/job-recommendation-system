from collections import defaultdict
from lxml.html import fromstring
from lxml.html.clean import Cleaner
from smart_open import open

import json
import re


class CorpusBuilder:

    cleaner: Cleaner  = Cleaner(style=True)
    pattern_control_chars: str = re.compile("\xa0|\xad")
    corpus: dict[str:list[str]] = None

    def __init__(self, jobs_filepath: str) -> None:
        self.jobs_filepath = jobs_filepath
        self.read_jobs_data()

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
        self.corpus = corpus
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


if __name__ == "__main__":
    corpus_filepath = "../dataset/jobs.jsonl"
    corpus_builder = CorpusBuilder(corpus_filepath)
    corpus_builder.corpus[list(corpus_builder.corpus.keys())[0]]
    corpus_builder.job_index[list(corpus_builder.job_index.keys())[1000]]
    corpus_builder.corpus["BMW Group"][10]
    test = 'Rolls Royce Motor Cars Graduate Schemes\n\nWe be\xadlieve in cre\xadating an envi\xadron\xadment where our placement student re\xadally can learn by do\xading dur\xading their time with us and where they are giv\xaden their own ar\xadeas of responsibilities from the start. That’s why our experts treat you as part of the team from day one, encour\xadage you to bring your own ideas to the table – and give you the opportunity to re\xadally show what you can do.\xa0\r\n\r\nAcross the UK, the BMW Group provide Apprenticeships, Industrial Placement Opportunities and Graduate Programmes to cater for a huge variety of interests and career paths.\r\n\r\nWith production operations in Oxford, Swindon, Hams Hall and Chichester, and head office functions like Marketing and Finance based at Farnborough, Oxford and Chichester there’s plenty to choose from.\r\n\r\nCurrent available roles include:\r\n\r\n\r\n\t\r\n\tBespoke Electrical Engineering\xa0\r\n\t\r\n\t\r\n\tClient Experience and Brand Marketing\xa0\r\n\t\r\n\t\r\n\tManufacturing Engineer\r\n\t\r\n\t\r\n\tSales Graduate\r\n\t\r\n\t\r\n\tOwnership Services\r\n\t\r\n\t\r\n\tProduct Management\xa0\r\n\t\r\n\r\n\r\nWhy choose us?\r\n\r\n\r\n\tGreat Pay\xa0– A competitive annual salary of £31,000, 26 days holiday (pro rata to your contract) and a pension scheme as well as a subsided on-site restaurant.\r\n\tRewarding Work-Life Balance\xa0– Contracted working hours are 40 hours a week, Monday - Friday helping you develop a fulfilling work-life balance.\r\n\tExciting Additional Benefits\xa0- Throughout your graduate scheme you will be supported by our experts and many fellow graduates, including an individually assigned mentor.\xa0The option to purchase or lease a BMW or MINI vehicle of your choice at a very special and reduced rate as part of your benefits package.\r\n'
    CorpusBuilder.remove_control_characters(test)
    test.find('\xa0')
    CorpusBuilder.remove_control_characters(test).find('\xad')

    
