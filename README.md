# Making a website from WordSpinner output

This project converts the output of WordSpinner into an HTML website. WordSpinner itself outputs HTML, but the files don't conform to HTML standards, and they don't include features such as menus. This project reads the WordSpinner files and media files and builds HTML websites. The scripts re-arrange the media, build menus, make responsive HTML, and also correct issues such as broken links to media.

Before using the scripts, collect the images and audio that the dictionaries reference and run the `flatten_media_dir` script to organise that media in a way that is efficient for web publication. Then run the `process` script to build the dictionary webpages. Once the scripts have completed, upload them and the media folders to your web server.


## Requirements

Requires Python 3 and [Poetry](https://python-poetry.org/docs/)


## 1. Compile media

The "flatten media" script will copy all JPEGs from a specified source folder, and it's subfolders, into a single target directory. This is done to compile all images into a single directory, and reduce missing problems associated with missing images. This approach is a design decision arising from the high degree of image reuse amongst the four dictionaries that were the cause of this project. If you have multiple dictionaries which don't share images, it's probably best to do the build process for one dictionary at a time.    

The media script will collect MP3 audio from a source fodler, but will keep separate directories of audio for each language rather than copying into a single target directory. Eg, for a dictionary project with two languages, the audio will be copied into two language folders.


1.1. First put all the folders containing your dictionary media into a `media` folder inside the project. You can also include any misc images; put them in a folder inside media too. 
1.2. Set up the Python environment. 
1.3. Edit the `flatten_media_dir` script to specific the language/s you are working with. See notes in the script. This will affect which subfolders the script will attempt to process.    

```
cd ~/Sites/dictionaries
poetry shell
python scripts/flatten_media_dir.py
```

1.6. The results will be two folders of media eg:
```shell
├── all_audio
│   ├── bilinarra
│   │   └── _audio
│   │        ├── word_01.mp3
│   │        └── word_02.mp3
│   └── mudburra
│       └── _audio
│            ├── word_03.mp3
│            └── word_04.mp3
└── all_images
    └── _img
        ├── img_01.jpg
        ├── img_02.jpg
        └── img_03.jpg
```


1.7. After the script has run, compress and optimise the images in the new directory (use third party software for this).


## 2. Create project structure

The processing script can work on an individual dictionary, or multiple dictionaries. This behaviour is specified as a list of language names in the script (see 4.3 below). For now, create folders for each dictionary that you want to build, and collate content into each.

2.1. Make a `content` folder in the same place that the `all_audio` and `all_images` folders are.   
2.2. Inside the new `content` folder, make another folder named (lowercase) with the dictionary language. Repeat for each dictionary that you are building.  
2.3. Make a `zips` folder in each language folder, and copy the WordSpinner zip files into that folder.  

e.g. for Bilinarra language:

```shell
├── all_audio
├── all_images
└── content
      └── bilinarra
             └── zips
                  ├── a-body-english.zip
                  ├── a-body.zip
                  ├── b-people-english.zip
                  └── b-people.zip
```

## 3. Making a dictionary home page

3.1. For each language you are building a dictionary for, create a file named `home.html` in the `content/language` folder, with the following structure (note that it is just a snippet of HTML, not a full page. I.e., no doctype or `<html><head><body>` tags). Add your home page content inside the second `<section>` tag. Save it as `home.html` in the language folder that is inside `content`. 

```
<section id="feature_image">
    <img src="_assets/feature.jpg" alt="landscape" />
</section>
<section>
    <p>replace with home page content</p>
</section>
```

3.2. Add a `feature.jpg` image (width 800 px) in that folder.

3.3. The complete content structure should look like this (showing an example of a two-dictionary project):
```  
├── all_audio
│   ├── bilinarra
│   │   └── _audio
│   │        ├── word_01.mp3
│   │        └── word_02.mp3
│   └── mudburra
│       └── _audio
│            ├── word_03.mp3
│            └── word_04.mp3
├── all_images
│   └── _img
│       ├── img_01.jpg
│       ├── img_02.jpg
│       └── img_03.jpg│
├── content
│      ├── bilinarra
│      │      ├── feature.jpg
│      │      ├── home.html
│      │      └── zips
│      │            ├── a-body-english.zip
│      │            ├── a-body.zip
│      │            ├── b-people-english.zip
│      │            └── b-people.zip
│      │
│      └── mudburra
│            ├── feature.jpg
│            ├── home.html
│            └── zips
│                  ├── a-body-english.zip
│                  ├── a-body.zip
│                  ├── b-people-english.zip
│                  └── b-people.zip   
└── scripts
       └── process.py

```

## 4. Build the HTML

This script builds webpages for each domain of a selected language, or all languages. The HTML pages include a menu which is generated by the dictionary domains. The list of domains is derived from the names of zips. The HTML is responsive, though very basic. The script checks if images or audio are missing and removes tags for media that is missing. Reports are generated with lists of missing names.

4.1. Debug first by changing the debug setting in `main()` to `True`. Copy the `home.html`, feature image and some zips from one of the dictionaries into a `test` folder in `content` (put the zips into a `zips` dir).   
4.2. Skip the first three commands below if you have just prepared the media (because you should already be in the right dir, with the Poetry environment already created).  
4.3. Run the script, then review the output.   
4.4. If you are happy with the output, change the debug setting to `False`, specify the language names you want to build in `main()` and then re-run the script. 

```
cd ~/Sites/dictionaries
poetry shell
python scripts/process.py
```

4.5. While building, the script checks if media that is linked in the content exists in the media directory. If media is not found, a message is shown in the terminal (see example below) and CSV files are generated in the `reports` dir containing the missing media details.

```shell
n-description
. . . missing image salt_c.jpg
. . . missing image yellow_ochre.jpg
```

4.6. When it completes, you should have an `output` folder, containing `_assets`, `_audio`, `_img` and domain folders and an index.html file.

```shell
├── output
│   └── bilinarra
│       ├── _assets
│       ├── _audio
│       ├── _img
│       ├── a-body
│       ├── a-body-english
│       ├── b-people
│       ├── b-people-english
```



## Check

To test it, set up Apache locally and browse to the generated pages using local dev domains. See guides online for instructions to set up Apache on Mac, such as this one on [grav](https://getgrav.org/blog/macos-monterey-apache-mysql-vhost-apc). Set the local dev domain by changing the `httpd-custom.conf` file in `~/Sites` and doing `brew services restart httpd`. 



## TODO

- remove () from the domains and zips?
