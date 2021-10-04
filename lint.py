#!/usr/bin/env python

import sys
import argparse
import logging
from pylint.lint import Run

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)

parser = argparse.ArgumentParser(prog="LINT")

parser.add_argument(
    "-p",
    "--path",
    nargs="+",
    help=(
        "path to directory you want to run pylint | "
        "Default: %(default)s | "
        "Type: %(type)s "
    ),
    default="./",
)

parser.add_argument(
    "-t",
    "--threshold",
    help=(
        "score threshold to fail pylint runner | "
        "Default: %(default)s | "
        "Type: %(type)s "
    ),
    default=7,
    type=float,
)

args = parser.parse_args()
path = list(args.path)
threshold = float(args.threshold)

files = "\n* ".join(path)
logger.info(f"PyLint Starting | Threshold: {threshold} | Files:\n* {files}")

results = Run(path, do_exit=False)

final_score = results.linter.stats["global_note"]

if final_score < threshold:

    message = f"PyLint Failed | Score: {final_score} | Threshold: {threshold}"

    logger.error(message)

    raise Exception(message)

message = f"PyLint Passed | Score: {final_score} | Threshold: {threshold}"

logger.info(message)

sys.exit(0)
