from pathlib import Path

src_path = Path("../media/Dict_Images")
target_path = Path("../images")

for each_file in src_path.glob('**/*.jpg'):
    print(each_file)
    each_file.rename(target_path.joinpath(each_file.name))
