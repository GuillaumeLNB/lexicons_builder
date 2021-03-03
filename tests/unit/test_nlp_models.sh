#!/bin/bash
for model in $(ls /nfs/nas4/readit/readit/nlp_models/*);
do
    echo -n "$model\t" >> results.tsv;
    python3.6 load_nlp_model.py $model 2>> results.tsv;
    echo "" >> results.tsv;
done