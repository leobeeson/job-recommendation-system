from stopwords import stopwords_english

from gensim.models.phrases import Phrases, FrozenPhrases, ENGLISH_CONNECTOR_WORDS

from collections import OrderedDict


class MultiWordExpressionExtractor:

    stopwords: list[str]  = stopwords_english["stopwords"]
    connector_words: list[str] = ENGLISH_CONNECTOR_WORDS

    corpus: list[list[str]] = None
    phrases_model: Phrases = None


    def __init__(self, corpus: list[list[str]]) -> None:
        self.corpus = corpus


    def extract_mwe(self, min_count: int=10) -> Phrases:
        phrases_model = Phrases(
            sentences=self.corpus,
            min_count=min_count,
            threshold=0,
            scoring="npmi",
            connector_words=MultiWordExpressionExtractor.connector_words)
        self.phrases_model = phrases_model


    def export_mwe(self) -> dict:
        mwe_export = self.phrases_model.export_phrases()
        mwe_export_sorted = MultiWordExpressionExtractor.sort_mwe_export(mwe_export)
        return mwe_export_sorted


    def identify_mwe_with_leading_and_trailing_stopwords(self, mwe_export: dict) -> list[str]:
        mwe_blacklist = []
        for mwe in mwe_export.keys():
            terms = mwe.split("_")
            # if len(terms) > 2:
            if terms[0] in self.stopwords or terms[-1] in self.stopwords:
                mwe_blacklist.append(mwe)
        return mwe_blacklist


    def remove_blacklisted_mwe(self, mwe_blacklist: list[str]) -> None:
        if len(mwe_blacklist) > 0:
            for mwe in mwe_blacklist:
                try:
                    del self.phrases_model.vocab[mwe]
                except KeyError:
                    pass


    def tokenise_mwe(self) -> None:
        corpus_mwe: list[list[str]] = []
        for doc in self.corpus:
            doc_mwe = self.phrases_model[doc]
            corpus_mwe.append(doc_mwe)
        self.corpus = corpus_mwe  

    
    @staticmethod
    def sort_mwe_export(mwe_export: dict, reversed: bool = True) -> dict:
        mwe_sorted = OrderedDict(
            sorted(
                mwe_export.items(), key=lambda kv: kv[1], reverse=reversed
                )
            )
        return mwe_sorted


if __name__ == "__main__":
    from corpus_builder import CorpusBuilder
    corpus_filepath = "../dataset/jobs.jsonl"
    corpus_builder = CorpusBuilder(corpus_filepath)
    
    mwe_extractor = MultiWordExpressionExtractor(corpus_builder.corpus_tokenised_flat)
    # mwe_extractor.corpus[0][:20]

    mwe_extractor.extract_mwe()
    # mwe_extractor.phrases_model.vocab
    len(mwe_extractor.phrases_model.vocab) # 669,188
    len([mwe for mwe in mwe_extractor.phrases_model.vocab if "_" in mwe]) # 637,177

    mwe_export = mwe_extractor.export_mwe()
    len(mwe_export) # 50,163
    mwe_blacklist = mwe_extractor.identify_mwe_with_leading_and_trailing_stopwords(mwe_export)
    len(mwe_blacklist) # 15,249
    
    mwe_extractor.remove_blacklisted_mwe(mwe_blacklist)
    mwe_export = mwe_extractor.export_mwe()
    len(mwe_export) # 34,914
    len([mwe for mwe in mwe_extractor.phrases_model.vocab if "_" in mwe]) # 621,928
    

    len([mwe for doc in mwe_extractor.corpus for mwe in doc if "_" in mwe]) # 0
    mwe_extractor.tokenise_mwe()
    len([mwe for doc in mwe_extractor.corpus for mwe in doc if "_" in mwe]) # 776,653
    len([mwe for doc in mwe_extractor.corpus for mwe in doc if "role_and_you" in mwe]) # 0
    len([mwe for doc in mwe_extractor.corpus for mwe in doc if "deloitte_nse" in mwe]) # 29
    len([mwe for doc in mwe_extractor.corpus for mwe in doc if "bring_to_wsp_we" in mwe]) # 0
    len([mwe for doc in mwe_extractor.corpus for mwe in doc if "bring_to_wsp" in mwe]) # 12
    mwe_extractor.corpus[10]

    ### SECOND ROUND ###
    mwe_extractor.extract_mwe()
    len(mwe_extractor.phrases_model.vocab) # 841,443
    len([mwe for mwe in mwe_extractor.phrases_model.vocab if "_" in mwe]) # 809,889
    mwe_export = mwe_extractor.export_mwe()
    len(mwe_export) # 55,853
    'bring_to_wsp_we' in mwe_export.keys() # False

    mwe_blacklist = mwe_extractor.identify_mwe_with_leading_and_trailing_stopwords(mwe_export)
    len(mwe_blacklist) # 19,479

    'bring_to_wsp_we' in mwe_export.keys() # False
    'bring_to_wsp_we' in mwe_blacklist # False

    mwe_extractor.remove_blacklisted_mwe(mwe_blacklist)
    len(mwe_extractor.phrases_model.vocab) # 821,964
    len([mwe for mwe in mwe_extractor.phrases_model.vocab if "_" in mwe]) # 790,410
    mwe_export = mwe_extractor.export_mwe()
    len(mwe_export) # 36,152
    'bring_to_wsp_we' in mwe_export.keys() # False

    mwe_extractor.tokenise_mwe()
    len([mwe for doc in mwe_extractor.corpus for mwe in doc if "_" in mwe]) # 652045
    len([mwe for doc in mwe_extractor.corpus for mwe in doc if "bring_to_wsp_we" in mwe]) # 12
    mwe_extractor.corpus[10]
    mwe_extractor.corpus[100]


    # doc 0
    'our_unique_culture'

    # doc 10
    'bring_to_wsp_we'
    'maximizes_the_contribution_individuals_can'
    'development_opportunities_you'


    mwe_blacklist = identify_mwe_with_leading_and_trailing_stopwords(mwe_export, stopwords)
    mwe_model = remove_blacklisted_mwe(mwe_model, mwe_blacklist)
    corpus_mwe = tokenise_mwe(corpus_tokenised, mwe_model)
    corpus_mwe[0]

    mwe_model = extract_mwe(corpus_mwe)
    mwe_export = export_mwe(mwe_model)
    mwe_blacklist = identify_mwe_with_leading_and_trailing_stopwords(mwe_export, stopwords)
    mwe_model = remove_blacklisted_mwe(mwe_model, mwe_blacklist)
    corpus_mwe = tokenise_mwe(corpus_tokenised, mwe_model)
    corpus_mwe[0]
    corpus_mwe[10]

    mwe_model.vocab
    # Train model 2-3 times, then filter blacklisted mwe on the model.vocab, then store model for subsequent use.

    "is_a_client" in mwe_model.vocab.keys()
    del mwe_model.vocab["is_a_client"]
    "is_a_client" in mwe_model.vocab.keys()

    mwe_bigram_model = Phrases(
        sentences=corpus_preprocessed,
        min_count=10,
        threshold=0,
        scoring="npmi",
        connector_words=ENGLISH_CONNECTOR_WORDS)
    mwe_bigrams_export = mwe_bigram_model.export_phrases()
    mwe_bigrams_export_sorted = sort_mwe_export(mwe_bigrams_export)

    corpus_bigrams = []
    for doc in corpus_preprocessed:
        doc_bigrams = mwe_bigram_model[doc]
        corpus_bigrams.append(doc_bigrams)
    len(corpus_bigrams)
    corpus_bigrams[1]


    ### Train Trigrams model:
    mwe_trigram_model = Phrases(
        sentences=corpus_bigrams,
        min_count=10,
        threshold=0,
        scoring="npmi",
        connector_words=ENGLISH_CONNECTOR_WORDS)
    mwe_trigrams_export = mwe_trigram_model.export_phrases()
    mwe_trigrams_export_sorted = sort_mwe_export(mwe_trigrams_export)

    corpus_trigrams = []
    for doc in corpus_bigrams:
        doc_trigrams = mwe_trigram_model[doc]
        corpus_trigrams.append(doc_trigrams)
    len(corpus_trigrams)
    corpus_trigrams[1]
