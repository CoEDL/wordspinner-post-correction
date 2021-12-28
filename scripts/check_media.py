"""
for each html
match all img src
iterate and check if file exists
"""
import csv
from pathlib import Path
import shutil

def main(language: str):
    from bs4 import BeautifulSoup
    from pathlib import Path

    entries = []
    missing = []

    # Make a list of all the image files we have
    images_on_disk = []
    images_on_disk_paths = Path(f"../all_images_target").glob("**/*.jpg")
    for images_on_disk_path in images_on_disk_paths:
        images_on_disk.append(images_on_disk_path.name)

    # Make a list of every entry and its image
    html_paths = Path(f"../output/{language}").glob("**/index.html")
    for html_path in html_paths:
        domain = html_path.parts[3]
        print(domain)
        with Path(html_path).open("r") as html_file:
            soup = BeautifulSoup(html_file, "html5lib")
            images = [image for image in soup.select(".wsumarcs-entry img.wsumarcs-comPic")]
            # print(images)
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

    with Path(f"../reports/report-{language}.csv").open("w", newline='') as csvfile:
        # csv_writer = csv.writer(csvfile,
        #                         delimiter=",",
        #                         quotechar="|",
        #                         quoting=csv.QUOTE_MINIMAL)
        # for entry_id, image_src, domain in missing:
        #     csv_writer.writerow([entry_id, image_src, domain])
        headers = ["Language", "Entry", "Image", "Domain"]
        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
        writer.writeheader()  # file doesn't exist yet, write a header

        for entry_id, image_src, domain in missing:
            writer.writerow({"Language": language,
                             "Entry": entry_id,
                             "Image": image_src,
                             "Domain": domain})


if __name__ == "__main__":

    if Path("../reports").is_dir():
        shutil.rmtree("../reports")
    Path("../reports").mkdir(parents=True, exist_ok=True)

    languages = [
        ["bilinarra", "Bilinarra"],
        ["gurindji", "Gurindji"],
        ["mudburra", "Mudburra"],
        ["ngarinyman", "Ngarinyman"]
        # ["test", "Test"]
    ]

    for language in languages:
        print(f"\n\n* * * * *\n\n{language[0]}")
        main(language=language[0])
