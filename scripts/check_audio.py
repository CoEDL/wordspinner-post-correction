"""
Make a list of all the dictionary audio we have.
For each domain (html), get all audio.
Compile a report of all the ones that are not in the master list.
"""

import csv
from pathlib import Path
import shutil
from typing import List


def compile_audio_on_disk_list(audio_dir: Path = ""):
    # Make a list of all the audio files we have
    audio_on_disk = []
    audio_on_disk_paths = audio_dir.glob("**/*.mp3")
    for audio_on_disk_path in audio_on_disk_paths:
        audio_on_disk.append(audio_on_disk_path.name)
    return(audio_on_disk)


def main(language: str, audio_on_disk: List[str]):
    from bs4 import BeautifulSoup
    from pathlib import Path

    entries = []
    missing = []

    # Make a list of every entry and its audio
    html_paths = Path(f"../output/{language}").glob("**/index.html")
    for html_path in html_paths:
        domain = html_path.parts[3]
        print(domain)
        with Path(html_path).open("r") as html_file:
            soup = BeautifulSoup(html_file, "html5lib")
            audios = [audio for audio in soup.select(".wsumarcs-entry img.wsumarcs-entrySfx")]
        for audio in audios:
            audio_src = audio["data-file"].replace("../_audio/", "")
            entry = audio.find_parent("div")
            entry_id = entry["id"]
            entries.append([entry_id, audio_src, domain])

    print(entries)

    # Check each entry to see if we have an audio for it
    # for entry_id, audio_src, domain in entries:
    #     if audio_src not in audio_on_disk:
    #         missing.append([entry_id, audio_src, domain])
    #
    # missing = sorted(missing, key=lambda x: x[0].lower())
    #
    # with Path(f"../reports/audio/report-{language}.csv").open("w", newline='') as csvfile:
    #     headers = ["Language", "Entry", "audio", "Domain"]
    #     writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
    #     writer.writeheader()
    #     for entry_id, audio_src, domain in missing:
    #         writer.writerow({"Language": language,
    #                          "Entry": entry_id,
    #                          "audio": audio_src,
    #                          "Domain": domain})


if __name__ == "__main__":

    DEBUG = True

    if DEBUG:
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
    Path("../reports/audio").mkdir(parents=True, exist_ok=True)

    audio_on_disk = compile_audio_on_disk_list(audio_dir=Path(f"../all_audio"))

    for language in languages:
        print(f"\n\n* * * * *\n\n{language[0]}")
        main(language=language[0], audio_on_disk=audio_on_disk)
