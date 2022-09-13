import shutil
from pathlib import Path


def process_images(source_path: Path = None, target_path: Path = None):
    # Process images by combining languages into a single dir
    for each_file in source_path.glob('**/*.jpg'):
        file_name = each_file.parts
        new_name = file_name[-1].replace(" ", "_").lower()
        shutil.copy(each_file, target_path.joinpath(new_name))
        print(new_name)


def process_audio(source_path: Path = None, target_path: Path = None):
    # Process audio separately by language
    target_path.mkdir(parents=True, exist_ok=True)
    for each_file in source_path.glob('**/*.mp3'):
        file_name = each_file.parts
        new_name = file_name[-1].replace(" ", "_").lower()
        shutil.copy(each_file, target_path.joinpath(new_name))
        print(new_name)


if __name__ == "__main__":

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

    source_path = Path(f"../media/")

    target_image_path = Path(f"../all_images/_img")
    target_image_path.mkdir(parents=True, exist_ok=True)
    process_images(source_path=source_path, target_path=target_image_path)

    for language in languages:
        target_audio_path = Path(f"../all_audio/{language[0]}/_audio")
        if target_audio_path.is_dir():
            shutil.rmtree("../all_audio")
        target_audio_path.mkdir(parents=True, exist_ok=True)
        print(f"\n\n* * * * *\n\n{language[0]}")
        process_audio(source_path=source_path.joinpath(language[0]), target_path=target_audio_path)
