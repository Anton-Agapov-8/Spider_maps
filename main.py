import sys

import sqlite3
from io import BytesIO

import requests
from PIL import Image
from flask import Flask, render_template, redirect

app = Flask(__name__)
x = '39.488892379812896'
y = '52.52593551259488'
delta = "2"
view_type = "map"


@app.route('/')
def main():
    global x, y, delta, view_type
    map_params = {
        "ll": ",".join([str(x), str(y)]),
        "spn": ",".join([str(delta), str(delta)]),
        "size": "650,450",
        "l": view_type
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params, stream=True)
    print(type(response.content))
    im = Image.open(BytesIO(response.content))
    print(type(im.tobytes()))
    # with open('map.png') as mapimg:
        # pass

    return render_template("main.html",
                        image=f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}')
    # return render_template("main.html", image=im.tobytes())


@app.route('/ll_right')
def indexl():
    global x, delta
    d = 5 * (float(delta)) / 10
    if float(x) + d < 180:
        x = str(float(x) + d)
    return redirect('/')


@app.route('/ll_left')
def indexr():
    global x, delta
    d = 5 * (float(delta)) / 10
    if float(x) - d > -180:
        x = str(float(x) - d)
    return redirect('/')


@app.route('/ll_down')
def indexd():
    global y, delta
    d = 5 * (float(delta)) / 10
    if float(y) - d > -90:
        y = str(float(y) - d)
    return redirect('/')


@app.route('/ll_up')
def indexu():
    global y, delta
    d = 5 * (float(delta)) / 10
    if float(y) + d < 90:
        y = str(float(y) + d)
    return redirect('/')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
