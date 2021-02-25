#!/bin/bash

mkdir nlp_models 2>/dev/null ;
i=0;
for model in $(cat model_urls);
do
    echo "MODEL $i OF $(wc -l model_urls)";
    let "i++"
    wget $model -P nlp_models/;

done
