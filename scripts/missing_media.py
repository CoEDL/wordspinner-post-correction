"""
Process backslash files to find mismatching media
standardise image and audio file names first using slugify

audio should stay in separate folders per language
images should be in a common directory
"""
import re
import shutil
from pathlib import Path
import os


def process_filename(file_name: Path):
    parts = file_name.parts
    return parts[-1].replace(" ", "_").lower()


def compile_audio_on_disk_list(media_dir: Path = ""):
    # Make a list of all the audio files we have for this language
    audio_on_disk = []
    audio_on_disk_paths = media_dir.glob("**/*.mp3")
    for audio_on_disk_path in audio_on_disk_paths:
        audio_on_disk.append(audio_on_disk_path.name.lower())
    audio_on_disk.sort()
    with Path("../reports/all_audio.txt").open("w") as audio_file:
        for item in audio_on_disk:
            audio_file.write("%s\n" % item)
    return audio_on_disk


def compile_images_on_disk_list(media_dir: Path = ""):
    # Make a list of all the audio files we have for this language
    images_on_disk = []
    images_on_disk_paths = media_dir.glob("**/*.jpg")
    for audio_on_disk_path in images_on_disk_paths:
        images_on_disk.append(audio_on_disk_path.name.lower())
    images_on_disk.sort()
    with Path("../reports/all_images.txt").open("w") as images_file:
        for item in images_on_disk:
            images_file.write("%s\n" % item)
    return images_on_disk


def report_missing_audio(media_source_path, backslash_source_path):
    # make a list of all audio files
    audio_list = compile_audio_on_disk_list(media_source_path)
    # get audio files from the backslash and check  if they are in the list.
    # make a list of missing ones
    missing = []
    for each_file in backslash_source_path.glob('**/*.txt'):
        print("\n\n***", each_file)
        all_entries = []
        with open(each_file, "r") as lex_file:
            text = lex_file.read()
            entries_raw = text.split('\n\n')  # Split by empty line
            for entry_raw in entries_raw:
                entry = ([item.strip() for item in entry_raw.split('\n')])
                if entry != ['']:
                    entry_tmp = []
                    for entry_data in entry:
                        matches = re.match(r"(\\+[a-z]+) (.+)", entry_data)
                        if matches:
                            all = matches.group(0)
                            key = matches.group(1).replace("\\", "")
                            content = matches.group(2)
                            entry_tmp.append((key, content))
                    all_entries.append(entry_tmp)

        for entry in all_entries:
            _, lx = entry[0]
            for key, content in entry:
                if key in ["sf", "sfx"]:
                    file_name = process_filename(Path(content))
                    if file_name not in audio_list:
                        print("missing", Path(each_file).parts[-1], lx, key, file_name)
                        missing.append(f"{Path(each_file).parts[-1]}, {lx}, {key}, {file_name}")

    with Path("../reports/missing_audio.txt").open("w") as missing_file:
        for item in missing:
            missing_file.write("%s\n" % item)


def report_missing_images(media_source_path, backslash_source_path):
    # make a list of all audio files
    image_list = compile_images_on_disk_list(media_source_path)
    # get audio files from the backslash and check  if they are in the list.
    # make a list of missing ones
    missing = []
    for each_file in backslash_source_path.glob('**/*.txt'):
        print("\n\n***", each_file)
        all_entries = []
        with open(each_file, "r") as lex_file:
            text = lex_file.read()
            entries_raw = text.split('\n\n')  # Split by empty line
            for entry_raw in entries_raw:
                entry = ([item.strip() for item in entry_raw.split('\n')])
                if entry != ['']:
                    entry_tmp = []
                    for entry_data in entry:
                        matches = re.match(r"(\\+[a-z]+) (.+)", entry_data)
                        if matches:
                            all = matches.group(0)
                            key = matches.group(1).replace("\\", "")
                            content = matches.group(2)
                            entry_tmp.append((key, content))
                        # print(entry_tmp)
                    all_entries.append(entry_tmp)

        for entry in all_entries:
            _, lx = entry[0]
            for key, content in entry:
                if key in ["pc"] and "jpg" in content:
                    file_name = process_filename(Path(content))
                    if file_name not in image_list:
                        print("missing", Path(each_file).parts[-1], lx, key, file_name)
                        missing.append(f"{Path(each_file).parts[-1]}, {lx}, {key}, {file_name}")


    with Path("../reports/missing_images.txt").open("w") as missing_file:
        for item in missing:
            missing_file.write("%s\n" % item)


if __name__ == "__main__":

    media_source_path = Path(f"../media/")
    backslash_source_path = Path(f"../backslash/")

    # report_missing_audio(media_source_path=media_source_path, backslash_source_path=backslash_source_path)
    report_missing_images(media_source_path=media_source_path, backslash_source_path=backslash_source_path)
