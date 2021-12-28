"""
Script to clean the HTML files

TODO
- make a list of just the xjpg image sources
- check for missing audio

"""
import html5lib
import glob
import os
import csv
import re
import shutil
import zipfile
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup


def compile_images_on_disk_list(image_dir: Path = ""):
    # Make a list of all the image files we have for all languages
    images_on_disk = []
    images_on_disk_paths = image_dir.glob("**/*.jpg")
    for images_on_disk_path in images_on_disk_paths:
        images_on_disk.append(images_on_disk_path.name.lower())
    return(images_on_disk)


def compile_audio_on_disk_list(audio_dir: Path = ""):
    # Make a list of all the audio files we have for this language
    audio_on_disk = []
    audio_on_disk_paths = audio_dir.glob("**/*.mp3")
    for audio_on_disk_path in audio_on_disk_paths:
        audio_on_disk.append(audio_on_disk_path.name.lower())
    return(audio_on_disk)


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


def get_template(template_path: str) -> BeautifulSoup:
    with Path(template_path).open("r") as template_file:
        return BeautifulSoup(template_file, "html5lib")


def make_domain_readable(domain: str) -> str:
    pattern = r"^[a-z]-(.*)"
    replacemenet = lambda m: m.group(1).replace("-", " ").title()
    return re.sub(pattern, replacemenet, domain)


def write_missing_report(type: str = "", language: str = "", missing: List[List[str]] = None):
    print("*** write_missing_report")
    csv_path = Path(f"../reports/{language}-{type}-report.csv")
    with csv_path.open("a", newline='') as csvfile:
        headers = ["Language", "Entry", "Src", "Domain"]
        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
        if csvfile.tell() == 0:
            print("*** write headers")
            writer.writeheader()
        for entry, src, domain in missing:
            writer.writerow({"Language": language,
                             "Entry": entry,
                             "Src": src,
                             "Domain": domain})


def process_domain(language: List[str],
                   html_path: Path,
                   menu_tag: str,
                   images_on_disk: List[str],
                   audio_on_disk: List[str]
                   ):
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

        # Try correcting some simple image name problems
        image_pattern = ".xjpg"
        image_replacement = ".jpg"
        html = re.sub(image_pattern, image_replacement, html)

        # Add a named anchor for english to language page linking
        anchor_pattern = r'<div class=\"wsumarcs-entry\" id=\"wsumarcs-([a-z]+)\">'
        anchor_replacement = r'<a id="\1"></a><div class="wsumarcs-entry" id="\1">'
        html = re.sub(anchor_pattern, anchor_replacement, html, flags=re.IGNORECASE)

        # Change english file link URLs
        url_pattern = r'/view.php\?domain=([ a-z\(\)]+)\&amp;hash=[\w]+'
        url_replacement = lambda m: "../" + m.group(1).lower().replace(" ", "-") + "/index.html"
        html = re.sub(url_pattern, url_replacement, html, flags=re.IGNORECASE)

        # Make a soup tag for the fixed content
        content_soup = BeautifulSoup(html, "html.parser")

        # Use BeautifulSoup to check for missing images, and generate a report
        entries = []
        missing = []
        images = [image for image in content_soup.select(".wsumarcs-entry img.wsumarcs-comPic")]
        for image in images:
            # Force src to lowercase, this also must happen in the flatten media script
            image["src"] = image["src"].replace(" ", "_").lower()
            img_name = image["src"].replace("../_img/", "")
            # Compile list of images and entry info
            entry = image.find_parent("div")
            entry_id = entry["id"]
            entries.append([entry_id, img_name, domain_dir])

            if img_name not in images_on_disk:
                print(f". . . missing image {img_name}")
                image.decompose()
                missing.append([entry_id, img_name, domain_dir])
        missing = sorted(missing, key=lambda x: x[0].lower())
        write_missing_report(type = "images", language = language[0], missing = missing)

        # Use BeautifulSoup to check for missing audio, and generate a report
        entries = []
        missing = []
        audios = [audio for audio in content_soup.select(".wsumarcs-entry img.wsumarcs-entrySfx")]
        for audio in audios:
            audio["data-file"] = audio["data-file"].replace(" ", "_").lower()
            audio_name = audio["data-file"].replace("../_audio/", "")
            entry = audio.find_parent("div")
            entry_id = entry["id"]
            entries.append([entry_id, audio_name, domain_dir])
            if audio_name not in audio_on_disk:
                print(f". . . missing audio {audio_name}")
                audio.decompose()
                missing.append([entry_id, audio_name, domain_dir])
        missing = sorted(missing, key=lambda x: x[0].lower())
        write_missing_report(type = "audio", language = language[0], missing = missing)

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
        article_tag.append(content_soup)

        # Save the html
        output_path = Path(f"../output/{language[0]}/{domain_dir}")
        output_path.mkdir(parents=True, exist_ok=True)

        with output_path.joinpath("index.html").open("w") as html_output_file:
            html_output_file.write(template_soup.prettify())


def build_index_file(language: List[str], domains: List[str]):

    # Slurp in the home page content
    with Path(f"../content/{language[0]}/home.html").open("r") as content_file:
        content_soup = BeautifulSoup(content_file, "html.parser")

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
    article_tag.append(content_soup)

    # Write the index file
    with Path(f"../output/{language[0]}/index.html").open("w") as index_file:
        index_file.write(template_soup.prettify())


def iterate_htmls(language: List[str],
                  domains: List[str],
                  images_on_disk: List[str],
                  audio_on_disk: List[str]
                  ):
    # Build the menu for the content pages - they will have different path ../ vs ./ for index page
    menu_tag = build_menu(domains=domains, is_index=False)
    # Build each domain page
    html_paths = Path("../tmp").glob("**/*.html")
    for html_path in html_paths:
        process_domain(language=language,
                       html_path=html_path,
                       menu_tag=menu_tag,
                       images_on_disk=images_on_disk,
                       audio_on_disk=audio_on_disk)


def main():
    """
    Before running this script, do the flatten_media_dir one
    """

    debug = True

    if debug:
        languages = [["test", "Test"]]
    else:
        languages = [
            ["bilinarra", "Bilinarra"],
            ["gurindji", "Gurindji"],
            ["mudburra", "Mudburra"],
            ["ngarinyman", "Ngarinyman"]
        ]
    # Images from the media folder have been flattened, combining all images into one dir
    images_on_disk = compile_images_on_disk_list(image_dir=Path(f"../all_images/"))

    if Path("../reports").is_dir():
        shutil.rmtree("../reports")
    Path("../reports/images").mkdir(parents=True, exist_ok=True)
    Path("../reports/audio").mkdir(parents=True, exist_ok=True)

    for language in languages:
        print(f"**** Doing {language[1]} ****")

        # Audio has been flattened from the media dir into separate audio folders per language
        audio_on_disk = compile_audio_on_disk_list(audio_dir=Path(f"../all_audio/{language[0]}/_audio"))

        # Reset tmp and reports dirs
        if Path("../tmp").is_dir():
            shutil.rmtree("../tmp")

        # Create output dir and copy assets from the template
        output_dir = Path(f"../output/{language[0]}")
        shutil.copytree("../template/_assets", output_dir.joinpath("_assets"), dirs_exist_ok=True)

        # Copy the feature image from the content folder
        shutil.copy(f"../content/{language[0]}/feature.jpg", output_dir.joinpath("_assets"))

        # Create media dirs and fill with content that has been flattened
        shutil.copytree("../all_images/_img_sm", output_dir.joinpath("_img"), dirs_exist_ok=True)
        shutil.copytree(f"../all_audio/{language[0]}/_audio", output_dir.joinpath("_audio"), dirs_exist_ok=True)

        # Prepare the domain zips
        zip_path = Path(f"../content/{language[0]}/zips")
        print(f"zip_path {zip_path}")
        domains = unzip_archives(zip_path=zip_path)

        # Now build the html pages
        print("==== Build index file ====")
        build_index_file(language=language, domains=domains)
        print("==== Iterate htmls ====")
        iterate_htmls(language=language, domains=domains, images_on_disk=images_on_disk, audio_on_disk=audio_on_disk)
        print("done\n\n")


if __name__ == "__main__":
    main()
