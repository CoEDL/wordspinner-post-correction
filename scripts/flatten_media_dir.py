import shutil
from pathlib import Path


source_path = Path(f"../all_images_source/")
target_path = Path(f"../all_images_target/")

# Process audio
# target_path.joinpath("_audio").mkdir(parents=True, exist_ok=True)
# for each_file in source_path.glob('**/*.mp3'):
#     print(each_file)
#     shutil.copy(each_file, target_path.joinpath("_audio"))

# Process images
target_path.joinpath("_img").mkdir(parents=True, exist_ok=True)
for each_file in source_path.glob('**/*.jpg'):
    file_name = each_file.parts
    new_name = file_name[-1].replace(" ", "_").lower()
    shutil.copy(each_file, target_path.joinpath(f"_img/{new_name}"))
    print(new_name)
