#!/usr/bin/env bash
python3 -m venv venv
./venv/bin/pip install -r ./requirements.txt
./venv/bin/python -m nltk.downloader wordnet wordnet_ic sentiwordnet
cd ./guessing && make
