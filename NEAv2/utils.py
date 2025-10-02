
import time
import schedule
import smtplib


def hashPassword(password):
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
def send_mail(client_email, client_forename, product, threshold_price):

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




