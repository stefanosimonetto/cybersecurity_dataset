import argformat
import argparse
import json
import random
from pathlib import Path

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description     = 'Randomly select files to inspect for creating ground truth',
        formatter_class = argformat.StructuredFormatter,
    )

    # Optional arguments
    parser.add_argument('json'    , help='outfile in which to store ground truth')
    parser.add_argument('files', nargs='+', help='possible files to select')
    parser.add_argument('--amount', type=int, default=50, help='number of documents to randomly select')
    parser.add_argument('--seed'  , type=int, default=42, help='seed to use for random select')

    # Parse arguments
    args = parser.parse_args()

    ########################################################################
    #                           Select documents                           #
    ########################################################################

    # Apply random seed
    random.seed(args.seed)
    # Select files
    selected = random.choices(args.files, k=args.amount)

    # Get filenames from paths
    files = [Path(path).name for path in selected]

    ########################################################################
    #                            Create outfile                            #
    ########################################################################

    # Create template
    template = {
        "IPv4"  : [],
        "URL"   : [],
        "MD5"   : [],
        "SHA1"  : [],
        "SHA256": [],
        "CVE"   : [],
    }

    # Create output
    output = {filename: template for filename in files}

    # Write output
    with open(args.json, 'w') as outfile:
        json.dump(output, outfile, indent='    ')


if __name__ == '__main__':
    main()