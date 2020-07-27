#Import Flask and other dependencies
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
#Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database into a new model
Base = automap_base()
#Reflect the tables
Base.prepare(engine, reflect=True)

#Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
#Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate and /api/v1.0/startdate/enddate<br/>"
        f"startdate/endate format YYYY-MM-DD"
    )


#Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create our session (link) from Python to the DB
    session = Session(engine)

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #Return the JSON representation of your dictionary.
    prcp_results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    date_prcp = []
    for date, prcp in prcp_results:
        date_prcp_dict = {}
        date_prcp_dict[date] = prcp
        date_prcp.append(date_prcp_dict)

    return jsonify(date_prcp)

#Station route
@app.route("/api/v1.0/stations")
def stations():
    #Create our session (link) from Python to the DB
    session = Session(engine)

    #Return a JSON list of stations from the dataset
    station_results = session.query(Station.station).all()

    session.close()

    #Convert list of tuples to normal list
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #Create our session (link) from Python to the DB
    session = Session(engine)

    #Query the dates and temperature observations of the most 
    #active station for the last year of data.
    station_temps = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
               filter(Measurement.station == "USC00519281").\
               filter(Measurement.date > '2016-08-22').all()

    session.close()
    #Create list of date and TOBS for most active station over last 12 months
    date_tobs = []
    for station, date, tobs in station_temps:
        date_tobs_dict = {}
        date_tobs_dict['Station'] = station
        date_tobs_dict[date] = tobs
        date_tobs.append(date_tobs_dict)

    return jsonify(date_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    #Create our session (link) from Python to the DB
    session = Session(engine)
    
    #When given the start only, calculate TMIN, TAVG, and TMAX 
    #for all dates greater than and equal to the start date.
    sel = [Measurement.date, 
       func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    station_stats = session.query(*sel).filter(Measurement.date >= str(start)).all()
    
    #Create list of date and TMIN, TMAX, TAVG
    temps = []
    for date, tmin, tmax, tavg in station_stats:
        temp_dict = {}
        temp_dict['TMIN'] = tmin
        temp_dict['TMAX'] = tmax
        temp_dict['TAVG'] = tavg
        temps.append(temp_dict)
    
    #Return Jsonified list
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    #Create our session (link) from Python to the DB
    session = Session(engine)
    
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
    #for dates between the start and end date inclusive.
    sel = [Measurement.date, 
       func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    station_stats = session.query(*sel).filter(Measurement.date >= str(start)).filter(Measurement.date <= str(end)).all()
    
    #Create list of date and TMIN, TMAX, TAVG
    temps = []
    for date, tmin, tmax, tavg in station_stats:
        temp_dict = {}
        temp_dict['TMIN'] = tmin
        temp_dict['TMAX'] = tmax
        temp_dict['TAVG'] = tavg
        temps.append(temp_dict)
    
    #Return Jsonified list
    return jsonify(temps)

     

if __name__ == "__main__":
    app.run(debug=True)