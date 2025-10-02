from flask import Flask, render_template, request, redirect, flash, url_for
from bs4 import BeautifulSoup
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, URL
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from statscalc import *
from quicksort import *
from threading import Thread
import re
from scraping_functions import *
from utils import *



# Clothing Seacrch Form class which is used on the search page
#It is an instance of the form that is used
class ClothingSearchForm(FlaskForm):
    clothing_company = SelectField('Select Clothing Company', choices=[('nike', 'Nike'), (
        'rohan', 'Rohan'), ('reiss', 'Reiss'), ('ishu', 'Ishu')])  # User Selects which retailer they would like to use
    keyword = StringField('Nike Keyword Search', validators=[Optional()]) # Nike search bar to query nike products
    url = StringField('URL (Rohan / Reiss / Ishu)', validators=[Optional(), URL()]) # inputs URL for 3 other companies product pages
    submit = SubmitField('Search') # search button 


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


#gets the client id of a user for the flask login manager
@login_manager.user_loader
def load_user(client_id):
    return Clients.query.get(int(client_id))



# Create Database Model

#class for clients table
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


#class for Products table
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

#class for Price History table
class PriceHistory(db.Model):
    #initialising all the fields for the priceHistory table and setting their dataTypes
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<PriceHistory for Product %r at Price %r on %r>' % (self.product_id, self.price, self.date_recorded)

#class for Watchlist table
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


#instatiating key objects
scraper = Scraper()
Scheduler = Scheduler()
Tools = AppTools(db, app, Products, PriceHistory, Watchlist)



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
                         hashed_password=Tools.hashPassword(unhashed_password))
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
        if client_to_check.hashed_password == Tools.hashPassword(password): #check if the password inputted matches the stored password by comparing the hashed values
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
    #gets the way in which the user would like their products to be arranged in the portfolio e.g Alphabetically, cheapest to most expensive ect
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

    #returns the rendered my portfolio page with the users specific products and their latest prices added
    return render_template("myportfoliopage.html", watchlist_entries=watchlist_entries_list, latest_prices=latest_prices)


#the route that runs when a user wishes to update their prices by pressing the update prices button
@app.route('/updateprice', methods=['GET', 'POST'])
@login_required
def updateprice():
    Tools.update_price_history() #calls the update prices method
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
                products = scraper.nike_scrape(keyword)
            except ScrapeException as e: 
                flash(e.toString()) # raise a scrape exception to the user if an invlalid url/ query is inputted
        elif clothing_company == 'rohan':
            try:
                products = scraper.scrape_rohan(url)
            except ScrapeException as e:
                flash(e.toString())
        elif clothing_company == 'reiss':
            try:
                products = scraper.scrape_reiss(url)
            except ScrapeException as e:
                flash(e.toString())
        elif clothing_company == 'ishu':
            try:
                products = scraper.scrape_ishu(url)
            except ScrapeException as e:
                flash(e.toString())

    return render_template("search.html", form=form, products=products) #return the new rendered html page with an empty form and a list of products found from the webscrape


# the route that runs when a user wishes to add a product to their portfolio
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
        db.session.add(watchlist_item) #adds item to watchlist table

    db.session.commit()
    return redirect(request.referrer) # redirects user back to search page



#the route that runs when a user wants to view price statistics on a product
@app.route('/price_analysis', methods=['GET', 'POST'])
@login_required
def price_analysis():
    #gets the product id of the product
    product_id = request.form.get('product_id')
    if product_id is None:
        pass

    # Gets the product object
    product = Products.query.get(product_id)
    if product is None:
        pass

    #gets product name and image attributes from the product object
    product_name = product.product_name
    product_image = product.product_image

    #gets all the prices stored in the database about that particular product
    price_history_records = PriceHistory.query.filter_by(product_id=product_id).all()

    # Extract price_values from price history records
    dates = [record.date_recorded for record in price_history_records]
    price_values = [record.price for record in price_history_records]

    # Instantiate a statsCalc object
    calculator = statsCalc()

    # Calculate price statistics by use of the statsCalc
    mean_price = round(calculator.mean(price_values),2)
    variance , standard_deviation = calculator.standardDev(price_values)
    variance = round(variance,2)
    standard_deviation = round(standard_deviation,2)
    mode_price = calculator.mode(price_values)
    median_price = calculator.median(price_values)

    #Create graph of price change vs time
    plot_image = Tools.create_price_history_plot(dates, price_values)

    # renders the price analysis page with the correct data created as inputs to then be formatted onto the page
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


#the route that runs when a user wants to remove an item from their watchlist
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

# the route that runs when there is an Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404 #renders the 404 error page an displays it


# The route that runs when there is an Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


#what runs at run time
if __name__ == '__main__':
    #schedules a webscrape for everyday at 19:00
    Scheduler.schedule_function()

    # Start the background scheduler in a separate thread
    scheduler_thread = Thread(target=Scheduler.background_scheduler) 
    scheduler_thread.start()

    app.run(debug=True) #runs the flask app
