# Welcome to Excav8r!
![enter image description here](https://i.imgur.com/LeOgrQ0.png)

Excav8r is an open-source Python library (inspired by an episode of Silicon Valley) that allows developers to download and/or utilize datasets of over a thousand images with just a few lines of code. It with the intention for use by AI developers who need access to large photosets quickly.

 ```python
 import excav8r
scraper = excav8r.Excva8r()

# Will save a maximum of 500 images from DuckDuckGo with search term "single orange png"  
scraper.getDuckDuckGo("single orange png", max=500)  
  
# Will save images from both DuckDuckGo and Google with keyword "hot dog"  
# to a folder called ScrapedImages in the working directory  
# The function will return all images downloaded in a 30 second timeframe  
scraper.getAll("hot dog png", destination="ScrapedImages/", timeout=30)  
  
#Will return a list of up to 20 PIL Image objects from Google Images with keyword "chihuahua"  
#timeout argument is null if as_list is True  
images = scraper.getGoogle("chihuahua", as_list=True, max=20)  
  
#Make sure to close the browser when it is no longer being used  
scraper.closeBrowser()
```

# Details

Excav8r utilizes a headless Selenium Framework to scrape the results of some of the most powerful search engines around, making the process of downloading large datasets a breeze. 

As of now, Excav8r is capable of scraping the search engines of

 - **DuckDuckGo**
 - **Google**

## How to Install

**!!MUST HAVE GOOGLE CHROME INSTALLED FOR EXCAV8R TO WORK!!**
1. Clone repo to your project
2. Use "pip install requirements.txt" in the command line to install Excav8r's dependencies *(Assuming you have navigated to the "excav8r "folder).*
3. import Excav8r to your project

```python
import excav8r
scraper = excav8r.Excva8r()
```



## How to use

As of now Excav8r has 3 functions types:

 -  **getAll()** - Scrapes all supported search engines for images
 ```python
def getDuckDuckGo(search_term, destination='excav8r/', timeout=300, max=1000, as_list=False)
```
- **getGoogle()** & **getDuckDuckGo()** - Scrapes images from respective search engines
 ```python
def getDuckDuckGo(search_term, destination='excav8r/', timeout=300, max=1000, as_list=False)
```

## Understanding the functions' arguments 

 - **search_term** - The search term that will be entered into search engines
 - **destination** - the folder downloaded images will be saved to *('excav8r' by default)*
 - **timeout** - The # of seconds Excav8r will spend scraping and returning images *(300 seconds/5 minutes by default)*
 - **max** - The maximum # of photos that will be returned *(1000 by default)*
 - **as_list** - If true, a list of PIL Image objects will be returned instead of images being downloaded. When true, *timeout* argument is ignored. *(False by default)*

