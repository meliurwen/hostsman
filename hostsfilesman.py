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


def read_listfile(hosts_file, address):
    import_entries = []
    line_number = 1
    for line in hosts_file:
        line = line.partition("#")[0].strip()
        if line:
            line = line.split()
            line_length = len(line)
            if line_length == 1:
                import_entries.append([address, line[0]])
            else:
                print(
                    "[Warning] Bad entry in '{path}' "
                    "at line {line_n}".format(
                        path=hosts_file.name,
                        line_n=line_number
                    ),
                    file=sys.stderr
                )
        line_number += 1
    return pd.DataFrame(import_entries, columns=["address", "hostname"])


def read_hostsfile(hosts_file):
    import_entries = []
    line_number = 1
    for line in hosts_file:
        line = line.partition("#")[0].strip()
        if line:
            line = line.split()
            line_length = len(line)
            if line_length == 2:
                import_entries.append(line)
            elif line_length > 2:
                address = line[0]
                for host in line[1:]:
                    import_entries.append([address, host])
            else:
                print(
                    "[Warning] Bad entry in '{path}' "
                    "at line {line_n}".format(
                        path=hosts_file.name,
                        line_n=line_number
                    ),
                    file=sys.stderr
                )
        line_number += 1
    return pd.DataFrame(import_entries, columns=["address", "hostname"])


def detect_format(hosts_file):
    line = hosts_file.readline()
    file_format = "empty"
    cnt = 1
    while line and (cnt < 128):
        line = line.partition("#")[0].strip()
        if line:
            line = line.split()
            line_length = len(line)
            if line_length == 2:
                if file_format in ("empty", "2_format"):
                    file_format = "2_format"
                elif file_format == "multi_format":
                    file_format = "multi_format"
                else:
                    return "unknown"
            elif line_length > 2:
                if file_format in ("empty", "2_format", "multi_format"):
                    file_format = "multi_format"
                else:
                    return "unknown"
            else:
                if file_format in ("empty", "mono_format"):
                    file_format = "mono_format"
                else:
                    return "unknown"
        line = hosts_file.readline()
        cnt += 1
    hosts_file.seek(0)  # Reset read/write position in the file
    return file_format


def read_file(hosts_file, file_format="auto", address="0.0.0.0"):
    if file_format == "auto":
        if hosts_file.name == "<stdin>":
            file_format = "multi_format"
        else:
            file_format = detect_format(hosts_file)
    if file_format in ("multi_format", "2_format"):
        hosts_file = read_hostsfile(hosts_file)
    elif file_format == "mono_format":
        hosts_file = read_listfile(hosts_file, address)
    else:
        print(
            "[Warning] Unrecognized file '{path}'. "
            "Treating it as empty...".format(
                path=hosts_file.name
            ),
            file=sys.stderr
        )
        hosts_file = pd.DataFrame(columns=["address", "hostname"])
    return hosts_file


def append_hosts(hosts_files_list):
    df_h = pd.DataFrame(columns=["address", "hostname"])
    for hosts_file in hosts_files_list:
        df_h = df_h.append(
            read_file(hosts_file),
            ignore_index=True,
            sort=False
        )
    return df_h


def intersect_hosts(hosts_files_list):
    df_h = pd.DataFrame(columns=["address", "hostname"])
    is_first_cycle = True
    for hosts_file in hosts_files_list:
        if is_first_cycle:
            df_h = read_file(hosts_file)
            is_first_cycle = False
        else:
            df_h = pd.merge(
                df_h,
                read_file(hosts_file)["hostname"],
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
            df_h = read_file(hosts_file)
            is_first_cycle = False
        else:
            df_h = pd.merge(
                df_h,
                read_file(hosts_file)["hostname"],
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
        elif filter_mode == "all":
            df_h = filter_cols(df_h, "hostname", HNAME_RFC1123_R)
            df_h = filter_ip(df_h)
        else:
            pass
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

    args = parser.parse_args()

    main(args)
