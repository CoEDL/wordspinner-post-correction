# Making a website from WordSpinner output

This project converts the output of WordSpinner into a HTML website. WordSpinner itself outputs HTML pages, but those files don't conform to HTML standards, and don't include features such as menus. This project uses the content from the WordSpinner pages, makes responsive HTML with menus, and also corrects issues such as broken links to media etc.

The process happens in a few stages. First, collect the images and audio that the dictionary references; run the script to organise that media in a way that is efficient for web publication, then run a script to process the HTML. Once the scripts have completed, upload to your web server.

This can be done for a single dictionary, or for multiple dictionaries at a time, which may be useful if the multiple dictionaries share image resources (because the media script will copy images from multiple projects into a single media directory).

## Requirements

Requires Python 3 and [Poetry](https://python-poetry.org/docs/)


## 1. Compile media

The "flatten media" script will copy JPGs from a specified folder (and subfolders) into a single directory. This is done as a simple (lazy) way to try and reduce the number of missing images in the dictionary content. 

The media script will do the same for MP3 audio, but will keep separate directories of audio for each language rather than copying into a single directory. Eg, for a dictionary proejct with two languages, the audio will be copied into two language folders:


1.1. First put all the folders containing your dictionary media into a single `media` folder.  
1.2. Set up the Python environment  
1.3. CD into the scripts directory  
1.4. Edit the flatten media script to specific the language you are working with. See notes in the script.    
1.5. Run it.

```
cd /Users/bbb/Sites/dictionaries
poetry shell
cd scripts
python flatten_media_dir.py
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
2.3. Make a `zips` folder in each language folder, and copy the WordSpinner zip files there.  

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

3.1. For each language you are building a dictionary for, create a file named `home.html` with the following structure (note that it is just a snippet of HTML, not a full page. I.e., no doctype or `<html><head><body>` tags). Add your home page content inside the second `<section>` tag. Save it as `home.html` in the language folder that is inside `content`. 

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

4.1. To build the html, prepare the Poetry environment, then run the `process.py` script.   
4.2. Debug first with a language named "test" by changing the debug setting in `main()` to `True`.   
4.3. The script doesn't accept any args, but you can specify or limit the languages it builds by changing the languages list in `main()`.   
4.4. Skip the first three commands below if you have just prepared the media (because you should already be in the right dir, with the Poetry environment already created).

```
cd /Users/bbb/Sites/dictionaries
poetry shell
cd scripts
python process.py
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
