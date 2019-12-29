include guessing/makefile

all: venv_init requirements_init nltk_data

venv_init:
	python3 -m venv venv

requirements_init:
	./venv/bin/pip install -r ./requirements.txt

nltk_data:
	echo -e "n\n" | ./venv/bin/python -m nltk.downloader wordnet wordnet_ic sentiwordnet

.PHONY: clean
clean:
	rm -f guessmaker
