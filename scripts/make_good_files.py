#!/usr/bin/env python3

import argparse
import glob
import os
import sys

import ROOT


DEFAULT_REQUIRED_BRANCHES = [
    "passSelection",
    "probe_recopt_over_tag_recopt",
    "probe_l1pt",
    "probe_recopt",
    "probe_l1eta",
    "probe_l1pt_over_probe_recopt",
    "tag_recopt",
    "tag_l1pt",
    "probe_l1pt_over_tag_recopt",
    "tag_l1eta",
    "L1Dijet_dphi",
]


def get_branches(tree):
    return {branch.GetName() for branch in tree.GetListOfBranches()}


def main():
    parser = argparse.ArgumentParser(
        description="Create a list of ROOT files that contain a required set of branches."
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing ROOT files.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="good_files.txt",
        help="Output text file containing one valid ROOT file per line. Default: good_files.txt",
    )
    parser.add_argument(
        "-t",
        "--tree",
        default="Events",
        help="Name of the TTree to check. Default: Events",
    )
    parser.add_argument(
        "--pattern",
        default="*.root",
        help='Glob pattern for input files. Default: "*.root"',
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print missing branches for bad files.",
    )

    args = parser.parse_args()

    input_pattern = os.path.join(args.input_dir, args.pattern)
    files = sorted(glob.glob(input_pattern))

    if not files:
        print(f"No files found matching: {input_pattern}", file=sys.stderr)
        return 1

    required = set(DEFAULT_REQUIRED_BRANCHES)

    good_files = []
    bad_files = []

    for filename in files:
        root_file = ROOT.TFile.Open(filename)

        if not root_file or root_file.IsZombie():
            bad_files.append(filename)
            if args.verbose:
                print(f"BAD FILE: {filename}", file=sys.stderr)
            continue

        tree = root_file.Get(args.tree)

        if not tree:
            bad_files.append(filename)
            if args.verbose:
                print(f"NO TREE '{args.tree}': {filename}", file=sys.stderr)
            root_file.Close()
            continue

        branches = get_branches(tree)
        missing = sorted(required - branches)

        if missing:
            bad_files.append(filename)
            if args.verbose:
                print(f"\nMISSING BRANCHES: {filename}", file=sys.stderr)
                for branch in missing:
                    print(f"  {branch}", file=sys.stderr)
        else:
            good_files.append(filename)

        root_file.Close()

    with open(args.output, "w") as f:
        for filename in good_files:
            f.write(filename + "\n")

    print(f"Total files found: {len(files)}")
    print(f"Good files:       {len(good_files)}")
    print(f"Bad files:        {len(bad_files)}")
    print(f"Wrote:            {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())