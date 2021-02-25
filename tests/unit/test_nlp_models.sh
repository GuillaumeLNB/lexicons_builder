#!/bin/bash
for model in $(ls ../nlp_models/*);
do
    echo -n "$model\t" >> results.tsv;
    python3.6 load_nlp_model.py $model 2>> results.tsv;
    echo "" >> results.tsv;
done