"""
Make a list of all the dictionary audio we have.
For each domain (html), get all audio.
Compile a report of all the ones that are not in the master list.

If this script is run after process.py it should result in an empty list,
because process should remove missing audio tags
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
            audio["data-file"] = audio["data-file"].replace(" ", "_").lower()
            audio_name = audio["data-file"].replace("../_audio/", "")
            entry = audio.find_parent("div")
            entry_id = entry["id"]
            entries.append([entry_id, audio_name, domain])

    # Check each entry to see if we have an audio for it
    for entry_id, audio_name, domain in entries:
        print(audio_name)
        if audio_name not in audio_on_disk:
            missing.append([entry_id, audio_name, domain])

    missing = sorted(missing, key=lambda x: x[0].lower())
    print(missing)
    with Path(f"../reports/audio/report-{language}.csv").open("w", newline='') as csvfile:
        headers = ["Language", "Entry", "Audio", "Domain"]
        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)
        writer.writeheader()
        for entry, audio, domain in missing:
            writer.writerow({"Language": language,
                             "Entry": entry,
                             "Audio": audio,
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

    reports_path = Path("../reports")
    if reports_path.is_dir():
        shutil.rmtree(reports_path)
    reports_path.joinpath("audio").mkdir(parents=True, exist_ok=True)

    for language in languages:
        audio_on_disk = compile_audio_on_disk_list(audio_dir=Path(f"../all_audio/{language[0]}/_audio"))
        print(audio_on_disk)
        print(f"\n\n* * * * *\n\n{language[0]}")
        main(language=language[0], audio_on_disk=audio_on_disk)
