import requests
import json
from bs4 import BeautifulSoup
import re


def nike_scrape(query='basketball'):
    """ scrapes nike using an API to get product data
    the API works by entering a query and it returns all the products that show up for that query

    params: takes a query as a parameter, this query is a string of the product/range that should be looked up by the API

    returns: returns a dictionary containing all the product data found

    """
    count = 60
    anchor = 0
    country = 'GB'
    country_language = 'en-GB'
    url = f'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=241B0FAA1AC3D3CB734EA4B24C8C910D&country={country}&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace({country})%26filter%3Dlanguage({country_language})%26filter%3DemployeePrice(true)%26searchTerms%3D{query}%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{count}&language={country_language}&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D'

    html = requests.get(url=url) # uses requests and the nike api to search for a product
    output = json.loads(html.text) # data is formatted into the using json

    products_data = []
    try:
        # gets product data for all products 
        for product in output.get('data', {}).get('products', {}).get('products', []):
            if 'colorways' in product and product['colorways']:
                title = product.get('title', '')
                subtitle = product.get('subtitle', '')
                price_data = product['colorways'][0].get('price', {})
                price = price_data.get('currentPrice', '')
                product_id = product.get('pid', '')
                image = product['colorways'][0].get('images', {}).get('squarishURL', '')
                products_data.append(
                    {'title': title, 'subtitle': subtitle, 'price': price, 'image': image, 'product_id': product_id})
    except:
        # if an error occurs because the query was invalid a scrape exeption is raised and the used is prompted to enter a different query
        raise ScrapeException("No Nike products named " + query)

    return products_data


def scrape():
    nike_scrape()


def getPrice(class_Type, soup):
    """used to strip the price products of their £ sign

    params: takes the soup tags of a webpage as input

    returns: returns the price as a float without the price sign if a price is found, else None
    
    """
    spans = soup.find_all('span', class_=class_Type)

    for span in spans:
        if '£' in span.text:
            price = span.text.replace('£', '').strip()  # remove the £ sign
            try:
                return float(price)  # Convert price to a float
            except ValueError:
                return None  # return None if conversion fails


def scrape_rohan(url):
    """ gets product data using webscraping from Rohan.com by inputting the URL of the users desired product

    params: takes the url of the product page as input

    returns: returns a dictionary of the product data collected

    """

    try:
        response = requests.get(url)
    except:
        # if an error is raised when scraping from the URL an exception is raised 
        raise ScrapeException('Invalid Rohan URL')

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    prices = []
    image = None

    tags = soup.find('div', class_="image-grid-item overflow-hidden rm-w-alternate")

    if tags == None:
        raise ScrapeException('Invalid Rohan URL')

    if tags:
        img = tags.find('img')  # directly find the first image tag
        if img:
            if img.has_attr('src'):
                image = img['src']  # get the image URL from the src attribute
            elif img.has_attr('data-srcset'):
                image = img['data-srcset'].split(" ")[0]  # get the first URL from the data-srcset attribute

    tags = soup.find('section', class_="product-data")

    if tags:
        name = tags.find('h1').text.strip()
        description = tags.find('p').text.strip()

        # price of a product not on sale
        normal_price = getPrice('price price--withTax', tags)
        if normal_price:
            prices.append(normal_price)

        sale_price = getPrice('price-now-label sale-color', tags)
        if sale_price:
            prices.append(sale_price)

        # before sale price
        non_sale_price = getPrice('price price--non-sale', tags)
        if non_sale_price:
            prices.append(non_sale_price)

        # during sale price
        during_sale_price = getPrice('price price--withTax sale-color', tags)
        if during_sale_price:
            prices.append(during_sale_price)

    price = min(prices)

    # returns product data as a dictionary
    products_data = [
        {'title': name, 'subtitle': description, 'price': price, 'image': image, 'product_id': 0}]
    return products_data


def scrape_ishu(url):
    """ gets product data using webscraping from Ishu.com by inputting the URL of the users desired product

     params: takes the url of the product page as input

    returns: returns a dictionary of the product data collected

    """

    #validation to see whether url is valid
    try:
        response = requests.get(url)
    except:
        raise ScrapeException("Invalid Ishu URL") #error raised if invalid URL inputted

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    tags = soup.find('span', class_="money")

    #used to remove £ sign from price string to prevent errors
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", tags.text)
    if numbers:
        product_price = float(numbers[0]) #converts price string to an integer
    else:
        product_price = None

    tags = soup.find('h1', class_="product-title")
    try: # error often raised here if an invalid wep page is inputted so exception is raised
        name = tags.text.strip() #gets product name
    except:
        raise ScrapeException('Invalid Ishu URL')

    # finds the image url of the product
    tags = soup.find_all('a', class_='fancybox')
    x = tags[0]["href"]
    image = "https:" + x

    # formats product data as a dictionary to return
    products_data = [
        {'title': name, 'subtitle': '', 'price': product_price, 'image': image, 'product_id': 0}]

    return products_data


def scrape_reiss(url):
    """ gets product data using webscraping from Reiss.com by inputting the URL of the users desired product

     params: takes the url of the product page as input

    returns: returns a dictionary of the product data collected

    """

    #errors may be raised here if an invalid URL is inputted
    try:
        response = requests.get(url)
    except:
        raise ScrapeException("Invalid Reiss URL")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')


    tags = soup.find('h1', class_='product-description')

    #raises error if the product couldn't be found
    if tags == None:
        raise ScrapeException('Invalid Reiss URL')

    #gets product name 
    product_name = tags.text

    #gets the product price
    tags = soup.find('div', class_='Price')
    if tags:
        spans = tags.find('span')
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", spans.text)
        if numbers:
            product_price = float(numbers[0])
        else:
            product_price = None

    # finds the thumbnail image of the product
    imgs = soup.find_all('img')
    src = []
    for img in imgs:
        src.append(img.get('src'))

    images = []
    for item in src:
        if item[0:6] == "https:":
            images.append(item)

    # returns the product data as a dictionary
    products_data = [
        {'title': product_name, 'subtitle': '', 'price': product_price, 'image': images[0], 'product_id': 0}]

    return products_data


class ScrapeException(Exception):
    # scrape exception raised when scrape doesnt work
    # error value entered when defined depending on which function it is called in
    def __init__(self, value):
        self.__value = value

    def toString(self):
        return self.__value
