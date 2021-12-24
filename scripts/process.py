"""
Script to clean the HTML files
"""
import html5lib
import glob
from pathlib import Path
import re
from bs4 import BeautifulSoup


def main(domain_dir: str, soup: BeautifulSoup):
    # Strip script and style tags
    [x.extract() for x in soup.findAll(['script', 'style'])]

    # Insert jQuery script link
    jquery_tag = soup.new_tag("script")
    jquery_tag.attrs["src"] = "http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"
    soup.head.insert(0, jquery_tag)

    # Insert the dictionary script
    # note that this is just the audio player code, not the hash href code
    script_tag = soup.new_tag("script")
    script_tag.attrs["src"] = "../script.js"
    soup.head.insert(1, script_tag)

    # Insert new stylesheet link
    stylesheet_tag = soup.new_tag("link")
    stylesheet_tag.attrs["rel"] = "stylesheet"
    stylesheet_tag.attrs["href"] = "../styles.css"
    soup.head.insert(2, stylesheet_tag)

    # Make it look nice (also makes it a str for regex)
    pretty_html = soup.prettify()

    # Fix audio dir in player icons
    audio_pattern = 'data-file="img/'
    audio_replacement = 'data-file="../audio/'
    pretty_html = re.sub(audio_pattern, audio_replacement, pretty_html)

    # Add a named anchor
    anchor_pattern = r'<div class=\"wsumarcs-entry\" id=\"wsumarcs-([a-z]+)\">'
    anchor_replacement = r'<a name="$1"></a><div class="wsumarcs-entry" id="\1">'
    pretty_html = re.sub(anchor_pattern, anchor_replacement, pretty_html)

    # Change english file link URLs
    # Expects the domain-english dir to be sibling to domain dir
    # TODO may need to change this to suit subdir deployment on the server?
    url_pattern = r'/view.php\?domain=([ a-z]+)\&amp;hash=[\w]+'
    url_replacement = lambda m: "../" + m.group(1).lower().replace(" ", "-") + "/index.html"
    pretty_html = re.sub(url_pattern, url_replacement, pretty_html, flags=re.IGNORECASE)

    # Save the html
    output_path = Path(f"../test/{domain_dir}")
    output_path.mkdir(parents=True, exist_ok=True)

    with output_path.joinpath("index.html").open("w") as html_output_file:
        html_output_file.write(pretty_html)


if __name__ == "__main__":
    html_paths = Path('../source').glob('**/*.html')
    for html_path in html_paths:
        # get the subdir that the html file is in. This should be the domain and english version
        domain_dir = html_path.parts[-2]
        with open(html_path) as html_file:
            soup = BeautifulSoup(html_file, 'html5lib')
            main(domain_dir, soup)
