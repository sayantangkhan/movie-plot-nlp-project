#!/bin/bash

cd data/embedded_corpus_tensor/
cat xaa xab xac xad xae xaf xag xah xai xaj xak xal xam xan xao xap xaq xar xas xat > ../embedded_corpus_tensor.pt
cd ../

corpus_checksum=294004621d3153c1138577baf527d73e77bdfc8b5fe30a841a591938ac17b636
if ! echo "$corpus_checksum embedded_corpus_tensor.pt" | sha256sum -c -; then
    echo "Checksum failed" >&2
    exit 1
fi

cd wikipedia_plots/
cat xaa xab xac xad xae xaf xag xah > ../wikipedia_plots.pkl
cd ../

wikipedia_checksum=ae9f8617dc1bd0c358dd51a628eb9d7711267735a577c17f46907390cf11f266
if ! echo "$wikipedia_checksum wikipedia_plots.pkl" | sha256sum -c -; then
    echo "Checksum failed" >&2
    exit 1
fi
