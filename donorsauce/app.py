# import necessary libraries
import sqlite3
import os
import json
import psycopg2

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

DATABASE_URL = os.environ['DATABASE_URL']
# DATABASE_URL = "dbname=donorsauce user=postgres password=david8242"

# DATABASE_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user="postgres",pw="david8242",url="127.0.0.1:5432",db="donorsauce")
# print("database string= " + DATABASE_URL)
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
# db = SQLAlchemy(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL


# db = SQLAlchemy(app)

# # reflect an existing database into a new model
# Base = automap_base()
# # reflect the tables
# Base.prepare(db.engine, reflect=True)

# # Save references to each table
# Legislators = Base.classes.legislators
# Donors = Base.classes.donors
# Donations = Base.classes.donations

# -------------------------------------------------------------------------


# @app.before_first_request
# def setup():
#     # Recreate database each time for demo
#     db.drop_all()
#     db.create_all()

# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/summary")
def summary():
    return render_template("summary.html")

# create route that renders map.html template
@app.route("/map")
def mapLegislators():
    return render_template("map.html")

# create route that returns legislator data
@app.route("/api/legislators")
def legislators():

    # connect to database
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = con.cursor()
    # get all legislator data
    cur.execute("SELECT l.first_name, l.last_name, t.total, l.party, l.age, l.state, l.district, l.latitude, l.longitude, l.leg_type, l.url \
                FROM ( \
                    SELECT sum(amount) as total, legislator \
                    FROM donations \
                    GROUP BY legislator \
                ) t JOIN legislators l ON l.id=t.legislator")
    results = cur.fetchall()
    print(results[0])
    print(results)
    # get column names
    myKeys = results[0].keys()
    # build dictionary
    d = {}
    for i, stats in enumerate(results):
        d[i] = {}
        for ii, key in enumerate(myKeys):
            d[i][key] = tuple(stats)[ii]
        # add top donors to dictionary
        d[i]['top_donors'] = {}
        d[i]['top_donors_amounts'] = {}
        # take out naughty characters in name
        name_first = tuple(stats)[0].replace("'", "")
        name_last = tuple(stats)[1].replace("'", "")
        try:
            cur.execute(f"SELECT donors.name, donations.amount FROM legislators, donors, donations \
                WHERE legislators.id = donations.legislator AND donors.name = donations.donor AND \
                legislators.first_name = '{name_first}' AND legislators.last_name = '{name_last}' \
                ORDER BY donations.amount desc LIMIT 3")
            topDonors = tuple(cur.fetchall())
            for iii in range(len(topDonors)):
                d[i]['top_donors'][iii] = topDonors[iii][0]
                d[i]['top_donors_amounts'][iii] = '${:,.0f}'.format(topDonors[iii][1])
        except:
            d[i]['top_donors'][iii] = {}
            d[i]['top_donors_amounts'][iii] = {}

    return jsonify(d)

# create route that returns donor data
@app.route("/api/donors")
def donors():
    # connect to database
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = con.cursor()
    # get all legislator data
    cur.execute("SELECT * FROM donors")
    results = cur.fetchall()
    # get column names
    myKeys = results[0].keys()
    # build dictionary
    d = {}
    for stats in results:
        donor_name = tuple(stats)[0]
        # replace naughty characters in donor name
        donor_name = donor_name.replace("'", "")
        d[donor_name] = {}
        for i in list(range(1,len(myKeys))):
            d[donor_name][myKeys[i]] = tuple(stats)[i]
        # add top 10 recipients to donor entry
        d[donor_name]['recipients'] = {}
        d[donor_name]['recipients_amount'] = {}
        cur.execute(f"SELECT a.first_name, a.last_name, c.amount FROM legislators a, donors b, donations c \
               WHERE a.id = c.legislator AND b.name = c.donor AND b.name = '{donor_name}' \
               order by c.amount desc LIMIT 10")
        topRecipients = tuple(cur.fetchall())
        for i in range(len(topRecipients)):
            d[donor_name]['recipients'][i] = topRecipients[i][0] + " " + topRecipients[i][1]
            d[donor_name]['recipients_amount'][i] = '${:,.0f}'.format(topRecipients[i][2])
    return jsonify(d)

@app.route("/api/summary")
def summary_info():
    # connect to database
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    # con = psycopg2.connect(DATABASE_URL) #db?
    cur = con.cursor()
    # initialize dictionary
    d= {}

    # Query biggest recipients
    cur.execute("SELECT first_name, last_name, sum(amount) as total FROM donations, legislators \
    WHERE donations.legislator = legislators.id GROUP BY legislators.id \
    ORDER BY total DESC LIMIT 5")
    topRecipients = tuple(cur.fetchall())
    names = []
    amounts = []
    for i in range(len(topRecipients)):
        names.append(topRecipients[i][0] + " " + topRecipients[i][1])
        amounts.append(topRecipients[i][2])
    d["largest_recipients"] = names
    d["largest_recipients_amount"] = amounts

    # Query biggest donors
    cur.execute("SELECT name, total FROM donors ORDER BY total DESC LIMIT 5")
    topDonors = tuple(cur.fetchall())
    names = []
    amounts = []
    for i in range(len(topDonors)):
        names.append(topDonors[i][0])
        amounts.append(topDonors[i][1])
    d["biggest_donors"] = names
    d["biggest_donors_amount"] = amounts

    # Query ages and amount (Democrats)
    d["democrat_info"] = {}
    cur.execute("SELECT age, sum(amount) as total, first_name, last_name FROM donations, legislators \
    WHERE donations.legislator=legislators.id AND legislators.party='Democrat' \
    GROUP BY legislators.id ORDER BY age DESC")
    democratInfo = tuple(cur.fetchall())
    ages = []
    amounts = []
    names = []
    for i in range(len(democratInfo)):
        ages.append(democratInfo[i][0])
        amounts.append(democratInfo[i][1])
        names.append(democratInfo[i][2] + " " + democratInfo[i][3])
    d["democrat_info"]["ages"] = ages
    d["democrat_info"]["amounts"] = amounts
    d["democrat_info"]["names"] = names

    # Query ages and amount (Republicans)
    d["republican_info"] = {}
    cur.execute("SELECT age, sum(amount) as total, first_name, last_name FROM donations, legislators \
    WHERE donations.legislator=legislators.id AND legislators.party='Republican' \
    GROUP BY legislators.id ORDER BY age DESC")
    republicanInfo = tuple(cur.fetchall())
    ages = []
    amounts = []
    names = []
    for i in range(len(republicanInfo)):
        ages.append(republicanInfo[i][0])
        amounts.append(republicanInfo[i][1])
        names.append(republicanInfo[i][2] + " " + republicanInfo[i][3])
    d["republican_info"]["ages"] = ages
    d["republican_info"]["amounts"] = amounts
    d["republican_info"]["names"] =  names

    # Query ages and amount (Independent)
    d["independent_info"] = {}
    cur.execute("SELECT age, sum(amount) as total, first_name, last_name FROM donations, legislators \
    WHERE donations.legislator=legislators.id AND legislators.party='Independent' \
    GROUP BY legislators.id ORDER BY age DESC")
    independentInfo = tuple(cur.fetchall())
    ages = []
    amounts = []
    names = []
    for i in range(len(independentInfo)):
        ages.append(independentInfo[i][0])
        amounts.append(independentInfo[i][1])
        names.append(independentInfo[i][2] + " " + independentInfo[i][3])
    d["independent_info"]["ages"] = ages
    d["independent_info"]["amounts"] = amounts
    d["independent_info"]["names"] =  names

    return jsonify(d)

@app.route("/api/<first_name>+<last_name>")
def legislator_detail(first_name, last_name):
    # connect to database
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = con.cursor()
    # get legislator info
    statement = f"SELECT donors.name, donations.amount \
                FROM legislators, donors, donations \
                WHERE legislators.id = donations.legislator AND donors.name = donations.donor AND \
                legislators.first_name = '{first_name}' AND legislators.last_name = '{last_name}' \
                ORDER BY donations.amount desc"
    cur.execute(statement)
    results = tuple(cur.fetchall())
    # construct dictionary
    d = {}
    d['recipient'] = first_name + " " + last_name
    donorInfo = []
    for i in range(len(results)):
        n = results[i][0] + ", " + '${:,.0f}'.format(results[i][1])
        donorInfo.append(n)
    d["donors"] = donorInfo

    return jsonify(d)

@app.route("/api/test")
def test():
    # connect to database
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = con.cursor()
    # get legislator info
    statement = "SELECT first_name, last_name FROM legislators \
                WHERE legislators.first_name = 'Bernard' AND legislators.last_name = 'Sanders'"
    cur.execute(statement)
    results = tuple(cur.fetchall())
    d = results
    return jsonify(d)

if __name__ == "__main__":
    app.run()
