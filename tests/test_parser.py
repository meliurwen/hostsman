#!/usr/bin/env python3

import pytest
from hostsman import __version__
from hostsman.__main__ import parser_create


def test_version(capsys):
    parser_orig = parser_create()

    with pytest.raises(SystemExit) as sys_exit:
        parser_orig.parse_args(['--version'])
    assert sys_exit.value.code == 0
    stdout_orig = capsys.readouterr().out

    assert stdout_orig == "hostsman (version {})\n".format(__version__)


# Tests presence and mutual exclusivity of set operations
def test_set_operations():
    parser_orig = parser_create()

    set_operations = [
        {"args": ["-u"], "res": {"u": True, "i": False, "s": False}},
        {"args": ["--union"], "res": {"u": True, "i": False, "s": False}},
        {"args": ["--i"], "res": {"u": False, "i": True, "s": False}},
        {"args": ["--intersection"], "res": {"u": False, "i": True, "s": False}},
        {"args": ["--s"], "res": {"u": False, "i": False, "s": True}},
        {"args": ["--subtraction"], "res": {"u": False, "i": False, "s": True}}
    ]

    for operation in set_operations:
        arguments_orig = parser_orig.parse_args(operation["args"])
        assert arguments_orig.union == operation["res"]["u"]
        assert arguments_orig.intersection == operation["res"]["i"]
        assert arguments_orig.subtraction == operation["res"]["s"]
