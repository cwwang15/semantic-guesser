import argparse
import bisect
import logging
import math
import os
import subprocess
import sys
from collections import defaultdict

import numpy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_grammar(password_file, output_folder, python_env):
    cmd = "%s semantic-train.py %s %s -vv" % (python_env, password_file, output_folder)
    logger.info(cmd)
    """ may Out of Memory Error happen, so run this cmd in bash! """
    _grammar = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    _grammar.communicate()
    pass


def exec_sample(grammar_dir, sample_file, sample_size, python_env):
    cmd = "%s -m guessing.sample %d %s > %s" % (python_env, sample_size, grammar_dir, sample_file)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result.communicate()


def exec_score(path_to_grammar, sample_file, scored_sample_file, python_env, print_split=False):
    if print_split:
        cmd = "%s -m guessing.score %s %s > %s --uppercase --camelcase --capitalized --print_split" \
              % (python_env, path_to_grammar, sample_file, scored_sample_file)
    else:
        cmd = "%s -m guessing.score %s %s > %s --uppercase --camelcase --capitalized" \
              % (python_env, path_to_grammar, sample_file, scored_sample_file)

    _score = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE)
    _score.communicate()


def exec_strength(scored_sample_file, scored_test_file, monte_carlo_result_file):
    fin_scored_sample = open(scored_sample_file, "r")
    log_probs = []
    for line in fin_scored_sample:
        line = line.strip("\r\n")
        pwd, prob = line.split("\t")
        logprob = -math.log2(max(float(prob), sys.float_info.min))
        log_probs.append(logprob)

    fin_scored_sample.close()
    log_probs = numpy.fromiter(log_probs, float)
    log_probs.sort()
    log_n = math.log2(len(log_probs))
    positions = (2 ** (log_probs - log_n)).cumsum()
    fin_scored_test = open(scored_test_file, "r")

    pwd_counter = defaultdict(lambda: [0, .0])
    total = 0
    for line in fin_scored_test:
        line = line.strip("\r\n")
        try:
            lst = line.split(" ")
            pwd = lst[0]
            prob = lst[-1]
        except Exception as e:
            print(e)
            sys.exit(-1)
        pwd_counter[pwd][0] += 1
        pwd_counter[pwd][1] = -math.log2(max(float(prob), sys.float_info.min))
        total += 1
    fin_scored_test.close()
    pwd_counter = dict(sorted(pwd_counter.items(), key=lambda x: x[1][1]))
    prev_rank = 0
    addon = 1
    cracked = 0
    fout = open(monte_carlo_result_file, "w")
    for pwd, (cnt, lp) in pwd_counter.items():
        idx = bisect.bisect_right(log_probs, lp)
        rank = math.ceil(max(positions[idx - 1] if idx > 0 else 1, prev_rank + addon))
        cracked += cnt
        prev_rank = rank
        fout.write(f"{pwd}\t{lp}\t{cnt}\t{rank}\t{cracked}\t{cracked / total * 100:5.2f}\n")
    fout.flush()
    fout.close()


def main():
    parser = argparse.ArgumentParser(description="Semantic Guesser: Monte Carlo Simulation")
    parser.add_argument("-t", "--test-file", type=str, required=True)
    parser.add_argument("-d", "--grammar-dir", required=True, type=str)
    parser.add_argument("--use-samples", dest="use_samples", type=str, required=False, default="no_default",
                        help="do not generate samples, use given samples")
    parser.add_argument("--scored", dest="scored_test_file", type=str, required=False, default="use_default")
    parser.add_argument("--result", dest="guess_crack_file", type=str, required=True)
    parser.add_argument("--sample-size", dest="sample_size", type=int, required=False, default=100000)
    parser.add_argument("--env", dest="python_env", type=str, required=True)
    parser.add_argument('--print_split', dest="print_split", action="store_true")
    args = parser.parse_args()
    _path_to_grammar = args.grammar_dir
    _python_env = args.python_env
    _sample_file = os.path.join(_path_to_grammar, "sample.txt")
    _scored_test_file = args.scored_test_file
    _guess_crack_file = args.guess_crack_file
    # if not args.use_grammar:
    #     logging.info("Generating grammar...")
    #     generate_grammar(args.pwd_file, _path_to_grammar, _python_env)
    #     logging.info("Generating grammar done")
    if args.use_samples == "no_default":
        logging.info("Generating samples...")
        exec_sample(_path_to_grammar, _sample_file, sample_size=args.sample_size, python_env=_python_env)
        logging.info("Generating samples done")
    else:
        _sample_file = args.use_samples
    logging.info("Scoring test set...")
    exec_score(_path_to_grammar, args.test_file, _scored_test_file, _python_env, print_split=args.print_split)
    logging.info("Scoring test done")
    logging.info("Evaluating strength...")
    exec_strength(_sample_file, _scored_test_file, _guess_crack_file)
    logging.info("Evaluating strength done")


if __name__ == '__main__':
    main()
