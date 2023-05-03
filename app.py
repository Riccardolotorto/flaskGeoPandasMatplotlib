from flask import Flask, render_template, request
app = Flask(__name__)

import pandas
import geopandas
import os
import matplotlib.pyplot as plt
import contextily

df = pandas.read_csv("http://servizi.apss.tn.it/opendata/FARM001.csv")
df = df.drop(df[df["LATITUDINE_P"].str.contains("-")].index)
from geopandas import GeoDataFrame
from shapely.geometry import Point
geometry = [Point(xy) for xy in zip(df["LONGITUDINE_P"], df["LATITUDINE_P"])]
df = df.drop(['LONGITUDINE_P', 'LATITUDINE_P'], axis=1)
farmacie = GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
comuni = geopandas.read_file("Comuni/Com01012023_g/Com01012023_g_WGS84.dbf")
comuni.crs

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/es1", methods = ["GET"])
def es1():
    farmacia = request.args.get("farmacia")
    farmaciaScelta = farmacie[farmacie["FARMACIA"].str.contains(farmacia.upper())].to_crs(3857)
    ax = farmaciaScelta.plot(figsize = (12, 12), color = "red", markersize = 10)
    contextily.add_basemap(ax)
    dir = "static/images"
    file_name = "mappa.png"
    save_path = os.path.join(dir, file_name)
    plt.savefig(save_path, dpi = 150)
    return render_template("mappa1.html")

@app.route("/es2")
def es2():
    comuniFarmacie = comuni.to_crs(3857)[comuni.to_crs(3857).intersects(farmacie.to_crs(3857).unary_union)]
    ax = comuniFarmacie.plot(figsize = (12, 12), edgecolor = "black", linewidth = 2, facecolor = "none")
    farmacie.to_crs(3857).plot(ax = ax, markersize = 10, color = "red")
    contextily.add_basemap(ax)

    dir = "static/images"
    file_name = "mappa2.png"
    save_path = os.path.join(dir, file_name)
    plt.savefig(save_path, dpi = 150)
    return render_template("mappa2.html")

@app.route("/es3")
def es3():
    farmacieDropped = farmacie.drop("COMUNE", axis = 1) 
    comuniFarmacie = comuni.to_crs(3857)[comuni.to_crs(3857).intersects(farmacie.to_crs(3857).unary_union)]
    joined = geopandas.sjoin(farmacieDropped.to_crs(3857), comuniFarmacie, predicate = "intersects", how="left")
    farmacie_per_comune = joined.groupby("COMUNE")[["FARMACIA"]].count().sort_values(by = "FARMACIA", ascending = False).reset_index().to_html()
    return render_template("3.html", tabella = farmacie_per_comune)

@app.route("/es4")
def es4():
    farmacieDropped = farmacie.drop("COMUNE", axis = 1) 
    comuniFarmacie = comuni.to_crs(3857)[comuni.to_crs(3857).intersects(farmacie.to_crs(3857).unary_union)]
    joined = geopandas.sjoin(farmacieDropped.to_crs(3857), comuniFarmacie, predicate = "intersects", how="left")
    farmacie_per_comune = joined.groupby("COMUNE")[["FARMACIA"]].count().sort_values(by = "FARMACIA", ascending = False).reset_index()
    finale = comuniFarmacie.merge(farmacie_per_comune, on = "COMUNE")
    ax = finale.plot(figsize = (12, 10), column = "FARMACIA", legend = True, alpha = 0.8, cmap = "Greens")
    farmacie.to_crs(3857).plot(ax = ax, markersize = 10, color = "red")
    contextily.add_basemap(ax)

    dir = "static/images"
    file_name = "mappa4.png"
    save_path = os.path.join(dir, file_name)
    plt.savefig(save_path, dpi = 150)
    return render_template("mappa4.html")

@app.route("/es5")
def es5():
    farmacieDropped = farmacie.drop("COMUNE", axis = 1) 
    comuniFarmacie = comuni.to_crs(3857)[comuni.to_crs(3857).intersects(farmacie.to_crs(3857).unary_union)]
    joined = geopandas.sjoin(farmacieDropped.to_crs(3857), comuniFarmacie, predicate = "intersects", how="left")
    farmacie_per_comune = joined.groupby("COMUNE")[["FARMACIA"]].count().sort_values(by = "FARMACIA", ascending = False).reset_index()
    dati = farmacie_per_comune["FARMACIA"]
    stringhe = farmacie_per_comune["COMUNE"]
    plt.figure(figsize=(16, 8))
    plt.pie(dati, labels=stringhe, autopct='%1.1f%%')

    dir = "static/images"
    file_name = "grafico5.png"
    save_path = os.path.join(dir, file_name)
    plt.savefig(save_path, dpi = 150)
    return render_template("grafico5.html")
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)