from typing import Iterator
import argformat
import argparse
import hashlib
import pandas as pd
import re
import sqlite3
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

################################################################################
#                                Parse methods                                 #
################################################################################

def parse(html: str, netloc: str) -> str:
    """Parse given html based on netloc parser.
    
        Parameters
        ----------
        html : str
            HTML to parse.
            
        netloc : str
            Network location of file origin.
            
        Returns
        -------
        text : str
            Text extracted from html file.
        """
    if netloc == 'blog.malwarebytes.com':
        text = parse_malwarebytes(html)
    elif netloc == 'blog.sucuri.net':
        text = parse_sucuri(html)
    elif netloc == 'blog.trendmicro.com':
        text = parse_trendmicro(html)
    elif netloc == 'blogs.forcepoint.com':
        text = parse_forcepoint(html)
    elif netloc == 'blogs.sophos.com':
        text = parse_sophos(html)
    elif netloc == 'news.sophos.com':
        text = parse_sophos(html)
    elif netloc == 'taosecurity.blogspot.com':
        text = parse_taosecurity(html)
    elif netloc == 'www.hexacorn.com':
        text = parse_hexacorn(html)
    elif netloc == 'www.infosecblog.org':
        text = parse_infosecblog(html)
    elif netloc == 'www.virusbulletin.com':
        text = parse_virusbulletin(html)
    elif netloc == 'www.webroot.com':
        text = parse_webroot(html)
    elif netloc == 'www.welivesecurity.com':
        text = parse_welivesecurity(html)
    else:
        raise ValueError(f"Unsupported netloc: '{netloc}'")

    # Replace multiple whitespace lines
    regex_whitespace = re.compile(r'\n\s*\n', )
    text = regex_whitespace.sub('\n\n', text).strip() + '\n'

    # Strip all lines
    text = '\n'.join(line.strip() for line in text.split('\n'))

    # Return result
    return text

def parse_trendmicro(html: str) -> str:
    """Parse HTML page from trendmicro."""
    raise NotImplementedError("No parser implemented for trendmicro.")


def parse_hexacorn(html: str) -> str:
    """Parse HTML page from hexacorn."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Get post content
    post = html.find_all("div", class_ = "post-content")

    # Assert we only find a single post
    assert len(post) == 1, f"Number of found posts was: '{len(post)}'"

    # Extract post text and return
    return post[0].get_text()


def parse_welivesecurity(html: str) -> str:
    """Parse HTML page from hexacorn."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Get promo content
    promo = html.find_all("div", class_ = "promo-text")
    # Assert we only find a single promo text
    assert len(promo) == 1, f"Number of found promos was: '{len(promo)}'"

    # Get promo text
    text = [promo[0].get_text()]

    # Get article content
    article = html.find_all("div", class_ = "col-md-10 col-sm-10 col-xs-12 formatted")
    # Assert we only find a single article text
    assert len(article) == 1, f"Number of found articles was: '{len(article)}'"
    
    # Iterate over children
    for child in article[0].children:
        # Break on dot tag
        if isinstance(child, Tag):
            # Check if child contains any class with dot tag
            if 'dot' in child.get('class', []) or len(child.find_all('div', class_='dot')):
                break
            # Check if child contains any class with widgets tag
            if 'widgets' in child.get('class', []) or len(child.find_all('div', class_='widgets')):
                break
        
        # Add text contents
        text.append(child.get_text())
    else:
        raise ValueError("Could not find <dot> tag")

    # Return text
    return '\n'.join(text)


def parse_malwarebytes(html: str) -> str:
    """Parse HTML page from malwarebytes."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Get title content
    title = html.find_all("h1", class_ = "entry-title")
    # Assert we only find a single title text
    assert len(title) == 1, f"Number of found titles was: '{len(title)}'"

    # Get article content
    article = html.find_all("div", id="articleBody")
    # Assert we only find a single article text
    if len(article) != 1:
        # Only case for: https://blog.malwarebytes.com/security-world/2018/01/meltdown-and-spectre-what-you-need-to-know/
        # Turns out not to be a problem, we are still looking for article[0]
        print(f"Warning: number of found articles was: '{len(article)}'")

    # Initialise text
    text = title[0].get_text()

    article = article[0]
    related = article.find_all('div', id='jp-relatedposts')
    # Assert we only find a single related text
    assert len(related) == 1, f"Number of found related was: '{len(related)}'"
    related[0].decompose()

    text += '\n'
    text += article.get_text()

    # Get text
    return text


def parse_sucuri(html: str) -> str:
    """Parse HTML page from sucuri."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Get title content
    titles   = html.find_all("h1", class_ = "entry-title")
    contents = html.find_all("div", class_="entry-content")

    # Check for same number of titles and contents
    assert len(titles) == len(contents), (
        f"Different number of titles ('{len(titles)}') and contents "
        f"('{len(contents)}') found."
    )

    if len(titles) != 1:
        print(f"Warning: {len(titles)} posts found in single page.")

    # Special case: https://blog.sucuri.net/2019/01/owasp-top-10-security-risks-part-iv.html
    if len(titles) == 0:
        # Get titles
        titles   = html.find_all("h1", class_="mb-30 green")
        contents = html.find_all("div", id="step0")

        # Assert titles and contents are of length 1
        assert len(titles) == len(contents) == 1, "Special case failed."

        # Loop over children
        to_remove = list()
        for child in contents[0].find_all('div', class_='c-lg-12'):
            if 'step' not in child.get('id', ''):
                to_remove.append(child)
                
        for child in to_remove:
            child.decompose()
        

    # Initialise result
    result = list()

    # Loop over titles and contents
    for title, content in zip(titles, contents):
        
        # Remove aside
        for aside in content.find_all('aside'):
            aside.decompose()

        result.append(title.get_text() + '\n' + content.get_text())

    # Return text
    return '\n\n'.join(result)


def parse_forcepoint(html: str) -> str:
    """Parse HTML page from forcepoint."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Initialise result
    result = list()

    # Get title
    title = html.find_all("h1")
    if len(title) != 1:
        print(f"Warning: Multiple titles found: '{len(title)}': {title}")
    result.append(title[0].get_text())

    # Get summary
    summary = html.find_all("div", class_="pane-node-field-blog-summary")
    assert len(summary) <= 1, f"Multiple summaries found: '{len(summary)}'"
    if len(summary):
        result.append(summary[0].get_text())


    content = html.find_all("div", class_="pane-node-field-main-content")
    assert len(content) == 1, f"Multiple contents found: '{len(content)}'"
    result.append(content[0].get_text())

    # Return text
    return '\n'.join(result)


def parse_sophos(html: str) -> str:
    """Parse HTML page from sophos."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Retrieve main
    main = html.find_all("main", id="main")
    assert len(main) == 1, f"Multiple mains found: {len(main)}"

    # Get article childs of main
    article = None
    for child in main[0].children:
        if isinstance(child, Tag) and child.name == "article":
            assert article is None, "Multiple articles found"
            article = child

    # Return text
    return article.get_text()


def parse_taosecurity(html: str) -> str:
    """Parse HTML page from taosecurity."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Get post
    post = html.find_all("div", class_="post")
    assert len(post) == 1, f"Multiple posts found: {len(post)}"
    post = post[0]

    # Remove post bottom
    to_remove = list()
    for bottom in post.find_all('div', class_="post-bottom"):
        to_remove.append(bottom)
    assert len(to_remove) == 1, "Multiple items to remove"
    for child in to_remove:
        child.decompose()

    # Return text
    return post.get_text()


def parse_infosecblog(html: str) -> str:
    """Parse HTML page from infosecblog."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Get article
    article = html.find_all("article", class_="post")
    assert len(article) == 1, f"Multiple articles found: {len(article)}"
    article = article[0]

    # Remove footer from article
    article.footer.decompose()

    # Return text
    return article.get_text()


def parse_virusbulletin(html: str) -> str:
    """Parse HTML page from virusbulletin."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Get titlepage
    main = html.find_all("div", class_="col-md-9")
    assert len(main) == 1, f"Multiple main found: {len(main)}"
    main = main[0]

    # Return text
    return "\n".join(traverse_virusbulletin(main))


def parse_webroot(html: str) -> str:
    """Parse HTML page from webroot."""
    # Transform into beautifulsoup
    html = BeautifulSoup(html, 'html.parser')

    # Get title
    title = html.find_all("h1", class_="entry-title")
    assert len(title) == 1, f"Multiple title found: {len(title)}"
    title = title[0]

    # Get content
    content = html.find_all("div", class_="entry-content")
    assert len(content) == 1, f"Multiple content found: {len(content)}"
    content = content[0]

    children = list(filter(lambda x: isinstance(x, Tag), content.children))
    assert len(children) == 1, f"Multiple children found: {len(children)}"
    content = children[0]

    # Remove bio and social
    to_remove = list()
    for child in content.find_all('div', id='singleBios'):
        to_remove.append(child)
    assert len(to_remove) == 1, f"Could not remove single bio: {len(to_remove)}"

    for child in content.find_all('div', class_="et_social_inline"):
        to_remove.append(child)
    assert len(to_remove) == 3, f"Could not remove single bio: {len(to_remove)}"

    for child in to_remove:
        child.decompose()

    # Return content text
    return content.get_text()

################################################################################
#                             Auxiliary functions                              #
################################################################################

def traverse_virusbulletin(html: Tag) -> Iterator[str]:
    """Iterate over text in virusbulletin HTML pages."""
    if isinstance(html, NavigableString):
        yield str(html.string)
    elif html.name.lower() in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        yield '\n' + html.get_text()
    elif html.name.lower() in {"p"}:
        yield html.get_text()
    elif "ccm-remo-expand" in html.get("class", []):
        yield ""
    else:
        for child in html.children:
            yield from traverse_virusbulletin(child)

################################################################################
#                                     Main                                     #
################################################################################

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description     = 'Parse raw html files to text files',
        formatter_class = argformat.StructuredFormatter,
    )

    # Optional arguments
    parser.add_argument('--database', default='release.db', help='path to ChainSmith database')
    parser.add_argument('--indir'   , default=Path(__file__).absolute().parent / 'html', help='path to html   directory')
    parser.add_argument('--outdir'  , default=Path(__file__).absolute().parent / 'text', help='path to output directory')
    
    # Parse arguments
    args = parser.parse_args()

    # Get input and output dir
    indir  = Path(args.indir)
    outdir = Path(args.outdir)

    # Open connection with databbase
    with sqlite3.connect(args.database) as connection:
        # Read data into dataframe
        df = pd.read_sql_query("SELECT * FROM iocs", connection)

    # Get list of urls
    urls = set(map(str, df['url'].values))

    # Download data
    for url in tqdm(sorted(urls), desc='Collecting'):
        # Get base url
        netloc = urlparse(url).netloc

        # Get hash of url
        hash = hashlib.sha256(url.encode('utf-8')).hexdigest()

        # Trendmicro blogs have been moved
        if 'trendmicro' in netloc: continue
        # These were not found
        if hash == "35f952d37df3edb7c2805a0637eb8e1fbb399dd9af2c80d0371a0716df8e9780": continue
        if hash == "51fcfb6f7096eec3f93edbe8221c6b040c173536315f93cbde95c30f9908143c": continue
        if hash == "6cdc11ee428afb5cd289f02a4a0982defe7797882b82840acd8666c93d334489": continue
        if hash == "231f863f7981bbfd8974cd429304a012f30253ffb092b649085bfbc9e0c2dd4f": continue
        if hash == "5b683739759cc0cfa97777fd4cb803709250a185d4ad8ff8bb95236bfa139961": continue
        if hash == "25db01a13649c5968718bf1c4e2d38db310fce7e0557d6a8304b3ffc821791f2": continue
        if hash == "95ee57b6e881a87b075401b22c8cc7c734a64597f2ee8ca5074c9e51f8765ff9": continue

        # Read data from file
        with open(indir / hash) as infile:
            html = infile.read()

        # Parse data
        try:
            text = parse(html, netloc)
        except Exception as e:
            print(hash)
            print(url)
            raise e

        # Write text to output file
        with open(outdir / hash, 'w') as outfile:
            outfile.write(text)

if __name__ == '__main__':
    main()