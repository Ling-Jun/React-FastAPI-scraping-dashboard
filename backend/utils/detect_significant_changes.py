# detect_significant_changes.py, functions here are mostly CPU-intensive

# from transformers import pipeline
# from scrapegraphai.graphs import (
#     SmartScraperGraph,
#     OmniScraperGraph,
#     SmartScraperMultiGraph,
# )
import itertools
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from utils.config import nlpModels, WarningMessages
import spacy, torch, re
import torch.nn.functional as F
from nltk import download
from rake_nltk import Rake
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import gensim.downloader as api
from rank_bm25 import BM25Okapi
import numpy as np


# ====================================================================================================================
#                                   Utility Functions
# ====================================================================================================================
def extract_keywords(text: str):
    """Extracts keywords from a given text using RAKE"""
    try:
        rake = Rake()
        rake.extract_keywords_from_text(text)
        return rake.get_ranked_phrases()
    except Exception as e:
        print(f"Error: {e}\n")
        download("stopwords")
        return extract_keywords(text)


def extract_ONLY_words(text: str) -> List[str]:
    """
    Breaks a string into words, handling hyphenated and plus-separated words.
    Replaces words containing - or + with their split components.
    """
    words = text.split()
    new_words = []
    for word in words:
        word = re.split(r"[-\+\>\?\(\)]", word)
        new_words.extend(word)
    return list(filter(None, new_words))


def tokenization(text: str, custom_stopwords=set()) -> List[str]:
    """
    Tokenizes text, handling hyphenated words and custom stopwords.
        improvement: handle hyphenated words
    """
    # stop_words = set(stopwords.words("english")) | custom_stopwords
    stop_words = custom_stopwords
    tokens = word_tokenize(text.lower())  # Tokenize to handle punctuation

    processed_tokens = []
    for word in tokens:
        if "-" in word:
            # Replace hyphens with spaces and tokenize the sub-words
            sub_words = word.replace("-", " ").split()
            # Extend the current token list with the subwords
            processed_tokens.extend(
                [w for w in sub_words if w.isalpha() and w not in stop_words]
            )

        elif word not in stop_words and word.isalpha():
            processed_tokens.append(word)

    return processed_tokens


def find_index_pairs_in_product_list(listA: List, listB: List):
    """
    Given a Cartesian product list from itertools.product(),
    this function recreates the index for each item in the component lists of product list

    Args:
    listA: The first list of items.
    listB: The second list of items.

    Returns:
    List[Tuple[int, int]]: A list of tuples, where each tuple contains the indices of the items
    from listA and listB that form each product tuple.

    e.g.

    the product list is:
        [('a', 'A'), ('a', 'B'), ('a', 'C'), ('b', 'A'), ('b', 'B'), ('b', 'C'), ('c', 'A'), ('c', 'B'), ('c', 'C')]

    the component lists are:
        ['a', 'b', 'c'] and ['A', 'B', 'C']

    for item ('b', 'A') in the product list, it returns (1, 0),
    which are the indices of each component item in its corresponding list
    """
    indices = [
        (i // len(listB), i % len(listB)) for i in range(len(listA) * len(listB))
    ]
    return indices


def create_similarity_matrix(diff_lines: List[str], keywords: List[str]):
    """Creates a similarity matrix between diff_lines and keywords."""

    num_diff_lines = len(diff_lines)
    num_keywords = len(keywords)
    similarity_matrix = np.zeros((num_diff_lines, num_keywords))

    for i, single_diff in enumerate(diff_lines):
        for j, single_keyword in enumerate(keywords):
            single_diff_set = set(single_diff.lower().split())
            single_keyword_set = set(single_keyword.lower().split())
            similarity_score = jaccard_similarity(single_diff_set, single_keyword_set)
            similarity_matrix[i, j] = similarity_score

    return similarity_matrix


# =================================================================================================
#                              Hugging Face spaCy lib
# =================================================================================================
def spacy_relevance(
    diff_lines: List[str],
    keywords: List[str],
    similarity_threshold: float = 0.0,
    model: str = None,
    *args,
    **kwargs,
):
    """
    run python -m spacy download en_core_web_md to download this model before using
    """
    print("Using spacy to detect relevance!\n")
    # print(f"diff_lines:{diff_lines}\n")
    if model is None:
        model = nlpModels.spaCy_Model3.value

    nlp = spacy.load(model)
    diff_embeddings = list(nlp.pipe(diff_lines))
    keywords_embeddings = list(nlp.pipe(keywords))
    index_pairs = find_index_pairs_in_product_list(diff_lines, keywords)

    matching_diff_keywords = []
    for product_index, (single_diff, single_keyword) in enumerate(
        itertools.product(diff_embeddings, keywords_embeddings)
    ):
        diff_lines_index, keywords_index = index_pairs[product_index]

        if model is nlpModels.spaCy_Model3.value:
            single_diff = single_diff._.trf_data.last_hidden_layer_state.data
            single_keyword = single_keyword._.trf_data.last_hidden_layer_state.data
            single_diff = torch.from_numpy(single_diff).mean(dim=0)
            single_keyword = torch.from_numpy(single_keyword).mean(dim=0)
            similarity_score = F.cosine_similarity(
                single_diff.unsqueeze(0), single_keyword.unsqueeze(0)
            ).item()
        else:
            similarity_score = single_diff.similarity(single_keyword)

        # print(f"similarity_score: {similarity_score}\n")
        if similarity_score >= similarity_threshold:
            # print(
            #     f"diff, keyword: {diff_lines[diff_lines_index], keywords[keywords_index]}\n"
            # )
            matching_diff_keywords.append(
                (diff_lines[diff_lines_index], keywords[keywords_index])
            )
    return matching_diff_keywords


def spacy_relevance2(
    diff_lines: List[str],
    keywords: List[str],
    similarity_threshold: float = 0.0,
    model: str = None,
):
    """
    run python -m spacy download en_core_web_md to download this model before using
    """
    print("Using spacy to detect relevance!\n")
    # print(f"diff_lines:{diff_lines}\n")
    if model is None:
        model = nlpModels.spaCy_Model3.value

    nlp = spacy.load(model)
    diff_embeddings = list(nlp.pipe(diff_lines))
    keywords_embeddings = list(nlp.pipe(keywords))
    index_pairs = find_index_pairs_in_product_list(diff_lines, keywords)

    diff_index = []
    for product_index, (single_diff, single_keyword) in enumerate(
        itertools.product(diff_embeddings, keywords_embeddings)
    ):
        diff_lines_index, _ = index_pairs[product_index]

        if model is nlpModels.spaCy_Model3.value:
            single_diff = single_diff._.trf_data.last_hidden_layer_state.data
            single_keyword = single_keyword._.trf_data.last_hidden_layer_state.data
            single_diff = torch.from_numpy(single_diff).mean(dim=0)
            single_keyword = torch.from_numpy(single_keyword).mean(dim=0)
            similarity_score = F.cosine_similarity(
                single_diff.unsqueeze(0), single_keyword.unsqueeze(0)
            ).item()
        else:
            similarity_score = single_diff.similarity(single_keyword)

        # print(f"similarity_score: {similarity_score}\n")
        if similarity_score >= similarity_threshold:
            diff_index.append(diff_lines_index)

    return diff_index


# =================================================================================================
#                           Hugging Face Sentence-Transformers lib
# =================================================================================================


def word_embed_relevance(
    diff_lines: List[str],
    keywords: List[str],
    similarity_threshold: float = 0.0,
    model: str = None,
) -> List[Tuple[str, str]]:
    print("Using StenceTransformers to detect relevance!\n")
    # print(f"diff_lines:{diff_lines}\n")
    if model is None:
        model = nlpModels.ST_Model1.value

    embedding_model = SentenceTransformer(model)
    diff_embeddings = embedding_model.encode(diff_lines, convert_to_tensor=True)
    keywords_embeddings = embedding_model.encode(keywords, convert_to_tensor=True)
    index_pairs = find_index_pairs_in_product_list(diff_lines, keywords)
    # print(f"len(diff_lines):{len(diff_lines)}\n")
    # print(f"len(diff_embeddings): {len(diff_embeddings)}\n")
    matching_diff_keywords = []
    for product_index, (single_diff, single_keyword) in enumerate(
        itertools.product(diff_embeddings, keywords_embeddings)
    ):
        diff_lines_index, keywords_index = index_pairs[product_index]
        similarity_scores = util.cos_sim(single_diff, single_keyword)
        similarity_score = similarity_scores.max().item()
        print(f"similarity_score: {similarity_score}\n")
        if similarity_score >= similarity_threshold:
            # print(
            #     f"diff, keyword: {diff_lines[diff_lines_index], keywords[keywords_index]}\n"
            # )
            matching_diff_keywords.append(
                (diff_lines[diff_lines_index], keywords[keywords_index])
            )

    return matching_diff_keywords


def word_embed_relevance2(
    diff_lines: List[str],
    keywords: List[str],
    similarity_threshold: float = 0.0,
    model: str = None,
) -> List[Tuple[str, str]]:
    embedding_model = SentenceTransformer(model)
    diff_embeddings = embedding_model.encode(diff_lines, convert_to_tensor=True)
    keywords_embeddings = embedding_model.encode(keywords, convert_to_tensor=True)
    # print(f"len(diff_lines):{len(diff_lines)}\n")
    # print(f"len(diff_embeddings): {len(diff_embeddings)}\n")
    index_pairs = find_index_pairs_in_product_list(diff_lines, keywords)

    diff_index = []
    for product_index, (single_diff, single_keyword) in enumerate(
        itertools.product(diff_embeddings, keywords_embeddings)
    ):
        diff_lines_index, _ = index_pairs[product_index]
        similarity_scores = util.cos_sim(single_diff, single_keyword)
        similarity_score = similarity_scores.max().item()
        print(f"similarity_score: {similarity_score}\n")
        if similarity_score >= similarity_threshold:
            diff_index.append(diff_lines_index)
        # else:
        #     diff_index.append(0)
    return diff_index


# ================================================================================================================================
# ================================================================================================================================
#                                      Vector Space Modeling
# ================================================================================================================================
# ================================================================================================================================


def _vectorized_n_cos_sim(text: str, keyword: str) -> float:
    """
    Calculate the relevance of a text to a set of keywords using the Vector Space Model.

    Parameters:
    - text (str): The text to be evaluated.
    - keywords (str): A string of keywords separated by spaces.

    Returns:
    - float: Cosine similarity score between the text and the keywords (range: 0 to 1).
    """
    documents = [text, keyword]
    # Fit and transform the documents into TF-IDF vectors
    tfidf_matrix = TfidfVectorizer().fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    # print(f"cosine_sim.shape:{cosine_sim.shape}\n")
    return cosine_sim[0][0]


def VSM_relevance(
    diff_lines: List[str],
    keywords: List[str],
    similarity_threshold: float = 0.0,
    *args,
    **kwargs,
):
    """
    the  *args, **kwargs allows the function to accept more arguments without causing error,
    this is in case you type more arguments than needed
    """
    # print(f"diff_lines:{diff_lines}\n")
    # print(f"keywords length: {len(keywords)}\n")

    matching_diff_keywords = []
    for single_diff, single_keyword in itertools.product(diff_lines, keywords):
        # print(f"single_diff: {single_diff}\n")
        similarity_score = _vectorized_n_cos_sim(single_diff, single_keyword)
        # print(f"similarity_score is: {similarity_score}\n")
        if similarity_score >= similarity_threshold:
            # print(
            #     f"diff, keyword: {diff_lines[diff_lines_index], keywords[keywords_index]}\n"
            # )
            matching_diff_keywords.append((single_diff, single_keyword))

    return matching_diff_keywords


def VSM_relevance2(
    diff_lines: List[str],
    keywords: List[str],
    similarity_threshold: float = 0.0,
    *args,
    **kwargs,
):
    """
    the  *args, **kwargs allows the function to accept more arguments without causing error,
    this is in case you type more arguments than needed
    """
    index_pairs = find_index_pairs_in_product_list(diff_lines, keywords)
    diff_index = []
    for product_index, (single_diff, single_keyword) in enumerate(
        itertools.product(diff_lines, keywords)
    ):
        diff_lines_index, _ = index_pairs[product_index]
        similarity_score = _vectorized_n_cos_sim(single_diff, single_keyword)
        if similarity_score >= similarity_threshold:
            diff_index.append(diff_lines_index)

    return diff_index


# ====================================================================================================================
#                                          Jaccard Similarity & WMD
# ====================================================================================================================
def jaccard_similarity(set1: set, set2: set):
    """This is not a Machine Learning algorithm"""
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union else 0


def Jaccard_relevance(
    diff_lines: List[str],
    keywords: List[str],
    similarity_threshold: float = 0.0,
    *args,
    **kwargs,
):
    """This is an exact match algorithm"""
    # print(f"diff_lines:{diff_lines}\n")
    # print(f"keywords length: {len(keywords)}\n")

    matching_diff_keywords = []
    for single_diff, single_keyword in itertools.product(diff_lines, keywords):
        # print(f"single_diff: {single_diff}\n")
        single_diff_set = single_diff.lower().split()
        single_keyword_set = single_keyword.lower().split()
        similarity_score = jaccard_similarity(
            set(single_diff_set), set(single_keyword_set)
        )

        print(f"similarity_score is: {similarity_score}\n")
        if similarity_score >= similarity_threshold:
            # print(
            #     f"diff, keyword: {diff_lines[diff_lines_index], keywords[keywords_index]}\n"
            # )
            matching_diff_keywords.append((single_diff, single_keyword))

    return matching_diff_keywords


# ====================================================================================================================
#  Composite approach using BM25, WMD, and NER
# ====================================================================================================================
async def bm25_relevance(
    diff_lines: List[str], keywords: List[str], similarity_threshold=0
) -> List[Tuple[str, str]]:
    """Uses BM25 for keyword importance ranking, not a ML algorithm"""
    tokenized_diff = [tokenization(line) for line in diff_lines]
    tokenized_keywords = [tokenization(word) for word in keywords]
    # print(f"tokenized_diff:{tokenized_diff}\n")
    # print(f"tokenized_keywords:{tokenized_keywords}\n")
    bm25 = BM25Okapi(tokenized_diff)
    keyword_scores = [
        bm25.get_scores(tokenized_keyword) for tokenized_keyword in tokenized_keywords
    ]
    keyword_scores = np.array(keyword_scores)
    min_val = keyword_scores.min()
    max_val = keyword_scores.max()
    # normalization using NumPy broadcasting
    keyword_scores = np.where(
        max_val - min_val > 0, (keyword_scores - min_val) / (max_val - min_val), 0.0
    )
    # print(f"shape of keyword_scores[0]: {len(keyword_scores[0])}\n")
    # print(f"keyword_scores:{keyword_scores}\n")
    matching_diff_keywords = []
    for i, keyword in enumerate(keywords):
        for j, score in enumerate(keyword_scores[i]):
            if score >= similarity_threshold:
                matching_diff_keywords.append((diff_lines[j], keyword))

    return matching_diff_keywords


def bm25_relevance2(diff_lines: List[str], keywords: List[str], similarity_threshold=0):
    """Uses BM25 for keyword importance ranking, not a ML algorithm"""
    tokenized_diff = [tokenization(line) for line in diff_lines]
    tokenized_keywords = [tokenization(word) for word in keywords]
    bm25 = BM25Okapi(tokenized_diff)
    keyword_scores = [
        bm25.get_scores(tokenized_keyword) for tokenized_keyword in tokenized_keywords
    ]
    keyword_scores = np.array(keyword_scores)
    min_val = keyword_scores.min()
    max_val = keyword_scores.max()
    keyword_scores = np.where(
        max_val - min_val > 0, (keyword_scores - min_val) / (max_val - min_val), 0.0
    )

    diff_index = []
    for i, keyword in enumerate(keywords):
        for j, score in enumerate(keyword_scores[i]):
            if score >= similarity_threshold:
                diff_index.append(j)

    return diff_index


async def wmd_relevance(
    diff_lines: List[str], keywords: List[str], similarity_threshold=0
) -> List[Tuple[str, str]]:
    """Uses Word Mover's Distance for meaning-based similarity"""
    matching_diff_keywords = []
    w2v_model = api.load("word2vec-google-news-300")
    for single_diff, single_keyword in itertools.product(diff_lines, keywords):
        diff_tokens = tokenization(single_diff)
        keyword_tokens = tokenization(single_keyword)
        # print(f"diff_tokens:{diff_tokens}\n")
        # print(f"keyword_tokens:{keyword_tokens}\n")

        if not diff_tokens or not keyword_tokens:
            continue

        try:
            wmd_distance = w2v_model.wmdistance(diff_tokens, keyword_tokens)
            similarity_score = 1 / (1 + wmd_distance)  # Normalize to similarity score
            print(f"similarity_score:{similarity_score}\n")
            if similarity_score >= similarity_threshold:
                matching_diff_keywords.append((single_diff, single_keyword))
        except Exception as e:
            print(f"Skipping WMD due to error: {e}")

    return matching_diff_keywords


def wmd_relevance2(diff_lines: List[str], keywords: List[str], similarity_threshold=0):
    """Uses Word Mover's Distance for meaning-based similarity"""
    w2v_model = api.load("word2vec-google-news-300")

    index_pairs = find_index_pairs_in_product_list(diff_lines, keywords)
    diff_index = []
    for product_index, (single_diff, single_keyword) in enumerate(
        itertools.product(diff_lines, keywords)
    ):
        diff_lines_index, _ = index_pairs[product_index]
        wmd_distance = w2v_model.wmdistance(
            tokenization(single_diff), tokenization(single_keyword)
        )
        similarity_score = 1 / (1 + wmd_distance)
        # print(f"similarity_score:{similarity_score}\n")
        if similarity_score >= similarity_threshold:
            diff_index.append(diff_lines_index)

    return diff_index


async def NER_significance(
    diff_lines: List[str], keywords: List[str]
) -> List[Tuple[str, str]]:
    """Uses Named Entity Recognition (NER) to prioritize important words"""
    matching_diff_keywords = []
    nlp = spacy.load(nlpModels.spaCy_Model1.value)  # For Named Entity Recognition (NER)
    for single_diff in diff_lines:
        doc = nlp(single_diff)
        entities = {ent.text.lower() for ent in doc.ents}  # Extract named entities
        # print(f"entities:{entities}\n")
        for single_keyword in keywords:
            if single_keyword.lower() in entities:
                matching_diff_keywords.append((single_diff, single_keyword))

    return matching_diff_keywords


def NER_significance2(diff_lines: List[str], keywords: List[str]) -> List[str]:
    diff_index = []
    nlp = spacy.load(nlpModels.spaCy_Model1.value)
    for i, single_diff in enumerate(diff_lines):
        doc = nlp(single_diff)
        entities = {ent.text.lower() for ent in doc.ents}  # Extract named entities

        for single_keyword in keywords:
            if single_keyword.lower() in entities:
                diff_index.append(i)

    return diff_index


async def detect_significant_changes(diff_lines: List[str], keywords: List[str]):
    """Combines BM25, WMD, and NER to filter significant changes"""

    bm25_matches = await bm25_relevance(diff_lines, keywords)
    wmd_matches = await wmd_relevance(diff_lines, keywords)
    ner_matches = await NER_significance(diff_lines, keywords)
    print(bm25_matches, wmd_matches, ner_matches)

    all_matches = list(
        set(bm25_matches + wmd_matches + ner_matches)
    )  # Merge all methods
    return all_matches


def detect_significant_changes2(
    diff_lines: List[str], keywords: List[str], bm25_thresh=0, wmd_thresh=0
):
    """Combines BM25, WMD, and NER to filter significant changes"""

    bm25_matches = bm25_relevance2(
        diff_lines, keywords, similarity_threshold=bm25_thresh
    )
    wmd_matches = wmd_relevance2(diff_lines, keywords, similarity_threshold=wmd_thresh)
    ner_matches = NER_significance2(diff_lines, keywords)

    all_matches = list(set(bm25_matches + wmd_matches + ner_matches))
    return all_matches


# ====================================================================================================================
# WMD isn't suited to calculate distance between a sentence and a word
# ====================================================================================================================
# import gensim.downloader as api
# model = api.load("word2vec-google-news-300")
# def _wmd(sentence1, sentence2):
#     """Calculates the Word Mover's Distance between two sentences."""
#     # Ensure words are in the model's vocabulary
#     sentence1 = [w for w in sentence1 if w in model.wv]
#     sentence2 = [w for w in sentence2 if w in model.wv]
#     distance = model.wv.wmdistance(sentence1, sentence2)
#     return distance

# print(api.info()["models"].keys())
# # Download a smaller model - Note these may not perform as well as the larger 'word2vec-google-news-300'
# model = api.load("glove-twitter-25")  # fast download - performance may be impacted
# model = api.load("glove-wiki-gigaword-50")  # ~66MB download

# ====================================================================================================================
# Hugging Face transformers library, for generate NLP tasks, not suited for semantic similarity
# ====================================================================================================================
# from typing import Literal
# from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModelForTokenClassification, AutoModelForSeq2SeqLM
# import torch
# from scipy.spatial.distance import cosine

# def _get_sentence_embedding(sentence, model_selection: Literal['bert', 'electra']):
#     """
#     return_tensors="pt": the output should be PyTorch tensors.
#     truncation=True: If the input exceeds the model's maximum length, truncate.
#     padding=True: the tokenized output is padded to the length of the longest sequence in the batch.

#     Output: The tokenizer returns a dictionary containing:
#         input_ids: Tensor of token IDs representing the input sentence.
#         attention_mask: Tensor indicating which tokens should be attended to (1) and which are padding (0).
#     """
#     if model_selection=='bert':
#         tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
#         model = BertModel.from_pretrained("bert-base-uncased")
#         inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
#         # print(f"inputs: {inputs}\n")
#         with torch.no_grad():
#             outputs = model(**inputs)
#         # Use the embeddings of the [CLS] token
#         return outputs.last_hidden_state[:, 0, :].squeeze()
#     elif model_selection=="electra":
#         tokenizer = AutoTokenizer.from_pretrained("dbmdz/electra-large-discriminator-finetuned-conll03-english")
#         model = AutoModelForTokenClassification.from_pretrained("dbmdz/electra-large-discriminator-finetuned-conll03-english", output_hidden_states=True)
#         inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
#         with torch.no_grad():
#             outputs = model(**inputs)
#         # Use the embeddings of the [CLS] token from the last hidden state
#         return outputs.hidden_states[-1][:, 0, :].squeeze()

# def LLM_cos_sim_relevance(
#     diff_lines: List[str], keywords: List[str], similarity_threshold: float =0.9, model_selection: Literal['bert', 'electra']="bert"
# ):
#     """
#     This function runs crazy slow on laptop
#     """
#     diff_embeddings = [_get_sentence_embedding(sentence, model_selection=model_selection) for sentence in diff_lines]
#     keywords_embeddings = [_get_sentence_embedding(sentence, model_selection=model_selection) for sentence in keywords]
#     print(f"diff_lines length:{len(diff_lines)}; diff_embeddings length:{len(diff_embeddings)}\n")
#     print(f"keywords length: {len(keywords)}; keywords_embeddings length: {len(keywords_embeddings)}\n")

#     for single_diff, single_keyword in itertools.product(
#         diff_embeddings, keywords_embeddings
#     ):
#         print(f"single_diff.shape: {single_diff.shape}\n")
#         print(f"single_keyword shape: {single_keyword.shape}\n")
#         similarity = cosine(single_diff.numpy(), single_keyword.numpy())
#         print(f"similarity: {similarity}\n")
#         if similarity > similarity_threshold:
#             return WarningMessages.SignificantChange.value
#     return WarningMessages.TrivialChange.value
