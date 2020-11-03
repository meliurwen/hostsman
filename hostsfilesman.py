#!/usr/bin/env python3

import sys
import argparse
import warnings
import pandas as pd

__author__ = "Meliurwen"
__version__ = "0.0.1"
__license__ = "GPLv3"

# hostname: https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address
# ipv4: https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch07s16.html
# ipv6: https://community.helpsystems.com/forums/intermapper/miscellaneous-topics/5acc4fcf-fa83-e511-80cf-0050568460e4

HNAME_RFC1123_R = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
IPV4_R = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
IPV6_R = r"^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$"


def filter_cols(df_h, colname, regex):
    return df_h[df_h[colname].str.contains(regex, regex=True)]


def filter_ip(df_h):
    cont_ipv4_df_h = df_h["address"].str.contains(IPV4_R, regex=True)
    cont_ipv6_df_h = df_h["address"].str.contains(IPV6_R, regex=True)
    return df_h[cont_ipv4_df_h | cont_ipv6_df_h]


def read_hostsfile(hosts_file):
    return pd.read_csv(
        hosts_file,
        header=None,
        names=["address", "hostname"],
        na_filter=False,
        skip_blank_lines=True, comment="#",
        delim_whitespace=True
    )


def append_hosts(hosts_files_list):
    df_h = pd.DataFrame(columns=["address", "hostname"])
    for hosts_file in hosts_files_list:
        df_h = df_h.append(
            read_hostsfile(hosts_file),
            ignore_index=True,
            sort=False
        )
    return df_h


def intersect_hosts(hosts_files_list):
    df_h = pd.DataFrame(columns=["address", "hostname"])
    is_first_cycle = True
    for hosts_file in hosts_files_list:
        if is_first_cycle:
            df_h = read_hostsfile(hosts_file)
            is_first_cycle = False
        else:
            df_h = pd.merge(
                df_h,
                read_hostsfile(hosts_file)["hostname"],
                how="inner",
                on="hostname",
                sort=False,
            )
    return df_h


def subctract_hosts(hosts_files_list):
    df_h = pd.DataFrame(columns=["address", "hostname"])
    is_first_cycle = True
    for hosts_file in hosts_files_list:
        if is_first_cycle:
            df_h = read_hostsfile(hosts_file)
            is_first_cycle = False
        else:
            df_h = pd.merge(
                df_h,
                read_hostsfile(hosts_file)["hostname"],
                indicator=True,
                how="left",
                on="hostname",
                sort=False,
            )[lambda x: x._merge == "left_only"].drop("_merge", 1)
    return df_h


def main(arguments):
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
        if filter_mode == "host":
            df_h = filter_cols(df_h, "hostname", HNAME_RFC1123_R)
        elif filter_mode == "ipv4":
            df_h = filter_cols(df_h, "address", IPV4_R)
        elif filter_mode == "ipv6":
            df_h = filter_cols(df_h, "address", IPV6_R)
        else:
            df_h = filter_cols(df_h, "hostname", HNAME_RFC1123_R)
            df_h = filter_ip(df_h)
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

    parser = argparse.ArgumentParser(
        prog='Hosts File Manager',
        description='Manages hosts files'
    )
    actions_group = parser.add_mutually_exclusive_group()
    actions_group.add_argument(
        "-u", "--union",
        action="store_true",
        required=False,
        help="merge hosts files"
    )
    actions_group.add_argument(
        "-i", "--intersection",
        action="store_true",
        required=False,
        help="hosts in common between hosts files"
    )
    actions_group.add_argument(
        "-s", "--subtraction",
        action="store_true",
        required=False,
        help="hosts in common between hosts files"
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
        choices=["host", "ipv4", "ipv6", "all"],
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

    args = parser.parse_args()

    main(args)
