#!/usr/local/bin/venv4semantic/bin/python
# coding=utf-8
import logging

import learning.train as train

if __name__ == '__main__':
    opts = train.options()
    password_file = opts.passwords

    verbose_levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    verbose_level = sum(opts.v) if opts.v else 0
    logging.basicConfig(level=verbose_levels[verbose_level])
    train.log.setLevel(verbose_levels[verbose_level])

    train.train_grammar(password_file,
                        opts.output_folder,
                        opts.tagtype,
                        opts.estimator,
                        opts.abstraction,
                        opts.num_workers)
