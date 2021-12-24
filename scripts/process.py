"""
Script to clean the HTML files
"""
from bs4 import BeautifulSoup
import html5lib
import re

# Open the html file
with open("../source/a-body/index.html") as html_input_file:
    soup = BeautifulSoup(html_input_file, 'html5lib')

# Strip script and style tags
[x.extract() for x in soup.findAll(['script', 'style'])]

# Insert jQuery script link
# <script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>
jquery_tag = soup.new_tag("script")
jquery_tag.attrs["src"] = "http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"
soup.head.insert(0, jquery_tag)

script_tag = soup.new_tag("script")
script_tag.attrs["src"] = "script.js"
soup.head.insert(1, script_tag)

# Insert new stylesheet link
stylesheet_tag = soup.new_tag("link")
stylesheet_tag.attrs["rel"] = "stylesheet"
stylesheet_tag.attrs["href"] = "styles.css"
soup.head.insert(2, stylesheet_tag)

pretty_html = soup.prettify()

# Fix audio dir in player icons
pattern = 'data-file="img/'
replacement = 'data-file="audio/'
pretty_html = re.sub(pattern, replacement, pretty_html)



# Save the html
with open("../test/test.html", "w") as html_output_file:
    html_output_file.write(str(pretty_html))
