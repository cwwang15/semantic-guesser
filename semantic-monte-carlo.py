import bisect
import csv
import itertools
import logging
import math
import os
import subprocess

import numpy

import learning.train as train
from learning import model


def generate_grammar(password_file, output_folder):
    cmd = "python semantic-train.py %s %s -vv" % (password_file, output_folder)
    _grammar = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    _grammar.communicate()
    pass


def exec_sample(grammar_dir, sample_file, sample_size=10000):
    grammar = model.Grammar.from_files(grammar_dir)
    fout = open(sample_file, "w")
    for password, base_struct, p in grammar.sample(sample_size):
        fout.write("{}\t{}\n".format(password, p))
    fout.flush()
    fout.close()


def exec_score(path_to_grammar, sample_file, scored_sample_file):
    cmd = "python -m guessing.score %s %s > %s --uppercase --camelcase --capitalized" \
          % (path_to_grammar, sample_file, scored_sample_file)
    _score = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE)
    _score.communicate()


spliter = chr(3)


def exec_strength(scored_sample_file, scored_test_file, monte_carlo_result_file):
    fin_scored_sample = open(scored_sample_file, "r")
    sample = []
    for line in fin_scored_sample:
        line = line.strip("\r\n")
        pwd, prob = line.split("\t")
        sample.append((-math.log2(float(prob)), pwd))
    fin_scored_sample.close()
    log_probs = numpy.fromiter((lp for lp, _ in sample), float)
    log_probs.sort()
    log_n = math.log2(len(log_probs))
    positions = (2 ** (log_probs - log_n)).cumsum()
    fin_scored_test = open(scored_test_file, "r")
    fout = open(monte_carlo_result_file, "w")

    for line in fin_scored_test:
        line = line.strip("\r\n")
        try:
            pwd, struct, prob = line.split(" ")
        except ValueError:
            continue
        # noinspection PyBroadException
        try:
            log_prob = -math.log2(float(prob))
        except Exception:
            log_prob = float("inf")
        idx = bisect.bisect_right(log_probs, log_prob)
        fout.write("%s%s%f\n" % (pwd, spliter, positions[idx - 1] if idx > 0 else 0))
    fin_scored_test.close()
    fout.flush()
    fout.close()
    pass


def generate_guess_crack(monte_carlo_result_filename, guess_crack_filename):
    fin = open(monte_carlo_result_filename, "r")

    prob_col = []
    for row in fin:
        try:
            row = row.strip("\r\n")
            prob_col.append(int(float(row.split(spliter)[-1])))
        except ValueError:
            print("row: ", row, ", row[1]: ", row[1])
            pass
    guesses, cracked = [0], [0]
    prob_col.sort()
    fout = open(guess_crack_filename, "w")
    for m, n in itertools.groupby(prob_col):
        guesses.append(m)
        cracked.append(cracked[-1] + len(list(n)))
        fout.write("%d: %d\n" % (guesses[-1], cracked[-1]))

    pass


if __name__ == "__main__":
    _password_file = "./util/train.txt"
    _path_to_grammar = "./models/rockyou-all"
    _sample_file = os.path.join(_path_to_grammar, "sample.txt")
    _scored_sample_file = os.path.join(_path_to_grammar, "scored_sample.txt")
    _test_file = "./util/test.txt"
    _scored_test_file = os.path.join(_path_to_grammar, "scored_test.txt")
    _result_file = os.path.join(_path_to_grammar, "result.txt")
    _guess_crack_file = os.path.join(_path_to_grammar, "guess_crack.txt")
    # generate_grammar(_password_file, _path_to_grammar)
    # exec_sample(_path_to_grammar, _sample_file)
    # exec_score(_path_to_grammar, _test_file, _scored_test_file)
    # exec_strength(_sample_file, _scored_test_file, _result_file)
    generate_guess_crack(_result_file, _guess_crack_file)
