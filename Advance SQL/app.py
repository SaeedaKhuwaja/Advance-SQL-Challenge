# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# list all the available routes
# route for homepage
@app.route("/")
def home():
    print("Server attempted to go to homepage...") #prints output in the console
    
    return(
        f"Welcome to Hawaii Climate Analysis Homepage<br/>"
        f"************************************************<br/>"
        f"Following are the available routes for Hawaii Climate Analysis:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Calculate Min, Max and Average temperature for all dates greater than and equal to given start date<br/>"
        f"/api/v1.0/Calculate Min, Max and Average temperature for all dates between given start date and given end date<br/>"
    )

# route for precipitation for last 12 years
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    query_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    # close the session
    session.close()

    # Convert the query results from your precipitation analysis to a dictionary using date 
    # as the key and prcp as the value.
    
    prcp_dic = {}
    for date, prcp in query_results:
        prcp_dic[date] = prcp

    # Return the JSON representation of your dictionary. 
    return jsonify(prcp_dic)

# route for stations
@app.route("/api/v1.0/stations")
def stations():

    # query for stations
    stations_list = session.query(Station.station, Station.name).all()
    
    # close the session
    session.close()

    # converting the results into dictionary
    station_dic = {}
    for station, name in stations_list:
        station_dic[station] = name
    
    # Returning the results as JSON
    return jsonify(station_dic)

# route for temperature observation
@app.route("/api/v1.0/tobs")
def tobs():

    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # query for temperature observations
    most_active = 'USC00519281'
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active).\
    filter(Measurement.date >= prev_year).all()
    
    session.close()

    # creating a list for the temperature observations
    tobs_list = []
    for date, temperature in results:
        tobs_dic = {}
        tobs_dic[date] = temperature
        tobs_list.append(tobs_dic)
    
    # Returning the results as JSON
    return jsonify(tobs_list)

# route for minimum temperature, the average temperature, and the maximum temperature for a specified start
@app.route("/api/v1.0/<start>")
def startdate(start):
    
    # convert the format of date into MMDDYYYY
    start = dt.datetime.strptime(start, "%m%d%Y")

    query_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()

    # convert the query results into a list
    start_date = []
    for min, max, avg in query_results:
        start_dic = {}
        start_dic["Minimum temperature"] = min
        start_dic["Maximum temperature"] = max
        start_dic["Average temperature"] = avg
        start_date.append(start_dic)

    # jsonify the results
    return jsonify(start_date)

# route for minimum temperature, the average temperature, and the maximum temperature between specific start and end date
@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
    
    # format the start and end dates
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    query_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    # convert the results into a list and return the results in json
    range_date = []
    for min, max, avg in query_results:
        range_dic = {}
        range_dic["Minimum temperature"] = min
        range_dic["Maximum temperature"] = max
        range_dic["Average temperature"] = avg
        range_date.append(range_dic)

    return jsonify(range_date)

if __name__ == '__main__':
    app.run(debug = True)
