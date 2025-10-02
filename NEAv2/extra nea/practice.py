import schedule
import time
import requests
import json
from bs4 import BeautifulSoup


def scrape():
    nike_scrape()
    urban_scrape()

def nike_scrape():
    count = 60
    anchor = 0
    country = 'GB'
    country_language = 'en-GB'
    query = 'dunk'
    url = f'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=241B0FAA1AC3D3CB734EA4B24C8C910D&country={country}&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace({country})%26filter%3Dlanguage({country_language})%26filter%3DemployeePrice(true)%26searchTerms%3D{query}%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{count}&language={country_language}&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D'


    html = requests.get(url=url)
    output = json.loads(html.text)
    print(output)

def urban_scrape():
    # Send an HTTP GET request to the product page
    url = 'https://www.shein.co.uk/Manfinity-Hypemode-Men-Slogan-Graphic-Tee-p-10466869-cat-1980.html?src_identifier=on%3DIMAGE_COMPONENT%60cn%3Dshopbycate%60hz%3DhotZone_1%60ps%3D5_1%60jc%3DitemPicking_100157210&src_module=Men&src_tab_page_id=page_home1694192537596&mallCode=1&imgRatio=3-4'
    url = 'https://www.shein.co.uk/Men-Slogan-Graphic-Tee-p-14384491-cat-1980.html?src_identifier=on%3DIMAGE_COMPONENT%60cn%3Dshopbycate%60hz%3DhotZone_1%60ps%3D5_1%60jc%3DitemPicking_100157210&src_module=Men&src_tab_page_id=page_home1694192537596&mallCode=1&imgRatio=3-4'
    url = 'https://www.shein.co.uk/Manfinity-EMRG-Men-Cotton-Letter-Floral-Print-Drop-Shoulder-Tee-p-15585485-cat-1980.html?src_identifier=fc%3DMen%60sc%3DSALE%60tc%3D0%60oc%3D0%60ps%3Dtab06navbar03%60jc%3DitemPicking_00511758&src_module=topcat&src_tab_page_id=page_goods_detail1694192804770&mallCode=1&imgRatio=3-4'
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    # Extract product details
    

    tags = soup.select('span')
    for span in tags:
        if '£' in span.text:
            price = span.text
            print(price)

    tags = soup.select('img')
    #print(tags)
    #for image in tags:
    #    print(image)

    img_tag = soup.find('img', {'data-src': True})
    data_src_value = img_tag['data-src'][2:]
    img_response = requests.get("http://"+data_src_value)

    if img_response.status_code == 200:
        with open('downloaded_image.jpg', 'wb') as file:
            file.write(img_response.content)
        print("Image downloaded and saved successfully.")
    else:
        print(f"Failed to download the image. Status code: {img_response.status_code}")
    




def scrape_rohan():
    #url inputted
    url = 'https://www.rohan.co.uk/mens/trousers-stretch-bags-convertible'
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup)

    tags = soup.find('div', class_="image-grid-item overflow-hidden rm-w-alternate")
    #print(tags)
    if tags:
        imgs = tags.find_all('img')
        data = []
        
        x = imgs[0]["data-srcset"]
        x = x.split(" ")
        for i in range(len(x)):
            if i % 2 == 0:
                print(x[i])
        #print(imgs)

    tags = soup.find('section', class_="product-data")
    print(tags)
    if tags:

        spans = tags.find('h1')
        name = spans.text.strip()
        print("Name: "+name)

        spans = tags.find('p')
        description = spans.text.strip()
        print("description: "+description)

        #price of a product not on sale
        print("normal price")
        price = getPrice_rohan('price price--withTax',tags)
        print(price)

        #n/a
        print("sale price")
        price = getPrice_rohan('price-now-label sale-color',tags)
        print(price)

        #before sale price
        print("non sale price")
        price = getPrice_rohan('price price--non-sale',tags)
        print(price)
        
        #during sale price
        print("sale price")
        price = getPrice_rohan('price price--withTax sale-color',tags)
        print(price)
        
        
def getPrice_rohan(class_Type,soup):
    spans = soup.find_all('span',class_=class_Type)

    for span in spans:
        if '£' in span.text:
            price = span.text
            return price.strip()




scrape_rohan()
    
