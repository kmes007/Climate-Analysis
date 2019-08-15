from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from datetime import datetime

import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# Flask
app = Flask(__name__)

# Create routes
@app.route("/")
def welcome():
    return """
    Welcome to the Hawaii Climate API!
    Available endpoints: <br>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/&lt;start&gt; where start is a date in YYYY-MM-DD format <br> 
    /api/v1.0/&lt;start&gt;/&lt;end&gt; where start and end are dates in YYYY-MM-DD format
    """

@app.route("/api/v1.0/precipitation")
def precip():
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= "2016-08-23").\
    filter(Measurement.date <= "2017-08-23").all()

    results_dict = []
    for row in results:
        date_dict = {}
        date_dict[row.date] = row.prcp
        results_dict.append(date_dict)

    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    results_list = list(np.ravel(results))

    return jsonify(results_list)

@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23").\
        filter(Measurement.date <= "2017-08-23").all()

    results_list = list(np.ravel(results))

    return jsonify(results_list)


@app.route("/api/v1.0/<start>")
def start_date(start):
    end_date = session.query(func.max(Measurement.date)).all()[0][0]
    temps = calc_temps(start, end_date)
    temps_list = list(np.ravel(temps))
    return jsonify(temps_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    temps = calc_temps(start, end)
    temps_list = list(np.ravel(temps))
    return jsonify(temps_list)

if __name__ == '__main__':
    app.run(debug=True)
    

# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def station_name():
    # Query all station names
    station_name_results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    station_name_list = list(np.ravel(station_name_results))

    # Jsonify all_tobs
    return jsonify(station_name_list)

# Return a JSON list of Temperature Observations (tobs) for the previous year

@app.route("/api/v1.0/tobs")
def tobs():
    #Find last date in database
    Last_Year_Observation = datetime.date(2017, 8, 23) - datetime.timedelta(days=7*52)

    Last_Year_Observation

    # Query temp observations
    tobs_results = session.query(Measurement.tobs).filter(Measurement.date > Last_Year_Observation).all()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs_results))

    # Jsonify all_tobs
    return jsonify(tobs_list)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<startdate>")
def start_date(startdate):
    #Parse the date 
    Srt_Date = datetime.datetime.strptime(startdate,"%Y-%m-%d")

    # Calculate summary stats
    summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
    filter(Measurement.date >= St_Date).all()

    summary = list(np.ravel(summary_stats))

    # Jsonify summary
    return jsonify(summary)

# Same as above with the inclusion of an end date
@app.route("/api/v1.0/<startdate>/<enddate>")
def daterange(startdate,enddate):
    #Parse the date 
    Srt_Date = datetime.datetime.strptime(startdate,"%Y-%m-%d")
    End_Date = datetime.datetime.strptime(enddate,"%Y-%m-%d")

    # Calculate summary stats
    summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
    filter(Measurement.date.between(St_Date,En_Date)).all()
    
    summary = list(np.ravel(summary_stats))

    # Jsonify summary
    return jsonify(summary)


if __name__ == '__main__':
    app.run(debug=True)