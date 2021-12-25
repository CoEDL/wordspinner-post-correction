import shutil
from pathlib import Path

# languages = ["test"]

languages = [
    "bilinarra",
    "gurindji",
    "mudburra",
    "ngarinyman"]

for language in languages:

    source_path = Path(f"../content/{language}")
    target_path = Path(f"../output/{language}/")

    target_path.joinpath("_audio").mkdir(parents=True, exist_ok=True)
    target_path.joinpath("_img").mkdir(parents=True, exist_ok=True)

    # Process audio
    for each_file in source_path.glob('**/*.mp3'):
        print(each_file)
        shutil.copy(each_file, target_path.joinpath("_audio"))

    # Process images
    for each_file in source_path.glob('**/*.jpg'):
        print(each_file)
        shutil.copy(each_file, target_path.joinpath("_img"))
