# Webscrapper
The project is intended to scrap content of ranobe's/novel's chapters. These are books that are published online with chapters of 2000-10000 symbols in general. \
It is not a hack in any way since scrapped novel must be available for viewing by any visitor. \
Potentially it can be as well be used to parse mangas at it is not supported currently.

## Scrapper is able to:
- bypass cloudflare (not always)
- use google profile (sometimes required to get access to chapters)
- include images (has many restrictions and can even fail due to image's strange type)
- save content in txt, docx, html
- press, make some input upon opening page (in case needed to bypass popup)
- scroll page
- wait for page to load
- can understand jammed text through image recognition

## Limitations to consider:
- requires you to look through html markdown of website's page with chapters and carefully consider a way for program to locate heading, content and link to the next chapter
- using chrome requires having chromedriver and putting path to it in settings
- using jammed text recognition requires tesseract and putting path to it in settings
- not sure if there will be problems with systems other than windows 11

## Pointers:
- if you want to add support for other websites or to patch some existing (some of them may even not work at all already), you should go to website_resolve and configure scraper for website using ExtendedFactory. Pay attention that it provides to default setup at the beginning and at the moment ParsingProcess is created, including post processors you can use. 
- locally you will have to for all files `*.example` write an analogue without  this postfix with value you want
