from flask import Flask, render_template, request, redirect, flash, url_for
from bs4 import BeautifulSoup
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, URL
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
import json
import requests
import time
import schedule
import smtplib
from statscalc import *
from quicksort import *
from threading import Thread
import re
from scraping_functions import nike_scrape, scrape_rohan, scrape_ishu, scrape_reiss, ScrapeException
from utils import hashPassword, send_mail
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend, which is non-interactive and thread-safe otherwise will not run on Mac-os
import matplotlib.pyplot as plt


def update_price_history():
    """
    Updates Database with latest prices

    Fetches all product data by running the scrape functions on every product
    then updates the respective prices table in the database.

    """


    with app.app_context():
        # Fetch all unique products (product_name and p_id) from the Watchlist table
        products = [
            (item.product.product_name, item.product.p_id, item.product.brand, item.product.product_url,
             item.client.email,
             item.client.forename, item.threshold_price)
            for item in
            Watchlist.query.all()]

        for product_name, p_id, brand, product_url, client_email, client_forename, threshold_price in products:
            if brand.lower() == 'nike':
                try: # errors may be raised scrape functions only if a product is no longer on a website or some other unforseen reason, they are ignored.
                    products_data = nike_scrape(product_name)
                except ScrapeException as e:
                    pass
            elif brand.lower() == 'rohan':
                try:
                    products_data = scrape_rohan(product_url)
                except ScrapeException as e:
                    pass
            elif brand.lower() == 'reiss':
                try:
                    products_data = scrape_reiss(product_url)
                except Exception as e:
                    pass
            elif brand.lower() == 'ishu':
                try:
                    products_data = scrape_ishu(product_url)
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
                    process_product(scraped_product, product_name, threshold_price, client_email, client_forename)
                elif brand.lower() == 'rohan' and scraped_product['title'] == product_name:
                    process_product(scraped_product, product_name, threshold_price, client_email, client_forename)
                elif brand.lower() == 'reiss' and scraped_product['title'] == product_name:
                    process_product(scraped_product, product_name, threshold_price, client_email, client_forename)
                elif brand.lower() == 'ishu' and scraped_product['title'] == product_name:
                    process_product(scraped_product, product_name, threshold_price, client_email, client_forename)

        db.session.commit()


def process_product(scraped_product, product_name, threshold_price, client_email, client_forename):
    # Update current price in Product table and Add the new price to PriceHistory
    price = scraped_product['price']
    if isinstance(price, str):
        price = float(price.replace('£', '').replace(',', ''))
    else:
        price = float(price)

    # Find the product in the Watchlist table
    product = Products.query.filter_by(product_name=scraped_product['title']).first()

    if product:
        new_price_entry = PriceHistory(product_id=product.id, price=price)
        db.session.add(new_price_entry)

    # Check if the current price is less than or equal to the threshold price sends an email if true
    if price <= threshold_price:
        send_mail(client_email, client_forename, product_name, threshold_price)


def readFromClients():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()

    cursor.close()
    conn.close()
    return clients

# Schedule the update_price_history function
def schedule_function():
    schedule.every().day.at("19:00").do(update_price_history) #data is scraped every day at 7pm



def background_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

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
    return plot_base64


class ClothingSearchForm(FlaskForm):
    clothing_company = SelectField('Select Clothing Company', choices=[('nike', 'Nike'), (
        'rohan', 'Rohan'), ('reiss', 'Reiss'), ('ishu', 'Ishu')])  # Add more choices as necessary
    keyword = StringField('Nike Keyword Search', validators=[Optional()])
    url = StringField('URL (Rohan / Reiss / Ishu)', validators=[Optional(), URL()])
    submit = SubmitField('Search')


app = Flask(__name__)
# Secret Key
app.config['SECRET_KEY'] = 'Ell!sjdfjksdnbf'
# Add Database (URI - Uniform Resource Indicator)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///quickfit.db"

# Initialize the Database
db = SQLAlchemy(app)

# Flask Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(client_id):
    return Clients.query.get(int(client_id))


# Create Database Model

class Clients(db.Model, UserMixin):
    #initialising all the fields for the clients table and setting their dataTypes
    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    hashed_password = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    #establishing a relationship with the watchlist table
    watchlist = db.relationship('Watchlist', backref='client', lazy=True)

    def __repr__(self):
        return '<Name %r>' % self.forename


class Products(db.Model):
    #initialising all the fields for the products table and setting their dataTypes
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    p_id = db.Column(db.Integer, nullable=True)
    product_image = db.Column(db.String(500), nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    product_url = db.Column(db.String(500), nullable=True)

    # This establishes the relationship with PriceHistory
    price_history = db.relationship('PriceHistory', backref='product', lazy=True)

    watchlists = db.relationship('Watchlist', backref='product', lazy=True)

    def __repr__(self):
        return '<Product %r>' % self.product_name


class PriceHistory(db.Model):
    #initialising all the fields for the priceHistory table and setting their dataTypes
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<PriceHistory for Product %r at Price %r on %r>' % (self.product_id, self.price, self.date_recorded)


class Watchlist(db.Model):
    #initialising all the fields for the Watchlist table and setting their dataTypes
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    threshold_price = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return '<Watchlist for Product %r by Client %r>' % (self.product_id, self.client_id)


#creating the database 
with app.app_context():
    db.create_all()

#the intital route visited which renders the login/registration page and displays it to a user
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("homepage.html")


@app.route('/forgottenpassword')
def fp():
    return render_template('forgottenpassword.html')

#the route that is run when a user wants to register for a quickfit account
@app.route('/submit_form', methods=['GET', 'POST'])
def submit_form():
    #gets any client that already exists with the email inputted
    client = Clients.query.filter_by(email=request.form['email']).first()
    #gets the password inputted
    unhashed_password = request.form['password']
    if client is None:
        #creates an entry of a new client in the clients table if the user doesn't already have an account
        #note the password inputted is hashed before being saved to the database
        client = Clients(forename=request.form['forename'],
                         surname=request.form['surname'],
                         email=request.form['email'],
                         hashed_password=hashPassword(unhashed_password))
        db.session.add(client)
        db.session.commit()
        flash("You have been successfully registered")
        login_user(client) #logs in the user
        return redirect(url_for('myportfolio')) #redirects a user to their my portfolio page
    
    else: # if the client is already registered flash an error message
        flash("You have already registered with that email. Please log-in")
        return redirect(url_for('index'))


#the route that is run when a user logs in to a pre-existing account
@app.route('/submit_login_form', methods=['GET', 'POST'])
def submit_login_form():
    #get the email and password from the login form 
    email = request.form['email']
    password = request.form['password']

    #error checking to see if the password is too short 
    if len(password) <= 6:
        flash('invalid username or password')
        return redirect(url_for('index'))

    #search for the client in the database by email address
    client_to_check = Clients.query.filter_by(email=email).first()

    if client_to_check:
        if client_to_check.hashed_password == hashPassword(password): #check if the password inputted matches the stored password by comparing the hashed values
            login_user(client_to_check) 
            return redirect(url_for('myportfolio', client_id=client_to_check.id)) #if valid log in user and redirect them to their portfolio page
        else:
            flash("incorrect username or password!") # if incorrect password inputted flash an error message
            return redirect(url_for('index'))
    else:
        flash("Incorrect username or password!") #if no such client exists then flash an error message
        return redirect((url_for('index')))


#the route that is run when a user wishes to visit their my portfolio page
@app.route('/myportfoliopage', methods=['GET', 'POST'])
@login_required
def myportfolio():
    sort = request.args.get('sort')
    watchlist_entries = current_user.watchlist
    # Convert to list for sorting
    watchlist_entries_list = list(watchlist_entries)

    # Retrieve the latest price for each watchlist entry
    latest_prices = {}
    for entry in watchlist_entries:
        latest_price = db.session.query(PriceHistory).filter_by(product_id=entry.product_id).order_by(
            PriceHistory.date_recorded.desc()).first()
        if latest_price:
            latest_prices[entry.id] = latest_price.price
        else:
            latest_prices[entry.id] = None

    # Sorting according to user choice using quicksort functions
    sorter = QuickSorter()
    if sort == 'price_desc':
        sorter.quicksort(watchlist_entries_list, 0, len(watchlist_entries_list) - 1,
                  key=lambda entry: latest_prices.get(entry.id, 0), reverse=True) #note reverse is true to sort the prices the opposite way to ascendingly
    elif sort == 'price_asc':
        sorter.quicksort(watchlist_entries_list, 0, len(watchlist_entries_list) - 1,
                  key=lambda entry: latest_prices.get(entry.id, 0))
    elif sort == 'alpha':
        sorter.quicksort(watchlist_entries_list, 0, len(watchlist_entries_list) - 1,
                  key=lambda entry: entry.product.product_name)

    return render_template("myportfoliopage.html", watchlist_entries=watchlist_entries_list, latest_prices=latest_prices)


@app.route('/updateprice', methods=['GET', 'POST'])
@login_required
def updateprice():
    update_price_history()
    return redirect(request.referrer)



#the route that is run when the user vistits the search page 
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    #the search for products form is set up to get any URLs and the retailer name of the website 
    form = ClothingSearchForm()

    #products initialised to an empty list as no products have been found from a webscrape yet 
    products = []

    if form.validate_on_submit():
        #once the form is submitted extract all data that was inputted
        clothing_company = form.clothing_company.data
        keyword = form.keyword.data
        url = form.url.data

        #do nike scrape if nike was selected or rohan scrape if rohan is selected ect
        if clothing_company == 'nike': 
            try:
                #gets all the products by use of webscraping functions
                products = nike_scrape(keyword)
            except ScrapeException as e: 
                flash(e.toString()) # raise a scrape exception to the user if an invlalid url/ query is inputted
        elif clothing_company == 'rohan':
            try:
                products = scrape_rohan(url)
            except ScrapeException as e:
                flash(e.toString())
        elif clothing_company == 'reiss':
            try:
                products = scrape_reiss(url)
            except ScrapeException as e:
                flash(e.toString())
        elif clothing_company == 'ishu':
            try:
                products = scrape_ishu(url)
            except ScrapeException as e:
                flash(e.toString())

    return render_template("search.html", form=form, products=products) #return the new rendered html page with an empty form and a list of products found from the webscrape


@app.route('/addtowatchlist', methods=['GET', 'POST'])
@login_required
def addtowatchlist():
    # Check if the product already exists in the Products table
    product = Products.query.filter_by(product_name=request.form.get('title')).first()

    # If the product doesn't exist in the Products table, add it
    if not product:
        new_product = Products(
            product_name=request.form.get('title'),
            description=request.form.get('subtitle'),
            p_id=request.form.get('product_id'),
            product_image=request.form.get('image'),
            brand=request.form.get('brand'),
            product_url=request.form.get('product_url'),
        )
        db.session.add(new_product)
        db.session.flush()  # Flush the session to get the ID of the newly added product

        # Add the current price to PriceHistory
        price = float(request.form.get('price').replace('£', '').replace(',', ''))
        price_entry = PriceHistory(product_id=new_product.id, price=price)
        db.session.add(price_entry)

        # Add the product to the user's Watchlist
        watchlist_item = Watchlist(
            product_id=new_product.id,
            client_id=current_user.id,
            threshold_price=round(float(request.form.get('target_price')), 2)
        )
        db.session.add(watchlist_item)
    else:
        # If product exists, just add it to Watchlist (assuming that the user might want to set different threshold
        # prices for the same product)
        watchlist_item = Watchlist(
            product_id=product.id,
            client_id=current_user.id,
            threshold_price=float(request.form.get('target_price'))
        )
        db.session.add(watchlist_item)

    db.session.commit()
    return redirect(request.referrer)


@app.route('/price_analysis', methods=['GET', 'POST'])
@login_required
def price_analysis():
    product_id = request.form.get('product_id')
    if product_id is None:
        pass

    # Get the name of the product
    product = Products.query.get(product_id)
    if product is None:
        pass

    product_name = product.product_name
    product_image = product.product_image

    price_history_records = PriceHistory.query.filter_by(product_id=product_id).all()

    # Extract price_values from price history records
    dates = [record.date_recorded for record in price_history_records]
    price_values = [record.price for record in price_history_records]

    # Instantiate a statsCalc object
    calculator = statsCalc(len(price_values)*3)

    # Calculate price statistics
    #mean_price = round(calculator.mean(price_values),2)
    mean_price = round(db.session.query(func.avg(PriceHistory.price).label('average_price')).join(Products, Products.id == PriceHistory.product_id).filter(Products.product_name == product_name).scalar(),2)

    variance , standard_deviation = calculator.standardDev(price_values)
    variance = round(variance,2)
    standard_deviation = round(standard_deviation,2)
    mode_price = calculator.mode(price_values)
    median_price = calculator.median(price_values)

    #Create graph of price change vs time
    plot_image = create_price_history_plot(dates, price_values)

    print(product_image)
    return render_template('price_analysis.html',
                           product_name=product_name,
                           product_image=product_image,
                           mean_price=mean_price,
                           variance=variance,
                           standard_deviation=standard_deviation,
                           mode_price=mode_price,
                           median_price=median_price,
                           plot_image=plot_image
                           )


@app.route('/removefromwatchlist', methods=['GET', 'POST'])
@login_required
def removefromwatchlist():
    product_id = request.form.get('product_id')

    # Fetch the product details using product_id
    product = Products.query.get(product_id)

    # If product doesn't exist, just redirect
    if not product:
        return redirect(request.referrer)

    # Check if there are other entries with the same product_id in the watchlist
    other_entries = Watchlist.query.filter_by(product_id=product_id).all()

    # Remove the current user's entry for this product from their Watchlist
    user_watchlist_entry = Watchlist.query.filter_by(product_id=product_id, client_id=current_user.id).first()
    if user_watchlist_entry:
        db.session.delete(user_watchlist_entry)

    # If there's only one entry (the one we've just deleted), then proceed with deletion
    if len(other_entries) == 1:
        # First, delete the price history associated with the product
        PriceHistory.query.filter_by(product_id=product_id).delete()

        # Now delete the product itself from the Products table
        db.session.delete(product)

    # Commit the changes to the database
    db.session.commit()

    return redirect(request.referrer)


# Logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Error Handling

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == '__main__':
    schedule_function()

    # Start the background scheduler in a separate thread
    scheduler_thread = Thread(target=background_scheduler)
    scheduler_thread.start()
    app.run(debug=True) #runs the flask app
