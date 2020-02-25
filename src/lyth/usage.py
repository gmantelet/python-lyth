"""
This modules defines the command line parser.
"""
import argparse

parser = argparse.ArgumentParser(description="Lyth: A (monolithic) compiled language")

parser.add_argument("-c", metavar="cmd", type=str, help="Execute command")


def fetch(line):
    """
    Augments the args object of parser with external information from commands.
    """
    args = parser.parse_args(line)

    args.cycle = int(args.c.split('=')[1]) if args.c is not None else 0
    del args.c

    return args
