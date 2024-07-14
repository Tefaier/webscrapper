# Webscrapper
The project is intended to scrap content of ranobe's/novel's chapters. These are books that are published online with chapters of 2000-10000 symbols in general. \
It is not a hack in any way. For scrapper novel must be available for viewing by any visitor or by you.

## Scrapper is able to:
- bypass cloudflare (not always)
- use google profile (sometimes required to get access to chapters)
- include images (has many restrictions and can even fail due to image's strange type)
- save content in txt, docx, html (html will add basic html structure)
- press, make some input upon opening page (in case needed to bypass popup)
- scroll page
- wait for page to load
- can understand jammed text through image recognition


## Limitations to consider:
- requires you to look through html markdown of website's page with chapters and carefully consider a way for program to locate heading, content and link to the next chapter
- using chrome requires having chromedriver and putting path to it in code/Settings.py
- using jammed text recognition requires tesseract and putting path to it in code/Settings.py
- not sure if there will be problems with systems other than windows 10

## Important at the start:
- create code/Settings.py file on the basis of code/Settings_base.py and input fields that you need. Also some settings that were left there can be used for reference (however they can be outdated either due to being made while earlier program versions or due to website change).
- if you use chrome, it will open a window. Closing it will terminate program but should leave saved what was already scrapped. Also using text recognition will require having chrome window chosen as "active"
- log that it writes to the console is not really accurate
- sometimes it may show you some text of what it scrapped in the console and ask you if you want it to continue. It is like a check if what it got is really a chapter you need. Conditions for triggering it can be altered.
