from pathlib import Path
import os


def normalise(dir):
    """
    Make the zips lowercase and get rid of spaces
    """

    # This glob string will get the subfolders inside the zips dir
    for child in sorted(dir.glob('**/*')):
        # Make the zips lowercase, and replace space with underscore
        child.rename(Path.joinpath(dir, child.name.lower().replace(" ", "-")))



def main():

    debug = True

    if debug:
        languages = [["ngarinyman", "Ngarinyman"]]
    else:
        languages = [
            ["bilinarra", "Bilinarra"],
            ["gurindji", "Gurindji"],
            ["mudburra", "Mudburra"],
            ["ngarinyman", "Ngarinyman"]
        ]

    for language in languages:

        zip_path = Path(f"../content/{language[0]}/zips")

        normalise(zip_path)
        quit()

        domains = []
        en_domains = []
        zip_paths = sorted(zip_path.glob("**/*.zip"))
        for path in zip_paths:
            print(path)

        for zip_path in sorted(zip_paths):
            domain = zip_path.stem
            if not "English" in domain:
                domains.append({"domain": domain})
            if "English" in domain:
                en_domains.append(domain.replace("-English", ""))

        for domain in domains:
            domain["has_en"] = True if domain["domain"] in en_domains else False

        print(domains)
        print(en_domains)


if __name__ == "__main__":
        main()
