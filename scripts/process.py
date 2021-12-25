"""
Script to clean the HTML files
"""
import html5lib
import glob
import os
import re
import shutil
import zipfile
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup


def make_domain_readable(domain: str) -> str:
    pattern = r"^[a-z]-(.*)"
    replacemenet = lambda m: m.group(1).replace("-", " ").title()
    return re.sub(pattern, replacemenet, domain)


def process_domain(language: List[str], html_path: str, menu_tag: str):
    domain_dir = html_path.parts[-2]
    print(domain_dir)
    with open(html_path) as html_file:
        # This is the wordspinner generated content. It needs to be cleaned
        content_soup = BeautifulSoup(html_file, "html.parser")

        # Strip script and style tags
        [x.extract() for x in content_soup.findAll(['script', 'style'])]

        # Remove weird big dot
        dot_pattern = '<span style="font-size:0.5em;position:relative;bottom:3px;">⚫</span>'
        html = re.sub(dot_pattern, '<br />', str(content_soup))

        # Fix audio dir in player icons
        audio_player_pattern = "img/audio.png"
        audio_player_replacement = "../_assets/audio.png"
        html = re.sub(audio_player_pattern, audio_player_replacement, html)

        # Fix audio player icons
        audio_pattern = r'data-file="img/'
        audio_replacement = r'data-file="../_audio/'
        html = re.sub(audio_pattern, audio_replacement, html)

        # Change img src path
        image_pattern = r'src="img/'
        image_replacement = r'src="../_img/'
        html = re.sub(image_pattern, image_replacement, html)

        # Add a named anchor for english to language page linking
        anchor_pattern = r'<div class=\"wsumarcs-entry\" id=\"wsumarcs-([a-z]+)\">'
        anchor_replacement = r'<a id="\1"></a><div class="wsumarcs-entry" id="\1">'
        html = re.sub(anchor_pattern, anchor_replacement, html, flags=re.IGNORECASE)

        # Change english file link URLs
        # TODO may need to change this to suit subdir deployment on the server?
        url_pattern = r'/view.php\?domain=([ a-z]+)\&amp;hash=[\w]+'
        url_replacement = lambda m: "../" + m.group(1).lower().replace(" ", "-") + "/index.html"
        html = re.sub(url_pattern, url_replacement, html, flags=re.IGNORECASE)

        # Make a soup tag for the fixed content
        content_tag = BeautifulSoup(html, "html.parser")

        # Get the page template
        template_soup = get_template(template_path = "../template/content.html")

        # Change the page title
        article_tag = template_soup.find("title")
        article_tag.string = f"{language[1]} dictionary | {make_domain_readable(domain_dir)}"

        # Insert the menu
        nav_tag = template_soup.find("nav")
        nav_tag.append(menu_tag)

        # Change the page header
        header_tag = template_soup.find("header")
        header_tag.string = make_domain_readable(domain_dir)

        # Insert the content
        article_tag = template_soup.find("article")
        article_tag.string = ""
        article_tag.append(content_tag)

        # Save the html
        output_path = Path(f"../output/{language[0]}/{domain_dir}")
        output_path.mkdir(parents=True, exist_ok=True)

        with output_path.joinpath("index.html").open("w") as html_output_file:
            html_output_file.write(template_soup.prettify())


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


def build_index_file(language: List[str], domains: List[str]):

    # Slurp in the home page content
    with Path(f"../content/{language[0]}/home.html").open("r") as content_file:
        content_tag = BeautifulSoup(content_file, "html.parser")

    # Build the menu for the index page - it will have different path ./ vs ../ for content pages
    menu_tag = build_menu(domains=domains, is_index=True)

    # Build the page
    template_soup = get_template(template_path = "../template/index.html")

    # Add page title
    title_tag = template_soup.find("title")
    title_tag.string = f"{language[1]} dictionary"

    # Change the page header
    header_tag = template_soup.find("header")
    header_tag.string = f"{language[1]} dictionary"

    # Insert the menu
    nav_tag = template_soup.find("nav")
    nav_tag.append(menu_tag)

    # Insert the content
    article_tag = template_soup.find("article")
    article_tag.string = ""
    article_tag.append(content_tag)

    # Write the index file
    with Path(f"../output/{language[0]}/index.html").open("w") as index_file:
        index_file.write(template_soup.prettify())


def build_menu(domains: List, is_index: bool = False):
    subdir = "./" if is_index else "../"
    menu_soup = BeautifulSoup("<ul id='menu'></ul>", "html5lib")
    menu_tag = menu_soup.ul

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


def iterate_htmls(language: List[str], domains: List[str]):
    # Build the menu for the content pages - they will have different path ../ vs ./ for index page
    menu_tag = build_menu(domains=domains, is_index=False)
    # Build each domain page
    html_paths = Path("../tmp").glob("**/*.html")
    for html_path in html_paths:
        process_domain(language, html_path, menu_tag)


def get_template(template_path: str) -> BeautifulSoup:
    with Path(template_path).open("r") as template_file:
        return BeautifulSoup(template_file, "html5lib")


if __name__ == "__main__":
    # Language first element should match zip and output dirs eg gurindji-zip gurindji-output
    # Second element is human-readable version
    language = ["test", "Test"]

    # Create output dir and copy assets from the template
    output_dir = Path(f"../output/{language[0]}")
    shutil.copytree("../template/_assets", output_dir.joinpath("_assets"), dirs_exist_ok=True)

    # Copy the feature image from the content folder
    shutil.copy(f"../content/{language[0]}/feature.jpg", output_dir.joinpath("_assets"))

    # Create media dirs but they will need to be manually filled
    output_dir.joinpath("_img").mkdir(parents=True, exist_ok=True)
    output_dir.joinpath("_audio").mkdir(parents=True, exist_ok=True)

    # Prepare the domain zips
    zip_path = Path(f"../content/{language[0]}/zips")
    domains = unzip_archives(zip_path=zip_path)

    # Now build the html pages
    build_index_file(language=language, domains=domains)
    iterate_htmls(language=language, domains=domains)
    print("done")
