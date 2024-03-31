import sys

import sqlite3
from io import BytesIO

import requests
from PIL import Image, ImageDraw
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
x = '39.488892379812896'
y = '52.52593551259488'
delta = "2"
view_type = "map"


def coords_to_str(coords):
    coords.sort()
    coords.append(coords[0])
    return ','.join(map(lambda x: ','.join(map(str, x)), coords))


@app.route('/')
def main():
    global x, y, delta, view_type
    points_coords = [(39, 53), (40, 55), (38, 53), (37, 54), (35, 54.5)]
    points_coords_str = coords_to_str(points_coords)
    point_color = "FF1000FF"
    point_color2 = "FF100088"
    w_line = 2
    map_params = {
        "ll": ",".join([str(x), str(y)]),
        "spn": ",".join([str(delta), str(delta)]),
        "size": "650,450",
        "l": view_type,
        "pl": f"c:{point_color},f:{point_color2},w:{w_line},{points_coords_str}"
    }
    return render_template("main.html",
                           image=f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}&pl={map_params["pl"]}')


@app.route('/ll_right')
def indexl():
    global x, delta
    d = 2 * (float(delta)) / 10
    if float(x) + d < 180:
        x = str(float(x) + d)
    return redirect('/')


@app.route('/ll_left')
def indexr():
    global x, delta
    d = 2 * (float(delta)) / 10
    if float(x) - d > -180:
        x = str(float(x) - d)
    return redirect('/')


@app.route('/ll_down')
def indexd():
    global y, delta
    d = 2 * (float(delta)) / 10
    if float(y) - d > -90:
        y = str(float(y) - d)
    return redirect('/')


@app.route('/ll_up')
def indexu():
    global y, delta
    d = 2 * (float(delta)) / 10
    if float(y) + d < 90:
        y = str(float(y) + d)
    return redirect('/')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
