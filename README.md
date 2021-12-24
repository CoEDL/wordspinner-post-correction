# Manual fixes

## Insert a named anchor for linking in the lang file

Match the entry opening div, keep the name, not the wsumarcs- bit.

```
<div class=\"wsumarcs-entry\" id=\"wsumarcs-([a-z]+)\">
```
Replace with:
```
<a name="$1"></a><div class="wsumarcs-entry" id="$1">
```

## Change the URL in the english file

Remove the view php path and hash, replace with domain name in lowercase.

```
/view.php\?domain=([ a-z]+)&hash=[\w]+
```
Replace with:
```
\L$1/index.html
```

Then, replace space with - and insert index.html.

```
<a href="([a-z]+) ([a-z]+)
```
Replace with:
```
<a href="../$1-$2/index.html
```







# Processing... 

Use Beautiful Soup to strip styles and script tags
It also automatically inserts html head and body.

Remove the `$('a[href*="#"]')` script stuff, seems to be something to do with the hash path.

Add link to common styles.css file
Add link to common script.js file


Change audio src to audio dir not img 
```
data-file="img/
data-file="audio/
```

Create a menu
Create an index page

Manually add a background image


TODO 
fix menu regex to handle () in names for 
    s-verbs-(inflecting)-english.zip
    s-verbs-(inflecting).zip
 


# RUN

make a language-output dir
and language-zip dir
make a tmp dir

put the wordspinner zips in the zips dir

## Flatten the media dir structure

make _audio and _img dirs in language-output
make a media dir
move DICT_Audio & Headword_Sound dirs from dropbox to the  media folder
change paths and media file ext in the flatten_media_dir script
run it
repeat for img

## Prep the HTML
Change gurindji-output and gurindji-zip dirs in the process script
run it


Test it locally - might need to change httpd-custom.conf file in ~/Sites
and `brew services restart httpd` 


FUTURE 
remove / increment duplicate ids
make filenaes lowercase
