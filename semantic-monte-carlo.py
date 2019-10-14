import bisect
import itertools
import logging
import math
import os
import subprocess
import sys

import numpy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_grammar(password_file, output_folder):
    cmd = "python semantic-train.py %s %s -vv" % (password_file, output_folder)
    logger.info(cmd)
    """ may Out of Memory Error happen, so run this cmd in bash! """
    # _grammar = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    # _grammar.communicate()
    pass


def exec_sample(grammar_dir, sample_file, sample_size=10000):
    cmd = "python -m guessing.sample %d %s > %s" % (sample_size, grammar_dir, sample_file)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result.communicate()


def exec_score(path_to_grammar, sample_file, scored_sample_file):
    cmd = "python -m guessing.score %s %s > %s --uppercase --camelcase --capitalized" \
          % (path_to_grammar, sample_file, scored_sample_file)
    _score = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE)
    _score.communicate()


spliter = chr(3)


def exec_strength(sample_file, scored_password_file, monte_carlo_result_file):
    cmd = "python -m guessing.strength %s %s > %s" \
          % (sample_file, scored_password_file, monte_carlo_result_file)
    result = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE
    )
    result.communicate()
    pass


def draw_guess_crack_curve(monte_carlo_result_file, curve_name, dataset, test_set):
    abs_dir = sys.path[0]
    fin = open(test_set, "r")
    test_set_size = len(fin.readlines())
    fin.close()
    picture_program_path = os.path.join(abs_dir, "..", "picture.py")
    cmd = "%s --guess-crack-file %s " \
          "--img %s.png --pdf %s.pdf " \
          "--dataset %s --password-model SemanticGuesser " \
          "--test-set-size %d" % (
              picture_program_path, monte_carlo_result_file, curve_name, curve_name, dataset, test_set_size)
    draw = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    draw.communicate()
    pass


def __exec_strength(scored_sample_file, scored_test_file, monte_carlo_result_file):
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
            prob_col.append(int(float(row.split("\t")[-1])))
        except ValueError:
            print("row: ", row, ", row[1]: ", row[1])
            pass
    guesses, cracked = [0], [0]
    prob_col.sort()
    fout = open(guess_crack_filename, "w")
    for m, n in itertools.groupby(prob_col):
        guesses.append(m)
        cracked.append(cracked[-1] + len(list(n)))
        fout.write("%d : %d\n" % (guesses[-1], cracked[-1]))

    pass


if __name__ == "__main__":
    _tag = "rockyou-1-255-carck-myspqce-1-255"
    _abs_dir = sys.path[0]
    _password_file = "/home/chaun/Documents/Passwords/RockYou/rockyou_new.txt"
    _path_to_grammar = os.path.join(_abs_dir, "models", _tag)
    _sample_file = os.path.join(_path_to_grammar, "sample.txt")
    _test_file = "/home/chaun/Documents/Passwords/MySpace/myspace_new.txt"
    _scored_test_file = os.path.join(_path_to_grammar, "scored_test.txt")
    _strength_file = os.path.join(_path_to_grammar, "pwd_strength.txt")
    _guess_crack_file = os.path.join(_path_to_grammar, "guess_crack.txt")
    _curve_filename = os.path.join(_path_to_grammar, "guess_crack")
    logging.info("Generating grammar...")
    generate_grammar(_password_file, _path_to_grammar)
    logging.info("Generating grammar done")
    logging.info("Generating samples...")
    exec_sample(_path_to_grammar, _sample_file, sample_size=100000)
    logging.info("Generating samples done")
    logging.info("Scoring test set...")
    exec_score(_path_to_grammar, _test_file, _scored_test_file)
    logging.info("Scoring test done")
    logging.info("Evaluating strength...")
    exec_strength(_sample_file, _scored_test_file, _strength_file)
    logging.info("Evaluating strength done")
    logging.info("Generating guess crack pair...")
    generate_guess_crack(_strength_file, _guess_crack_file)
    logger.info("Generating guess crack pair done")
    logger.info("Drawing guess crack curve...")
    draw_guess_crack_curve(_guess_crack_file, _curve_filename, _tag, _test_file)
    logger.info("Drawing guess crack curve done")
