"""
Script to rebuild the HTML files
"""
from pathlib import Path
from typing import List
import csv
import html5lib
import re
import shutil
import zipfile
from bs4 import BeautifulSoup
from jinja2 import Template


def compile_images_on_disk_list(image_dir: Path = ""):
    # Make a list of all the image files we have for all languages
    images_on_disk = []
    images_on_disk_paths = image_dir.glob("**/*.jpg")
    for images_on_disk_path in images_on_disk_paths:
        images_on_disk.append(images_on_disk_path.name.lower())
    return images_on_disk


def compile_audio_on_disk_list(audio_dir: Path = ""):
    # Make a list of all the audio files we have for this language
    audio_on_disk = []
    audio_on_disk_paths = audio_dir.glob("**/*.mp3")
    for audio_on_disk_path in audio_on_disk_paths:
        audio_on_disk.append(audio_on_disk_path.name.lower())
    return audio_on_disk


def unzip_archives(zip_path: Path = None):
    """
    TODO: assumes that all domains have an English equivalent,
    so the domains list will be a set of names without the english equivalents.
    Should fix this to be more explicit list of domains and mark which ones do have English
    """
    domains = []
    zip_paths = zip_path.glob("**/*.zip")

    for zip_path in sorted(zip_paths):
        domain = zip_path.stem
        domain_clean = domain.replace("(", "").replace(")", "")
        # Temporarily exclude english zips from the domain list until we have a better way
        domain_no_english = domain_clean.replace("-english", "")
        domains.append(domain_no_english)
        domains = list(set(domains))
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(f"../tmp/{domain_clean}")
    domains.sort()
    print(domains)
    return domains


def build_menu(domains: List, is_index: bool = False):
    subdir = "./" if is_index else "../"
    menu_soup = BeautifulSoup('<ul id="menu"></ul>', "html.parser")
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
        # TODO check whether there's actually a page for this
        link_group_tag.append(english_link_tag)

        menu_tag.append(link_group_tag)
    return menu_tag


def get_template(template_path: str) -> BeautifulSoup:
    with Path(template_path).open("r") as template_file:
        return BeautifulSoup(template_file, "html5lib")


def make_domain_readable(domain: str) -> str:
    pattern = r"^[a-z]+-(.*)"
    replacemenet = lambda m: m.group(1).replace("-", " ").title()
    return re.sub(pattern, replacemenet, domain)


def write_missing_report(report_type: str = "", language: str = "", missing: List[List[str]] = None):
    csv_path = Path(f"../reports/{language}-{report_type}-report.csv")
    with csv_path.open("a", newline='') as csvfile:
        headers = ["Language", "Entry", "Src", "Domain"]
        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
        if csvfile.tell() == 0:
            writer.writeheader()
        for entry, src, domain in missing:
            writer.writerow({"Language": language,
                             "Entry": entry,
                             "Src": src,
                             "Domain": domain})


def process_domain(language: List[str],
                   html_path: Path,
                   menu_soup: BeautifulSoup,
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

        # Remove <!--a--> and bad <!--a2-> tags
        html = html.replace("<!--a-->", "")
        html = html.replace("<!--a2->", "")

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
        anchor_replacement = r'<div class="wsumarcs-entry" id="\1">'
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
        write_missing_report(report_type="images", language=language[0], missing=missing)

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
        write_missing_report(report_type="audio", language=language[0], missing=missing)

        # Get the page templates
        template_soup = get_template(template_path="../templates/entry_page/content.html")

        # Change the page title
        article_tag = template_soup.find("title")
        article_tag.string = f"{language[1]} dictionary | {make_domain_readable(domain_dir)}"

        # Insert the menu
        nav_tag = template_soup.find("nav")
        nav_tag.append(menu_soup)

        # Change the page header
        header_tag = template_soup.find("header")
        header_tag.string = make_domain_readable(domain_dir)

        # Insert the content
        article_tag = template_soup.find("article")
        article_tag.string = ""
        article_tag.append(content_soup)

        # Save the html
        domain_output_path = Path(f"../output/{language[0]}/{domain_dir}")
        domain_output_path.mkdir(parents=True, exist_ok=True)
        with domain_output_path.joinpath("index.html").open("w") as html_output_file:
            html_output_file.write(template_soup.prettify())


def build_index_file(language: List[str], domains: List[str]):

    # Slurp in the home page content
    with Path(f"../content/{language[0]}/home.html").open("r") as content_file:
        content_soup = BeautifulSoup(content_file, "html.parser")

    # Build the menu for the index page - it will have different path ./ vs ../ for content pages
    menu_tag = build_menu(domains=domains, is_index=True)

    # Build the page
    template_soup = get_template(template_path="../templates/entry_page/index.html")

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
    menu_soup = build_menu(domains=domains, is_index=False)
    # Build each domain page
    html_paths = Path("../tmp").glob("**/*.html")
    for html_path in html_paths:
        process_domain(language=language,
                       html_path=html_path,
                       menu_soup=menu_soup,
                       images_on_disk=images_on_disk,
                       audio_on_disk=audio_on_disk)


def main():
    """
    Before running this script, do the flatten_media_dir script
    And add wordspinner zips to content/language/zips/ dir
    """

    debug = False

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

    # Reset reports dir
    reports_path = Path("../reports")
    if reports_path.is_dir():
        shutil.rmtree(reports_path)
        reports_path.mkdir(parents=True, exist_ok=True)

    # Reset output dir
    output_path = Path(f"../output")
    if output_path.is_dir():
        shutil.rmtree(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

    # Build landing page
    if not debug:
        landing_page_path = Path(f"../output/dictionaries/")
        landing_page_path.mkdir(parents=True, exist_ok=True)
        with open("../templates/landing_page/index.html") as template_file:
            tm = Template(template_file.read())
            html = tm.render(languages=languages)
            with landing_page_path.joinpath("index.html").open("w") as html_output_file:
                html_output_file.write(html)
        shutil.copytree("../templates/landing_page/_assets", landing_page_path.joinpath("_assets"), dirs_exist_ok=True)

    for language in languages:
        print(f"==== Doing {language[1]} ====")

        # Audio has been flattened from the media dir into separate audio folders per language
        audio_on_disk = compile_audio_on_disk_list(audio_dir=Path(f"../all_audio/{language[0]}/_audio"))

        # Reset tmp and reports dirs
        tmp_path = Path("../tmp")
        if tmp_path.is_dir():
            shutil.rmtree(tmp_path)

        # Copy assets
        output_language_dir = Path(f"../output/{language[0]}")
        shutil.copytree("../templates/entry_page/_assets", output_language_dir.joinpath("_assets"), dirs_exist_ok=True)

        # Copy the feature image from the content folder
        shutil.copy(f"../content/{language[0]}/feature.jpg", output_language_dir.joinpath("_assets"))

        # Create media dirs and fill with content that has been flattened
        shutil.copytree("../all_images/_img_sm", output_language_dir.joinpath("_img"), dirs_exist_ok=True)
        shutil.copytree(f"../all_audio/{language[0]}/_audio", output_language_dir.joinpath("_audio"), dirs_exist_ok=True)

        # Prepare the domain zips
        zip_path = Path(f"../content/{language[0]}/zips")
        domains = unzip_archives(zip_path=zip_path)

        # Now build the html pages
        print("==== Build index file ====")
        build_index_file(language=language, domains=domains)
        print("==== Iterate htmls ====")
        iterate_htmls(language=language, domains=domains, images_on_disk=images_on_disk, audio_on_disk=audio_on_disk)
        print("done\n\n")


if __name__ == "__main__":
    main()
