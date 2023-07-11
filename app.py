from flask import Flask, render_template, request
import datetime
import certifi
import os

# reads key-value pairs from a .env file and can set them as environment variables.
from dotenv import load_dotenv

# pymongo allows to open the client side session to MongoDB that we can use to connect to DB
from pymongo import MongoClient

load_dotenv()  # populates the environment variables from the .env file

# You should not create a DB and store it directly in the main file b/c MongoClient() might run multiple times
# When you deploy the app. Sometimes deployment may run this file multiple times creating multiple mongo clients,
# but using app factory prevents it


# Use Flask's app factory
def create_app():
    app = Flask(__name__)
    # Pass-in mongoDB connection stream. It is a cluster representation.
    # In some cases you may want to configure PyMongo to use a specific set of CA (Certificate Authority) certificates.
    # This is most often the case when you are acting as your own certificate authority rather
    # than using server certificates signed by a well known authority.
    # The tlsCAFile option takes a path to a CA file
    client = MongoClient(
        os.getenv("MONGODB_URI"),
        tlsCAFile=certifi.where(),
    )

    # Connect to the database (microblog) that we created in our cluster
    # using .db allows to save the db connection in the app
    app.db = client.microblog

    # entries = []  # temp list to store my data

    @app.route(
        "/", methods=["GET", "POST"]
    )  # create an endpoint, methods = specify that this endpoint
    # may receive GET and POST requests
    def home():
        # Retrieve data (the entries collection) from DB
        # app.db.entries - access the entries collection
        # the .find method is passed with an empty dictionary to retrieve everything in DB
        # print([e for e in app.db.entries.find({})])

        # the request variable has a value when we are in a f-n that is currently responding to a request.
        if request.method == "POST":
            # then grap the entry using the NAME of the field (textarea) "content"
            entry_content = request.form.get("content")
            formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")

            # # Storing data as a tuple in our list
            # entries.append((entry_content, formatted_date))

            # Insert data to DB (as a python dictionary). pymongo will turn it into a dictionary
            app.db.entries.insert_one(
                {"content": entry_content, "date": formatted_date}
            )

        # Access the data stored in DB and
        # Reformat with list compression
        entries_with_date = [
            (
                entry["content"],
                entry["date"],
                datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%b %d"),
            )
            # it returns a Cursor object - collection of the document which is returned upon the find method execution
            # but it behaves as a list
            for entry in app.db.entries.find({})
        ]

        # To pass the entries to the template, create an entries variable in the template that contains a list of tuples
        # render_template will run when we go to this endpoint
        return render_template("home.html", entries=entries_with_date)

    return app
