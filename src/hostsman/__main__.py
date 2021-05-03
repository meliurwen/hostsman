#!/usr/bin/env python3

import sys
import argparse
import warnings
from . import __version__
from .hostsman import append_hosts, intersect_hosts, filter_hosts, subctract_hosts


def parser_create():

    parser = argparse.ArgumentParser(
        prog='hostsman',
        description='Manages hosts files'
    )
    actions_group = parser.add_mutually_exclusive_group()
    actions_group.add_argument(
        "-u", "--union",
        action="store_true",
        required=False,
        help="all entries of all hosts files are merged"
    )
    actions_group.add_argument(
        "-i", "--intersection",
        action="store_true",
        required=False,
        help="entries in common between hosts files"
    )
    actions_group.add_argument(
        "-s", "--subtraction",
        action="store_true",
        required=False,
        help="entries of the leftmost hosts file which are not entries of the hosts file(s) on its right"
    )
    parser.add_argument(
        "-d", "--dedupe",
        action="store_true",
        required=False,
        help="deduplicate entries with same hostnames"
    )
    parser.add_argument(
        "-f", "--filter",
        nargs="+",
        default=[],
        choices=["host", "ipv4", "ipv6", "all", "none"],
        required=False,
        help="filter entries with invalid values"
    )
    parser.add_argument(
        "-a", "--address",
        nargs=1,
        type=str,
        required=False,
        help="assign the issued address to all the entries"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__)
    )
    parser.add_argument(
        "FILE",
        type=argparse.FileType('r'),
        nargs="*",
        default=[sys.stdin],
        help="hosts file(s)"
    )

    return parser


def main():

    arguments = parser_create().parse_args()

    if arguments.union:
        df_h = append_hosts(arguments.FILE)
    elif arguments.intersection:
        df_h = intersect_hosts(arguments.FILE)
    elif arguments.subtraction:
        df_h = subctract_hosts(arguments.FILE)
    else:
        df_h = append_hosts(arguments.FILE)
    for filter_mode in arguments.filter:
        warnings.filterwarnings("ignore", 'This pattern has match groups')
        df_h = filter_hosts(filter_mode, df_h)
    if arguments.dedupe:
        df_h = df_h.drop_duplicates(
            subset=["hostname"],
            keep="last",
            ignore_index=True
        )
    if arguments.address:
        df_h["address"] = arguments.address[0]

    df_h.to_csv(
        sys.stdout,
        sep=" ",
        columns=["address", "hostname"],
        header=False,
        index=False,
        compression="infer"
    )


if __name__ == "__main__":
    sys.exit(main())
