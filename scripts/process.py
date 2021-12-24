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
    script_tag.attrs["src"] = "../_assets/script.js"
    soup.head.insert(1, script_tag)

    # Insert new stylesheet link
    stylesheet_tag = soup.new_tag("link")
    stylesheet_tag.attrs["rel"] = "stylesheet"
    stylesheet_tag.attrs["href"] = "../_assets/styles.css"
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
    audio_player_replacement = "../_img/audio.png"
    pretty_html = re.sub(audio_player_pattern, audio_player_replacement, pretty_html)

    # Fix audio player icons
    audio_pattern = r'data-file="img/'
    audio_replacement = r'data-file="../_audio/'
    pretty_html = re.sub(audio_pattern, audio_replacement, pretty_html)

    # Change img src path
    image_pattern = r'src="img/'
    image_replacement = r'src="../_img/'
    pretty_html = re.sub(image_pattern, image_replacement, pretty_html)

    # Add a named anchor
    anchor_pattern = r'<div class=\"wsumarcs-entry\" id=\"wsumarcs-([a-z]+)\">'
    anchor_replacement = r'<a id="\1"></a><div class="wsumarcs-entry" id="\1">'
    pretty_html = re.sub(anchor_pattern, anchor_replacement, pretty_html, flags=re.IGNORECASE)

    # Change english file link URLs
    # Expects the domain-english dir to be sibling to domain dir
    # TODO may need to change this to suit subdir deployment on the server?
    url_pattern = r'/view.php\?domain=([ a-z]+)\&amp;hash=[\w]+'
    url_replacement = lambda m: "../" + m.group(1).lower().replace(" ", "-") + "/index.html"
    pretty_html = re.sub(url_pattern, url_replacement, pretty_html, flags=re.IGNORECASE)

    # Save the html
    output_path = Path(f"../bilinarra-output/{domain_dir}")
    output_path.mkdir(parents=True, exist_ok=True)

    with output_path.joinpath("index.html").open("w") as html_output_file:
        html_output_file.write(pretty_html)


def unzip_archives():
    domains = []
    zip_paths = Path("../bilinarra-zips").glob("**/*.zip")
    for zip_path in zip_paths:
        domain = zip_path.stem

        domains.append(domain.replace("-english", ""))
        domains_unique = list(set(domains))
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(f"../tmp/{domain}")
    domains_unique.sort()
    return domains_unique


def build_menu(domains: List = [], is_index: bool = False):
    subdir = "./" if is_index else "../"
    menu_soup = BeautifulSoup("<div id='menu'></div>", "html5lib")
    menu_tag = menu_soup.div

    home_group_tag = menu_soup.new_tag('li')
    home_tag = menu_soup.new_tag("a", href=subdir)
    home_tag.string = "Home"
    home_group_tag.append(home_tag)
    menu_tag.append(home_group_tag)

    for domain in domains:
        link_group_tag = menu_soup.new_tag('li')
        link_tag = menu_soup.new_tag("a", href=f"{subdir}{domain}/")
        link_tag.string = make_domain_readable(domain)

        seperator_tag = menu_soup.new_tag("span")
        seperator_tag.string = " | "

        english_link_tag = menu_soup.new_tag("a", href=f"{subdir}{domain}-english/")
        english_link_tag.string = "English"

        link_group_tag.append(link_tag)
        link_group_tag.append(seperator_tag)
        link_group_tag.append(english_link_tag)
        menu_tag.append(link_group_tag)
    return menu_tag


def iterate_htmls(menu_tag: str):
    html_paths = Path("../tmp").glob("**/*.html")
    for html_path in html_paths:
        domain_dir = html_path.parts[-2]
        with open(html_path) as html_file:
            print(html_path)
            soup = BeautifulSoup(html_file, "html5lib")
            process_domain(domain_dir, soup, menu_tag)

def build_index_file(domains):
    menu_tag = build_menu(domains=domains, is_index=True)
    index_path = Path("../bilinarra-output/index.html")
    soup = BeautifulSoup("", "html5lib")

    # Set the page class so CSS can style the home page a little differently
    body = soup.find("body")
    body.attrs["id"] = "home"

    meta_tag = soup.new_tag("meta")
    meta_tag.attrs["charset"] = "UTF-8"
    soup.head.insert(0, meta_tag)

    # Add page title
    title_tag = soup.new_tag("title")
    title_tag.string = "Dictionary"
    soup.head.insert(0, title_tag)

    # Add styles
    stylesheet_tag = soup.new_tag("link")
    stylesheet_tag.attrs["rel"] = "stylesheet"
    stylesheet_tag.attrs["href"] = "_assets/styles.css"
    soup.head.insert(1, stylesheet_tag)

    # Add a page header
    header_tag = soup.new_tag("header")
    title_tag = soup.new_tag("h1")
    title_tag.string = "REPLACE LANGUAGE NAME"
    header_tag.append(title_tag)
    soup.body.insert(0, header_tag)

    # Add page text
    section_tag = soup.new_tag("section")
    content_tag = soup.new_tag("p")
    content_tag.string = "REPLACE CONTENT"
    section_tag.append(content_tag)
    soup.body.insert(1, section_tag)

    # Add the menu
    soup.body.insert(2, menu_tag)

    # Write the index file
    with index_path.open("w") as index_file:
        index_file.write(soup.prettify())


if __name__ == "__main__":
    domains = unzip_archives()
    build_index_file(domains=domains)
    menu_tag = build_menu(domains=domains)
    iterate_htmls(menu_tag)
    print("done")
