#!/usr/local/bin/venv4semantic/bin/python
# coding=utf-8
import logging
import os

import learning.train as train
from util.digits_pattern import digits

if __name__ == '__main__':
    opts = train.options()
    password_file = opts.passwords

    verbose_levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    verbose_level = sum(opts.v) if opts.v else 0
    logging.basicConfig(level=verbose_levels[verbose_level])
    train.log.setLevel(verbose_levels[verbose_level])
    if opts.number_split:
        digits.parse_file(password_file)
    train.train_grammar(password_file,
                        opts.output_folder,
                        opts.tagtype,
                        opts.estimator,
                        opts.abstraction,
                        opts.num_workers)
    if opts.number_split:
        digits.to_pickle(os.path.join(opts.output_folder, "number_split.pickle"))
