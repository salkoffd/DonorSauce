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

path_database = "DonorSauce.sqlite"

# -------------------------------------------------------------------------

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
    con = sqlite3.connect(path_database)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # get all legislator data
    cur.execute("SELECT first_name, last_name, sum(amount) as total, party, age, state, district, latitude, longitude, leg_type, url \
    from donations, legislators WHERE donations.legislator = legislators.id group by legislators.id")
    results = cur.fetchall()
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
    con = sqlite3.connect(path_database)
    con.row_factory = sqlite3.Row
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
    con = sqlite3.connect(path_database)
    con.row_factory = sqlite3.Row
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
    con = sqlite3.connect(path_database)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # get legislator info about donors
    statement = "SELECT donors.name, donations.amount \
                FROM legislators, donors, donations \
                WHERE legislators.id = donations.legislator AND donors.name = donations.donor AND \
                legislators.first_name = '{}' AND legislators.last_name = '{}' \
                ORDER BY donations.amount desc".format(first_name, last_name)
    cur.execute(statement)
    results = tuple(cur.fetchall())
    # construct dictionary
    d = {}
    donorInfo = []
    for i in range(len(results)):
        n = results[i][0] + ", " + '${:,.0f}'.format(results[i][1])
        donorInfo.append(n)
    d["donors"] = donorInfo

    # get legislator info about self
    cur.execute("SELECT party, age, state, district, leg_type, url FROM legislators \
                WHERE first_name = '{}' AND last_name = '{}'".format(first_name, last_name))
    results = cur.fetchall()
    # get column names
    myKeys = results[0].keys()
    print(myKeys)
    # build dictionary
    d['legislator_info'] = {}
    d['legislator_info']['name'] = first_name + " " + last_name
    for i in range(len(myKeys)):
        print(i)
        print(tuple(results)[0][i])
        d['legislator_info'][myKeys[i]] = tuple(results)[0][i]
    
    return jsonify(d)


if __name__ == "__main__":
    app.run()
