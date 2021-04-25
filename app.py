import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#setup database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#create an app
app = Flask(__name__)

@app.route("/")
def homepage():
    return (
        f"Welcome to the homepage!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    last_12_months = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date > '2016-08-22').all()
    
    session.close()
    
    precip_dict = {}
    for i in last_12_months:
        precip_dict[(i.date)] = i.prcp
        
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    stations = session.query(Station.station).all()
    
    session.close()
    
    stations_list = list(np.ravel(stations))
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    
    active_station_temp = session\
        .query(Measurement.date,Measurement.tobs,Measurement.station).\
        filter(Measurement.date > '2016-08-22',Measurement.station == 'USC00519281').all()    
   
    session.close()

    return jsonify(active_station_temp)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)

    start_date = str(dt.datetime.strptime(start,'%Y-%m-%d').date())

    start_temp = session\
            .query(func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()
    
    session.close()

    return jsonify(start_temp)

@app.route("/api/v1.0/<start>/<end>")
def temp_dates(start,end):
    session = Session(engine)
    
    start_date = str(dt.datetime.strptime(start,'%Y-%m-%d').date())
    end_date = str(dt.datetime.strptime(end,'%Y-%m-%d').date())

    start_end_temp = session\
            .query(func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    
    session.close()
    
    return jsonify(start_end_temp)
    
#define main behavior
if __name__ == "__main__":
    app.run(debug=True)
