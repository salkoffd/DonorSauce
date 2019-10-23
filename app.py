# import necessary libraries
import sqlite3
import os
import json

from sqlalchemy import func

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

path_database = os.path.join("db", "DonorSauce.sqlite")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db/DonorSauce.sqlite"

db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
Legislators = Base.classes.legislators
Donors = Base.classes.donors
Donations = Base.classes.donations

# -------------------------------------------------------------------------

@app.before_first_request
def setup():
    # Recreate database each time for demo
    db.drop_all()
    db.create_all()

# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")

# create route that renders map.html template
@app.route("/map")
def mapLegislators():
    return render_template("map.html")

# create route that returns legislator data
@app.route("/api/legislators")
def legislators():

    # connect to database
    con = sqlite3.connect(path_database)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # get all legislator data
    cur.execute("SELECT * FROM legislators")
    results = cur.fetchall()
    # get column names
    myKeys = results[0].keys()
    # build dictionary
    d = {}
    for i, stats in enumerate(results):
        d[i] = {}
        for ii, key in enumerate(myKeys):
            d[i][key] = tuple(stats)[ii]
    return jsonify(d)



if __name__ == "__main__":
    app.run()
