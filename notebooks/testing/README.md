# Model Comparison

This folder contains the notebook used to test our three models: [naive substring similarity](substring_similarity.ipynb), [Okapi](okapi_bm25.ipynb), and [Embed-and-rerank](embed_and_rerank.ipynb).
Accuracy testing was done using our scraped IMDB user-summary dataset. We also manually compared the types of misclassifications given by Okapi vs Embed-and-rerank, and decided that although they had the same accuracy on our test set, embed-and-rerank performed better on synonyms and so would be a better base for a search engine.

See our [main README](../../README.md#classifier) for more discussion.
