import pandas as pd
import numpy as np
import os
import sqlalchemy
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import matplotlib.pyplot as plt
from flask import Flask, jsonify, render_template, request, redirect
import json
from datetime import datetime
from dateutil.parser import parse
import plotly.plotly as py
import plotly.graph_objs as go




#################################################
# Flask Setup
#################################################
app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///data.sqlite"
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '')
SQLAlchemy(app)



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///data.sqlite", echo=False)

conn = engine.connect()

inspector = inspect(engine)

Base = automap_base()
Base.prepare(engine,reflect=True)
Base.classes.keys()

class DPI(Base):
    __tablename__ = "DPI"
    __table_args__ = {"extend_existing":True}
    field1 = Column(Text,primary_key=True)

class FPSR(Base):
    __tablename__ = "FPSR"
    __table_args__ = {"extend_existing":True}
    DATE = Column(Text,primary_key=True)

class PCE(Base):
    __tablename__ = "PCE"
    __table_args__ = {"extend_existing":True}
    GeoName = Column(Text,primary_key=True)
    Line = Column(Text,primary_key=True)

class DEMO(Base):
    __tablename__ = "acs2015_county_data"
    __table_args__ = {"extend_existing":True}
    CensusId = Column(Integer,primary_key=True)

Base.prepare()
session = Session(engine)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
	return render_template('index.html')


@app.route("/PCElist")
def pcelist():
	description_List = [d.Description for d in session.query(PCE.Description).distinct()]
	
	return jsonify(description_List)
	

@app.route("/geonames")
def geonames():
	geoName_List = [g.GeoName for g in session.query(PCE.GeoName).distinct()]
	
	return jsonify(geoName_List)
	

@app.route("/regionData")
def regionpce1():
    sql = "select * from PCE where GeoName in ('Mid East', 'Far West', 'Southwest', 'Southeast', 'New England', 'Great Lakes', 'Plains', 'Rocky Mountain')"
    df = pd.read_sql(sql, engine)
    df.drop(['GeoFIPS', 'ComponentId', 'ComponentName', 'Line', 'IndustryClassification', 'Region'], axis=1, inplace=True)
    
    region_dict = []
    for d in df.to_dict(orient='records'):
	    region_dict.append(d)		

    reg_grp_dict = []
    import itertools
    from operator import itemgetter
    sorted_regions = sorted(region_dict, key=itemgetter('GeoName'))
    for key, group in itertools.groupby(sorted_regions, key=lambda x:x['GeoName']):
        reg_grp_dict.append(key)
        reg_grp_dict.append(list(group))
    
    return (jsonify(reg_grp_dict))
    # return(jsonify(region_dict))



@app.route("/pcedetail/<state>")
def pcedstate(state):
    pcedetail = {}
    for year in range (1997,2017,1):
        y=str(year)

        pcedetail[y] = {}
        sqlquery = str(r' select "Line", "Description", "' + y + r'" from PCE WHERE GeoName= "' + state + r'"')
        for row in conn.engine.execute(sqlquery):
            pcedetail[y][str(row.Description)] = row[2]
    return(jsonify(pcedetail))


	
if __name__ == '__main__':
    app.run(debug=True)
