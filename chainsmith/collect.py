import argformat
import argparse
import hashlib
import sqlite3
import os
import pandas as pd
import random
import requests
from pathlib import Path
from time import sleep
from tqdm import tqdm

def download(url):
    """Download data from URL."""
    # Get URL
    response = requests.get(url, headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
    })

    # Sleep for a random amount of time
    sleep(2*random.random())

    # Return response as text
    return response.text



def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description     = 'Collect ChainSmith dataset',
        formatter_class = argformat.StructuredFormatter,
    )

    # Optional arguments
    parser.add_argument('--database', default='release.db', help='path to ChainSmith database')
    parser.add_argument('--outdir'  , default=Path(__file__).absolute().parent / 'html', help='path to output html files')

    # Parse arguments
    args = parser.parse_args()

    # Set output directory
    outdir = Path(args.outdir)

    # Open connection with databbase
    with sqlite3.connect(args.database) as connection:
        # Read data into dataframe
        df = pd.read_sql_query("SELECT * FROM iocs", connection)

    # Get list of urls
    urls = set(map(str, df['url'].values))

    # Download data
    for url in tqdm(sorted(urls), desc='Collecting'):
        # Get hash of url
        hash = hashlib.sha256(url.encode('utf-8')).hexdigest()

        # Create output file
        outfile = outdir / hash
        # Check if output file exists
        if os.path.isfile(outfile): continue

        # Download data
        data = download(url)

        # Write data to output file
        with open(outfile, 'w') as outfile:
            outfile.write(data)



if __name__ == '__main__':
    main()