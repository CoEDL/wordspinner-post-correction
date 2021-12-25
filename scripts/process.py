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

    # # Insert the menu
    # soup.body.insert(0, menu_tag)
    # 
    # # Add a page header
    # title_tag = soup.new_tag("h1")
    # title_tag.string = make_domain_readable(domain_dir)
    # soup.body.insert(1, title_tag)

    # Save the html
    output_path = Path(f"../test-output/{domain_dir}")
    output_path.mkdir(parents=True, exist_ok=True)


    with output_path.joinpath("index.html").open("w") as html_output_file:
        html_output_file.write(pretty_html)


def unzip_archives(zip_path: Path = None):
    domains = []
    zip_paths = zip_path.glob("**/*.zip")
    for zip_path in zip_paths:
        domain = zip_path.stem

        domains.append(domain.replace("-english", ""))
        domains = list(set(domains))
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(f"../tmp/{domain}")
    domains.sort()
    return domains


def build_index_file(language: str, domains: List[str]):
    menu_tag = build_menu(domains=domains, is_index=True)
    # Open the index template
    with Path("../html_template/index.html").open("r") as template_file:
        soup = BeautifulSoup(template_file, "html5lib")
        print(str(soup))
        # Set the page class so CSS can style the home page a little differently
        # body = soup.find("body")
        # body.attrs["id"] = "home"
        #
        # # Add page title
        # title_tag = soup.new_tag("title")
        # title_tag.string = "TEST Dictionary"
        # soup.head.insert(0, title_tag)
        #
        # # Write the index file
        # with Path("../test-output/index.html").open("w") as index_file:
        #     index_file.write(soup.prettify())

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


if __name__ == "__main__":
    #  language should make zip and output dirs eg gurindji-zip gurindji-output
    language = "test"
    zip_path = Path(f"../{language}-zips")
    domains = unzip_archives(zip_path=zip_path)
    build_index_file(language=language, domains=domains)
    # menu_tag = build_menu(domains=domains)
    # iterate_htmls(menu_tag)
    print("done")
