"""
Script to clean the HTML files
"""
import html5lib
import glob
import os
from pathlib import Path
import re
import zipfile
from typing import List

from bs4 import BeautifulSoup


def make_domain_readable(domain: str) -> str:
    pattern = r"^[a-z]-(.*)"
    replacemenet = lambda m: m.group(1).replace("-", " ").title()
    return re.sub(pattern, replacemenet, domain)


def process_domain(domain_dir: str, soup: BeautifulSoup, menu_tag: str):
    # Strip script and style tags
    [x.extract() for x in soup.findAll(['script', 'style'])]

    # Insert jQuery script link
    jquery_tag = soup.new_tag("script")
    jquery_tag.attrs["src"] = "https://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"
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

    # Insert the menu
    soup.body.insert(0, menu_tag)

    # Add a page header
    header_tag = soup.new_tag("header")
    title_tag = soup.new_tag("h1")
    title_tag.string = make_domain_readable(domain_dir)
    header_tag.append(title_tag)
    soup.body.insert(1, header_tag)

    # Make it look nice (also makes it a str for regex)
    pretty_html = soup.prettify()

    # Remove weird big dot
    dot_pattern = '''<span style="font-size:0.5em;position:relative;bottom:3px;">
     ⚫
    </span>'''
    pretty_html = re.sub(dot_pattern, '', pretty_html)


    # Fix audio dir in player icons
    audio_player_pattern = "img/audio.png"
    audio_player_replacement = "../img/audio.png"
    pretty_html = re.sub(audio_player_pattern, audio_player_replacement, pretty_html)

    # Fix audio player icons
    audio_pattern = 'data-file="img/'
    audio_replacement = 'data-file="../audio/'
    pretty_html = re.sub(audio_pattern, audio_replacement, pretty_html)

    # Add a named anchor
    anchor_pattern = r'<div class=\"wsumarcs-entry\" id=\"wsumarcs-([a-z]+)\">'
    anchor_replacement = r'<a id="\1"></a><div class="wsumarcs-entry" id="\1">'
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


def unzip_archives():
    domains = []
    zip_paths = Path("../zips").glob("**/*.zip")
    for zip_path in zip_paths:
        domain = zip_path.stem

        domains.append(domain.replace("-english", ""))
        domains_unique = list(set(domains))
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(f"../source/{domain}")
    domains_unique.sort()
    return domains_unique


def build_menu(domains: List):
    menu_soup = BeautifulSoup("<div id='menu'></div>", "html5lib")
    menu_tag = menu_soup.div

    for domain in domains:
        link_group_tag = menu_soup.new_tag('li')
        link_tag = menu_soup.new_tag("a", href=f"../{domain}/")
        link_tag.string = make_domain_readable(domain)

        seperator_tag = menu_soup.new_tag("span")
        seperator_tag.string = " | "

        english_link_tag = menu_soup.new_tag("a", href=f"../{domain}-english/")
        english_link_tag.string = "English"

        link_group_tag.append(link_tag)
        link_group_tag.append(seperator_tag)
        link_group_tag.append(english_link_tag)
        menu_tag.append(link_group_tag)

    return menu_tag


def iterate_htmls(menu_tag: str):
    html_paths = Path("../source").glob("**/*.html")
    for html_path in html_paths:
        domain_dir = html_path.parts[-2]
        with open(html_path) as html_file:
            print(html_path)
            soup = BeautifulSoup(html_file, "html5lib")
            process_domain(domain_dir, soup, menu_tag)


if __name__ == "__main__":
    domains_unique = unzip_archives()
    menu_tag = build_menu(domains_unique)
    iterate_htmls(menu_tag)
    print("done")
