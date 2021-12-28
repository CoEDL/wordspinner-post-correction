import shutil
from pathlib import Path

# languages = ["test"]



source_path = Path(f"../all_images_source/")
target_path = Path(f"../all_images_target/")

# target_path.joinpath("_audio").mkdir(parents=True, exist_ok=True)
target_path.joinpath("_img").mkdir(parents=True, exist_ok=True)

# # Process audio
# for each_file in source_path.glob('**/*.mp3'):
#     print(each_file)
#     shutil.copy(each_file, target_path.joinpath("_audio"))

# Process images
for each_file in source_path.glob('**/*.jpg'):
    print(each_file)
    shutil.copy(each_file, target_path.joinpath("_img"))
