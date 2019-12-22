#!/usr/bin/env bash
python3 -m venv venv
source ./venv/bin/activate
pip install -r ./requirements.txt
python -m nltk.downloader wordnet wordnet_ic sentiwordnet
cd ./guessing && make
