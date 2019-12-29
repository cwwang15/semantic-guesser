include guessing/makefile

all: venv_init requirements_init ntlk_data

venv_init:
	python3 -m venv venv

requirements_init:
	./venv/bin/pip install -r ./requirements.txt

ntlk_data:
	./venv/bin/python -m ntlk.downloader wordnet wordnet_ic sentiwordnet

.PHONY: clean
clean:
	rm -f guessmaker
