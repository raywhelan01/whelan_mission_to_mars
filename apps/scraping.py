# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup

import pandas as pd

#Master method
def scrape_all():
    
    import datetime as dt
    
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemi_pics": mars_hemi_pics(browser)
    }
    return data


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())


#Create the Mars news method
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
    
    return news_title, news_p

#Featured image scraper method
def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)


    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # Find the relative image url
    try:
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    return img_url

#Mars facts function
def mars_facts():

    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns=['Description', 'value']
    df.set_index('Description', inplace=True)
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

#Challenge: Hemisphere images
def mars_hemi_pics(browser):

    # Visit hemispheres URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    links_found = browser.find_link_by_partial_text('Enhanced')
    hemispheres = []
    for link in links_found:
        print(link)
        browser.find_link_by_partial_text('Enhanced').click()
        hemi_soup = BeautifulSoup(browser.html, 'html.parser')
        hemi_title = hemi_soup.find("h2", class_='title').get_text()
        hemi_rel = hemi_soup.find('img', class_='wide-image').get("src")
        hemi_url = f'https://astrogeology.usgs.gov{hemi_rel}'
        hemi_dict = {'img_url': hemi_url, 'title': hemi_title}
        hemispheres.append(hemi_dict)
    return(hemispheres)
