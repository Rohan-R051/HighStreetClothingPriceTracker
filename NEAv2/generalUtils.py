
"""
Rohan Ratnalingam
The Grammar School At Leeds

Quickfit.com
A-level Computer Science NEA 

utils.py

Classes:
AppTools
Scheduler

Overview:
Apptools class contains all methods that the quickfit app neeeds during runtime. For example hashing passwords, sending emails ect
Scheduler class is used to schedule and call a webscrape at 19:00 every day


METHODS: 
AppTools.__init__ - initialises an instance of an AppTool
hashPassword - takes a users password as an input hashes it and returns the hashed value to store in the database
update_price_history - updates the prices of all the products within the products table
process_products - for all product prices scraped, the prices are fomatted, appends a new price entry for that product into the price history table, sends an email if the new price is below the threshold price.
create_price_history_plot - creates a png image of a price against time graph for a particular product

Scheduler.__init__ - creates an instance of the scheduler class
schedule_function - schedules a web scrape for everyday at 19:00
background_scheduler - runs in the background through threading so that every second it checks is it 7pm and would then run a webscrape if true

"""







import time
import schedule
import smtplib
from scraping_functions import *
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend, which is non-interactive and thread-safe otherwise will not run on Mac-os
import matplotlib.pyplot as plt




class AppTools(object):
    def __init__(self,db,app,products,pricehistory,watchlist):
        self.db = db
        self.app = app
        self.Products = products
        self.PriceHistory = pricehistory
        self.Watchlist = watchlist
        scraper = Scraper()

    def hashPassword(self, password):
        """ hashing function to convert a password (string) to a hashed password (string) to save in a database

        params: takes the users password as a string as the only parameter

        returns: returns the users hashed password as a string

        """

        hashnums = ""
        hash = ""

        # uses numerical operators to convert different characters in the string to numbers and different characters
        hashnums += str(ord(password[0]) + ord(password[-1]))
        hashnums += str(ord(password[1]) * ord(password[2]))
        hashnums += str(round(ord(password[2]) + ord(password[-2]), -1))
        hashnums += str(ord(password[3]) ** 3)

        if ord(password[4]) >= ord(password[5]):
            hashnums += str(ord(password[4]))
        else:
            hashnums += str(ord(password[5]))

        for i in range(0, len(hashnums), 2):
            if int(hashnums[i:i + 2]) >= 65 and int(hashnums[i:i + 2]) <= 90:
                hash += chr(int(hashnums[i:i + 2]))
            else:
                hash += hashnums[i:i + 2]

        return hash


    # Send email to client (if current price <= threshold price)
    def send_mail(self, client_email, client_forename, product, threshold_price):
        """"sends a pre-formatted email to a customer

        params: takes the clients email address as a string, clients firstname as a string, the product the client wants to buy as a string and the threshold price as a float

        returns: none
        """


        # has email address below
        my_email = "quickfit.clothingprice@gmail.com"
        PASSWORD = "uksnjdvahyvknuwl"

        # opens connection using smtp library
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=my_email, password=PASSWORD)
            #creates a message
            msg_body = (f"Subject: Price Target Alert: {product}\n\n"
                        f"Dear {client_forename}\n\n"
                        f"Your item: {product} has just hit your watchlist price of £{threshold_price}\n\n"
                        f"Please log in to Quickfit to view your product\n")
            #sends message
            connection.sendmail(from_addr=my_email, to_addrs=client_email,
                                msg=msg_body.encode('utf-8'))

    def update_price_history(self):
        """
        Updates Database with latest prices

        Fetches all product data by running the scrape functions on every product
        then updates the respective prices table in the database.

        """


        with self.app.app_context():
            # Fetch all unique products (product_name and p_id) from the Watchlist table
            products = [
                (item.product.product_name, item.product.p_id, item.product.brand, item.product.product_url,
                item.client.email,
                item.client.forename, item.threshold_price)
                for item in
                self.Watchlist.query.all()]

            for product_name, p_id, brand, product_url, client_email, client_forename, threshold_price in products:
                if brand.lower() == 'nike':
                    try: # errors may be raised scrape functions only if a product is no longer on a website or some other unforseen reason, they are ignored.
                        products_data = scraper.nike_scrape(product_name)
                    except ScrapeException as e:
                        pass
                elif brand.lower() == 'rohan':
                    try:
                        products_data = scraper.scrape_rohan(product_url)
                    except ScrapeException as e:
                        pass
                elif brand.lower() == 'reiss':
                    try:
                        products_data = scraper.scrape_reiss(product_url)
                    except Exception as e:
                        pass
                elif brand.lower() == 'ishu':
                    try:
                        products_data = scraper.scrape_ishu(product_url)
                    except ScrapeException as e:
                        pass
                else:
                    continue
                # Match the scraped products with those in the watchlist
                print(products_data)
                for scraped_product in products_data:
                    # Modified condition to check p_id for Nike brand
                    if (brand.lower() == 'nike' and
                            scraped_product['title'] == product_name and
                            int(scraped_product['product_id']) == p_id):
                        self.process_product(scraped_product, product_name, threshold_price, client_email, client_forename)
                    elif brand.lower() == 'rohan' and scraped_product['title'] == product_name:
                        self.process_product(scraped_product, product_name, threshold_price, client_email, client_forename)
                    elif brand.lower() == 'reiss' and scraped_product['title'] == product_name:
                        self.process_product(scraped_product, product_name, threshold_price, client_email, client_forename)
                    elif brand.lower() == 'ishu' and scraped_product['title'] == product_name:
                        self.process_product(scraped_product, product_name, threshold_price, client_email, client_forename)

            self.db.session.commit()


    def process_product(self,scraped_product, product_name, threshold_price, client_email, client_forename):
        # Update current price in Product table and Add the new price to PriceHistory
        price = scraped_product['price']
        if isinstance(price, str):
            price = float(price.replace('£', '').replace(',', ''))
        else:
            price = float(price)

        # Find the product in the Watchlist table
        product = self.Products.query.filter_by(product_name=scraped_product['title']).first()

        if product:
            new_price_entry = self.PriceHistory(product_id=product.id, price=price)
            self.db.session.add(new_price_entry)

        # Check if the current price is less than or equal to the threshold price sends an email if true
        if price <= threshold_price:
            self.send_mail(client_email, client_forename, product_name, threshold_price)

    def create_price_history_plot(dates, prices):
        #creates a graph of prices against the dates recorded usiung matplotlib

        plt.figure()
        plt.plot(dates, prices)
        plt.title('Price History')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.xticks(rotation=45)
        plt.tight_layout()

        #saving the graph as an image to display on the webpage
        # Encode plot as a base64 string
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()  # Close the plot to free memory
        return plot_base64 #returns the image created



class Scheduler(object):
    def __init__(self):
        #initailises a instance of a scheduler. A scheduler has an apptools object to cause a webscrape 
        self.__time = "19:00"
        self.__qfTools = AppTools()

    def schedule_function(self):
        schedule.every().day.at(self.__time).do(self.__qfTools.update_price_history) #data is scraped every day at 7pm


    def background_scheduler(): 
        #runs in a thread in the background. It forever checks if it is 19:00 if so it does a webscrape then sleeps for a second
        while True:
            schedule.run_pending()
            time.sleep(1)
