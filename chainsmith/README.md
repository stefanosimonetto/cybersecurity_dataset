# Chainsmith dataset
This dataset was created to reproduce and compare the results of Chainsmith of the paper
`Z. Zhu and T. Dumitraș, "ChainSmith: Automatically Learning the Semantics of Malicious Campaigns by Mining Threat Intelligence Reports," in 3rd IEEE European Symposium on Security and Privacy, London, UK, 2018.`

The original dataset consists of a `sqlite3` database called [release.db](http://chainsmith.umiacs.umd.edu/tdumitra/chainsmith/release.db), also see http://chainsmith.umiacs.umd.edu/tdumitra/chainsmith/#/downloads.
`release.db` contains a table of indicators of compromise (IOCs) extracted from the following data sources:

| **Source**         | **n_posts** | **Time span**             | **n_IOCs (unique)** |
|--------------------|-------------|---------------------------|---------------------|
| forcepoint         |  101        |  2010-07-26 - 2018-05-17  |  1259               |
| hexacorn           |  73         |  2011-11-28 - 2020-12-05  |  154                |
| infoSec            |  153        |  2004-05-06 - 2018-06-23  |  197                |
| malwarebytes       |  898        |  2012-06-29 - 2019-06-21  |  2803               |
| sophos             |  596        |  2000-11-24 - 2019-06-11  |  1136               |
| sucuri             |  579        |  2009-08-10 - 2021-02-12  |  4506               |
| tao_security       |  159        |  2003-12-16 - 2013-11-14  |  526                |
| trend_micro        |  170        |  2009-10-02 - 2020-07-10  |  168                |
| virus_bulletin     |  350        |  2005-10-01 - 2016-01-29  |  1357               |
| we_live_security   |  632        |  2009-05-13 - 2018-03-14  |  1938               |
| webroot            |  371        |  2009-03-31 - 2018-01-18  |  9753               |

Retrieved from http://chainsmith.umiacs.umd.edu/tdumitra/chainsmith/#/home#data-sources at 2022-08-03.

## Database
The database contains a single table `iocs`.
This table consists of the following columns:

| **Column** |
|------------|
| ioc        |
| ioc_norm   |
| category   |
| label      |
| url        |
| source     |
| title      |
| post_date  |

## HTML & text
Unfortunately, Chainsmith does not include the text or html webpages from which the text was extracted.
Instead, they include a `source` column in the database containing a URL for each IOC to the original report in which they occured.
In total, we successfully retrieved 3905 different documents out of the original 4082 sources (see [Missing sources](#missing-sources)).

### HTML
We extend this dataset by downloading the HTML pages using the `collect.py` script which downloads all unique `source` values into the `./html/` directory.
As a naming convention, we use the `sha256` hash of the URL for the file names:

```python
import hashlib
filename = hashlib.sha256(<url>.encode('utf-8')).hexdigest()
```

### Text
After downloading all files, we extract the content of the HTML pages using the `parse.py` script.
This script contains extractors specific to each source and uses the extractors to convert HTML pages into text.

## Missing sources
The following sources could not be retrieved (as of 2022-08-03), because they were taken offline:
 * All `trend_micro` sources (170 sources).
 * https://blogs.forcepoint.com/security-labs/angler-exploit-kits-last-heartbeat
 * https://blogs.forcepoint.com/security-labs/d%C3%A9j%C3%A0-vu-petya-ransomware-appears-smb-propagation-capabilities
 * https://blogs.forcepoint.com/security-labs/lockys-new-dga-seeding-new-domains
 * https://blogs.forcepoint.com/security-labs/mint-linux-website-breach-lead-trojanised-iso-and-data-theft
 * https://blogs.forcepoint.com/security-labs/torrentlocker-back-and-targets-sweden-italy
 * https://blogs.forcepoint.com/security-labs/vulnerability-google-chromes-default-pdf-reader-cve-2016-1681
 * https://www.webroot.com/blog/2018/01/18/how-to-keep-cryptocurrency-secure/

Note that these sources are still in the `./html/` directory, but do not occur in the `./text/` directory because the downloaded 'empty' HTML pages could not be parsed.