import sys

from numpy import cos, arccos, deg2rad, rad2deg, pi, sin, tan, arcsin
from flask import Flask, render_template, redirect, url_for
from data import db_session
from data.Spiders import Spiders

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bober'
x = '39.488892379812896'
y = '52.52593551259488'
delta_list = ['8', '4', '2', '1', '0.5', '0.25', '0.125', '0.0625', '0.03125', '0.015265', '0.0078125', '0.00390625', '0.001953125', '0.0009765625']
delta_i = 0
delta = delta_list[delta_i]
view_type = "map"
points = [['39.488892379812896', '52.52593551259488', 'round']]


def coords_to_str(coords):
    coords.sort()
    coords.append(coords[0])
    return ','.join(map(lambda x: ','.join(map(str, x)), coords))


@app.route('/', methods=['POST', 'GET'])
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
        "size": "450,450",
        "l": view_type,
        "pl": f"c:{point_color},f:{point_color2},w:{w_line},{points_coords_str}",
        'pt': '~'.join(map(lambda x: ','.join(map(str, x)), points))
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    return render_template("main.html",
                           image=f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}&pl={map_params["pl"]}&pt={map_params["pt"]}')


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


@app.route('/delta_plus')
def indexdp():
    global delta, delta_list, delta_i
    # print(delta_i, len(delta_list) - 1)
    if delta_i < len(delta_list) - 1:
        delta = delta_list[delta_i + 1]
        delta_i += 1
    return redirect('/')


@app.route('/delta_minus')
def indexdm():
    global delta, delta_list, delta_i
    # print(delta_list[0])
    # print(delta_i, len(delta_list) - 2)
    if delta_i > 0:
        delta = delta_list[delta_i - 1]
        delta_i -= 1
    return redirect('/')


@app.route('/change_type')
def indextype():
    global view_type
    if view_type == "map":
        view_type = "sat,skl"
    else:
        view_type = "map"
    return redirect('/')


@app.route('/mouse_coords/<coords>')
def indexmouse(coords):
    coords2 = list(map(int, coords.split('; ')))
    k = float(delta)
    center_x = 765
    center_y = 335
    x_koeff = (k / 10) / 18
    y_koeff = (k / 10) / 30
    # print(coords2)
    # print(coords2, (coords2[0] - center_x), (coords2[1] - center_y), k, x_koeff, y_koeff)
    coords2[0] = (coords2[0] - center_x) * x_koeff + float(x)
    coords2[1] = (center_y - coords2[1]) * y_koeff + float(y)
    points.append([str(coords2[0]), str(coords2[1]), 'round'])
    # print(points)
    return redirect('/')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    # db_session.global_init('db/Spiders.db')
    app.run(host="127.0.0.1", port=5000)
