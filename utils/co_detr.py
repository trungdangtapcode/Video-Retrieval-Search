import bm25s
import Stemmer  # optional: for stemming
import numpy as np
stemmer = Stemmer.Stemmer("english")

DIRECTORY_INDEX = ''
retriever = None
ids = None
def init():
    global retriever, ids
    retriever = bm25s.BM25.load(DIRECTORY_INDEX, load_corpus=True)
    ids = list(range(len(retriever.corpus)))

def get_top_k(query: str, k: int):
    query = query.lower()
    query_tokens = bm25s.tokenize(query, stemmer=stemmer)
    results, scores = retriever.retrieve(query_tokens, corpus = ids, k=k)
    return np.array(results)