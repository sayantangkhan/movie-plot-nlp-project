import pandas as pd
import ast
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder, util

bi_encoder_model = "msmarco-distilbert-base-v4"
cross_encoder_model = "cross-encoder/ms-marco-MiniLM-L-6-v2"

bi_encoder = SentenceTransformer(bi_encoder_model)
bi_encoder.max_seq_length = 256  # Truncate long passages to 256 tokens
cross_encoder = CrossEncoder(cross_encoder_model)

pre_cross_encode_k = 100
pre_cross_encode_k_constraints = 300
results_to_show = 10

plots = pd.read_csv("/home/sayantan/DataScienceBootcamp/movie-plot-nlp-project/Data/wiki_with_revenue.csv",
                    compression="zip", converters={'to_embed': ast.literal_eval})
id_and_summary = pd.read_csv(
    "/home/sayantan/DataScienceBootcamp/movie-plot-nlp-project/Data/id_and_summary.csv", compression="zip")

# If running on a non-GPU kernel
corpus_embeddings = torch.load(
    '/home/sayantan/DataScienceBootcamp/movie-plot-nlp-project/inference-models/corpus_embeddings.pt', map_location=torch.device('cpu'))

def satisfies_genre_constraint(genre, movie_id, wiki_dataset):
    if genre == "Any":
        return True
    return wiki_dataset['Genre'] == genre

def satisfies_year_constraint(year_string, movie_id, wiki_dataset):
    if year_string == "Any":
        return True
    year = int(year_string)
    return year-10 <= wiki_dataset['Year'] <= year+10

def semantic_query(query_string, constraints, corpus_embeddings=corpus_embeddings, bi_encoder=bi_encoder, cross_encoder=cross_encoder, id_and_summary=id_and_summary, wiki_dataset=plots):
    constraint_genre = constraints['genre']
    constraint_year = constraints['year']

    if not (constraint_genre == "Any" and constraint_year == "Any"):
        pre_cross_encode_k = pre_cross_encode_k_constraints

    query_embedding = bi_encoder.encode(query_string, convert_to_tensor=True)
    pre_cross_encode_hits = util.semantic_search(
        query_embedding, corpus_embeddings, top_k=pre_cross_encode_k)

    cross_inp = [[query_string, id_and_summary['to_embed']
                  [hit['corpus_id']]] for hit in pre_cross_encode_hits[0]]
    cross_scores = cross_encoder.predict(cross_inp)
    cross_encoder_res = sorted(
        enumerate(cross_scores), key=lambda x: x[1], reverse=True)

    res_movie_title_and_year = []
    res_score = []

    for res in cross_encoder_res:
        if len(res_movie_title_and_year) >= results_to_show:
            break

        index = res[0]
        score = res[1]
        corpus_id = pre_cross_encode_hits[0][index]['corpus_id']
        movie_id = id_and_summary['MovieId'][corpus_id]
        movie_title = wiki_dataset['Title'][movie_id]
        movie_year = wiki_dataset['Release Year'][movie_id]
        wiki_url = wiki_dataset['Wiki Page'][movie_id]
        if not (movie_title.strip(), movie_year, wiki_url) in res_movie_title_and_year:
            if satisfies_genre_constraint(constraint_genre, movie_id, wiki_dataset) and satisfies_year_constraint(constraint_year, movie_id, wiki_dataset):
                res_movie_title_and_year.append(
                    (movie_title.strip(), movie_year, wiki_url))
                res_score.append(score)
    return list(zip(res_movie_title_and_year, res_score))
