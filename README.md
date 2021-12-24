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
 
