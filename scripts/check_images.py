"""
Make a list of all the dictionary images we have.
For each domain (html), get all images.
Compile a report of all the ones that are not in the master list.

If this script is run after process.py it should result in an empty list,
because process should remove missing image tags
"""

import csv
from pathlib import Path
import shutil
from typing import List


def compile_images_on_disk_list(image_dir: Path = ""):
    # Make a list of all the image files we have
    images_on_disk = []
    images_on_disk_paths = image_dir.glob("**/*.jpg")
    for images_on_disk_path in images_on_disk_paths:
        images_on_disk.append(images_on_disk_path.name)
    return(images_on_disk)


def main(language: str, images_on_disk: List[str]):
    from bs4 import BeautifulSoup
    from pathlib import Path

    entries = []
    missing = []

    # Make a list of every entry and its image
    html_paths = Path(f"../output/{language}").glob("**/index.html")
    for html_path in html_paths:
        domain = html_path.parts[3]
        print(domain)
        with Path(html_path).open("r") as html_file:
            soup = BeautifulSoup(html_file, "html5lib")
            images = [image for image in soup.select(".wsumarcs-entry img.wsumarcs-comPic")]
        for image in images:
            image_src = image["src"].replace("../_img/", "")
            entry = image.find_parent("div")
            entry_id = entry["id"]
            entries.append([entry_id, image_src, domain])

    # Check each entry to see if we have an image for it
    for entry_id, image_src, domain in entries:
        if image_src not in images_on_disk:
            missing.append([entry_id, image_src, domain])

    missing = sorted(missing, key=lambda x: x[0].lower())

    with Path(f"../reports/images/report-{language}.csv").open("w", newline='') as csvfile:
        headers = ["Language", "Entry", "Image", "Domain"]
        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
        writer.writeheader()
        for entry, image, domain in missing:
            writer.writerow({"Language": language,
                             "Entry": entry,
                             "Image": image,
                             "Domain": domain})


if __name__ == "__main__":

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

    if Path("../reports").is_dir():
        shutil.rmtree("../reports")
    Path("../reports/images").mkdir(parents=True, exist_ok=True)

    images_on_disk = compile_images_on_disk_list(image_dir=Path(f"../all_images/_img"))

    for language in languages:
        print(f"\n\n* * * * *\n\n{language[0]}")
        main(language=language[0], images_on_disk=images_on_disk)
