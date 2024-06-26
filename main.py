import sys
from colorsys import hsv_to_rgb
from math import atan

from PIL import Image
from flask import Flask, render_template, redirect, url_for
from numpy import deg2rad, arctan, rad2deg

from data import db_session  # , spider_image_api
from data.AuthorizationForm import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.Spiders import Spiders
from data.SpidersDescription import SpidersDescription
from data.User import User
from data.SpiderFormUpdate import SpiderFormUpdate
from data.SpiderFormAdd import SpiderFormAdd


def coords_to_str(coords):
    # coords.sort(key=lambda x: x[0]*x[1])
    coords.append(coords[0])
    return ','.join(map(lambda x: ','.join(map(str, x)), coords))


app = Flask(__name__)
app.config['SECRET_KEY'] = 'bober'
login_manager = LoginManager()
login_manager.init_app(app)
x = '39.488892379812896'
y = '52.52593551259488'
delta_list = ['8', '4', '2', '1', '0.5', '0.25', '0.125', '0.0625', '0.03125', '0.015265', '0.0078125', '0.00390625',
              '0.001953125', '0.0009765625']
delta_i = 0
delta = delta_list[delta_i]
view_type = "map"
points = []  # [['39.488892379812896', '52.52593551259488', 'round']]
points_making = []
db_session.global_init('db/Spiders.db')
db_sess = db_session.create_session()
spiders = db_sess.query(Spiders).all()
# print(spiders)
# print([el for el in spiders])
# print([[el2 for el2 in el.points.split('|')] for el in spiders])
spider_list_str = []
color_list = []
color_list2 = []
spider_list = []
deletor_activated = False
points_check = False


def count_colors():
    global spider_list_str, color_list, color_list2, spider_list
    db_session.global_init('db/Spiders.db')
    db_sess = db_session.create_session()
    spiders = db_sess.query(Spiders).all()
    spider_list = [[list(map(float, el2.split('/'))) for el2 in el.points.split('|')] for el in spiders]
    spider_list_str = [coords_to_str(el) for el in spider_list]
    color_list = [c for c in range(0, 360, 360 // len(spider_list_str))]
    color_list2 = []
    for i in range(len(color_list)):
        color_list2.append(''.join(list(map(lambda x: hex(int(x * 255))[2:] + '0' * (2 - len(hex(int(x * 255))[2:])),
                                            hsv_to_rgb(color_list[i] / 360, 1, 1)))))


count_colors()
# print(spider_list, spider_list_str, color_list2, sep='\n')
db_sess.close()
spider_index = 0
making_points = False
point_spider_name = ''

point_colors = {
    '|'.join(map(str, list(range(0, 13)) + list(range(330, 360)))): 'rd',
    '|'.join(map(str, list(range(13, 33)))): 'do',
    '|'.join(map(str, list(range(33, 48)))): 'or',
    '|'.join(map(str, list(range(48, 80)))): 'yw',
    '|'.join(map(str, list(range(80, 153)))): 'gn',
    '|'.join(map(str, list(range(153, 208)))): 'lb',
    '|'.join(map(str, list(range(208, 241)))): 'bl',
    '|'.join(map(str, list(range(241, 290)))): 'vv',
    '|'.join(map(str, list(range(290, 330)))): 'pn',
}


@app.route('/', methods=['POST', 'GET'])
def main():
    global x, y, delta, view_type, spider_index, spider_list_str, points_check
    points_check = False
    # print(points)
    area_color = color_list2[spider_index] + 'ff'
    area_color2 = color_list2[spider_index] + '88'
    w_line = 2
    # print(spider_list_str[spider_index])
    point_color = 'rd'
    for key in point_colors:
        pc = color_list[spider_index]
        if str(pc) in list(key.split('|')):
            point_color = point_colors[key]
    db_session.global_init('db/Spiders.db')
    db_sess2 = db_session.create_session()
    current_spider = db_sess2.query(Spiders).filter(Spiders.id == spider_index + 1).first()
    # print(current_spider, spider_index + 1)
    current_spider_points = []
    if current_spider:
        if current_spider.points_unchecked:
            current_spider_points = [list(map(float, el2.split('/'))) for el2 in
                                     current_spider.points_unchecked.split('|')]
    if current_spider_points is None:
        current_spider_points = []
    w_line = 2
    s = ''
    if current_spider_points:
        s = f'pm{point_color}s'
    print(spider_list_str[spider_index])
    if spider_list_str[spider_index] != '0.0,0.0':
        map_params = {
            "ll": ",".join([str(x), str(y)]),
            "spn": ",".join([str(delta), str(delta)]),
            "size": "450,450",
            "l": view_type,
            "pl": f"c:{area_color},f:{area_color2},w:{w_line},{spider_list_str[int(spider_index)]}",
            'pt': '~'.join(
                map(lambda x: ','.join(map(str, x)), [[*el, s] for el in current_spider_points]))
        }
        img = f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}&pl={map_params["pl"]}&pt={map_params["pt"]}'
    else:
        map_params = {
            "ll": ",".join([str(x), str(y)]),
            "spn": ",".join([str(delta), str(delta)]),
            "size": "450,450",
            "l": view_type,
            'pt': '~'.join(
                map(lambda x: ','.join(map(str, x)), [[*el, s] for el in current_spider_points]))
        }
        img = f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}&pt={map_params["pt"]}'

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # print('|'.join(map(lambda x: '/'.join(x), points)))
    return render_template("main.html", image=img, spider_list=[el.name for el in spiders], colors=color_list2)


@app.route('/ll_right')
def indexl():
    global x, delta
    d = 2 * (float(delta)) / 10
    if float(x) + d < 180:
        x = str(float(x) + d)
    if making_points:
        return redirect('/points2')
    return redirect('/')


@app.route('/ll_left')
def indexr():
    global x, delta
    d = 2 * (float(delta)) / 10
    if float(x) - d > -180:
        x = str(float(x) - d)
    if making_points:
        return redirect('/points2')
    return redirect('/')


@app.route('/ll_down')
def indexd():
    global y, delta
    d = 2 * (float(delta)) / 10
    if float(y) - d > -90:
        y = str(float(y) - d)
    if making_points:
        return redirect('/points2')
    return redirect('/')


@app.route('/ll_up')
def indexu():
    global y, delta
    d = 2 * (float(delta)) / 10
    if float(y) + d < 90:
        y = str(float(y) + d)
    if making_points:
        return redirect('/points2')
    return redirect('/')


@app.route('/delta_plus')
def indexdp():
    global delta, delta_list, delta_i
    # print(delta_i, len(delta_list) - 1)
    if delta_i < len(delta_list) - 1:
        delta = delta_list[delta_i + 1]
        delta_i += 1
    if making_points:
        return redirect('/points2')
    return redirect('/')


@app.route('/delta_minus')
def indexdm():
    global delta, delta_list, delta_i
    if delta_i > 0:
        delta = delta_list[delta_i - 1]
        delta_i -= 1
    if making_points:
        return redirect('/points2')
    return redirect('/')


@app.route('/change_type')
def indextype():
    global view_type
    if view_type == "map":
        view_type = "sat,skl"
    else:
        view_type = "map"
    if making_points:
        return redirect('/points2')
    return redirect('/')


@app.route('/mouse_coords/<coords>')
def indexmouse(coords):
    if current_user.is_authenticated:
        coords2 = list(map(int, coords.split('; ')))
        k = float(delta)
        center_x = 765
        center_y = 335
        x_koeff = (k / 10) / 18
        y_koeff = (k / 10) / 30
        coords2[0] = (coords2[0] - center_x) * x_koeff + float(x)
        coords2[1] = (center_y - coords2[1]) * y_koeff + float(y)
        if not deletor_activated:
            points_making.append([str(coords2[0]), str(coords2[1])])
        else:
            dist_list = []
            for i in range(len(points_making)):
                dist_list.append([((float(points_making[i][0]) - coords2[0]) ** 2 + (
                        float(points_making[i][1]) - coords2[1]) ** 2) ** 0.5, i])
            if dist_list:
                min_dist = dist_list[0][0]
                min_ind = 0
                for el in dist_list:
                    if el[0] < min_dist:
                        min_dist = el[0]
                        min_ind = el[1]
                if (((float(points_making[min_ind][0]) - coords2[0]) / x_koeff) ** 2 + (
                        (float(points_making[min_ind][1]) - coords2[1]) / y_koeff) ** 2) ** 0.5 < 30:
                    points_making.pop(min_ind)
    return redirect('/points2')


@app.route('/change_spider/<index>')
def change_spider(index):
    global spider_index
    # print(spider_index, end='|')
    spider_index = int(index) - 1
    # print(spider_index)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        db_session.global_init('db/Spiders.db')
        db_sess2 = db_session.create_session()
        if db_sess2.query(User).filter(User.name == str(form.name.data)).first():
            return render_template('register.html', message="Такой пользователь уже есть",
                                   title='Регистрация', form=form)
        user = User()
        user.name = form.name.data
        user.set_password(form.password.data)
        db_sess2.add(user)
        db_sess2.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_session.global_init('db/Spiders.db')
        db_sess2 = db_session.create_session()
        user = db_sess2.query(User).filter(User.name == str(form.name.data)).first()
        # print(user, user.check_password(form.password.data))
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            db_sess2.close()
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/points')
def spider_add_or_update():
    return render_template('AddOrUpdate.html', title='Выбор')


@app.route('/willadd', methods=['GET', 'POST'])
def addForm():
    form = SpiderFormAdd()
    if form.validate_on_submit():
        db_session.global_init('db/Spiders.db')
        db_sess3 = db_session.create_session()
        if db_sess3.query(Spiders).filter(Spiders.name == str(form.name.data)).first():
            return render_template('AddSpider.html', message="Такой паук уже есть", form=form)
        else:
            spider = create_spider(form.name.data)
            db_sess3.add(spider)
            db_sess3.commit()

            print(form.picture.data)
            spider_desc = create_spider_description(form.name.data, form.size.data, form.color.data,
                                                    form.Spider_type.data, form.time.data, form.picture.data)
            im = Image.open(form.picture.data)
            im = im.resize((500, 500))
            im.save(f'static\{form.picture.data}')
            im = im.resize((100, 100))
            im.save(f'static\{form.picture.data[:-4]}_small{form.picture.data[-4:]}')
            db_sess3.add(spider_desc)
            db_sess3.commit()
            spider_names = open('spider_names.txt', 'w', encoding='utf8')
            spider_names.write('|'.join([el.name for el in db_sess3.query(Spiders).all()]))
            global point_spider_name
            point_spider_name = form.name.data
            return redirect(f'/points2')
    return render_template('AddSpider.html', form=form)


@app.route('/willupdate', methods=['GET', 'POST'])
def updateForm():
    db_session.global_init('db/Spiders.db')
    db_sess3 = db_session.create_session()

    spider_names = open('spider_names.txt', 'w', encoding='utf8')
    spider_names.write('|'.join([el.name for el in db_sess3.query(Spiders).all()]))
    spider_names.close()
    form = SpiderFormUpdate()
    print(db_sess3.query(Spiders).all())
    if form.validate_on_submit():
        spider = db_sess3.query(Spiders).filter(Spiders.name == str(form.name.data)).first()
        if spider:
            global point_spider_name, points_check
            point_spider_name = spider.name
            if points_check:
                global points_making
                if spider.points_unchecked is None:
                    points_check = False
                    return redirect('/')
                points_making = [list(map(float, el2.split('/'))) for el2 in
                                 spider.points_unchecked.split('|')]
            return redirect(f'/points2')
        return render_template('UpdateSpider.html', message="Такого паука нет", form=form, spider_list=spider_list)
    return render_template('UpdateSpider.html', form=form)


@app.route('/points2')
def indexpoint():
    global x, y, delta, view_type, spider_index, spider_list_str, making_points, point_spider_name, points_making
    count_colors()
    making_points = True
    db_session.global_init('db/Spiders.db')
    db_sess3 = db_session.create_session()
    spider = db_sess3.query(Spiders).filter(Spiders.name == point_spider_name).first()
    db_sess3.close()
    area_color = color_list2[int(spider.id) - 1] + 'ff'
    area_color2 = color_list2[int(spider.id) - 1] + '88'
    point_color = 'rd'
    for key in point_colors:
        pc = color_list[int(spider.id) - 1]
        if str(pc) in list(key.split('|')):
            point_color = point_colors[key]
    w_line = 2
    s = ''
    if points_making:
        s = f'pm{point_color}s'
    # print(points_making, end=' | ')
    # print(points_making)
    if spider_list_str[int(spider.id) - 1] != '0.0,0.0':
        map_params = {
            "ll": ",".join([str(x), str(y)]),
            "spn": ",".join([str(delta), str(delta)]),
            "size": "450,450",
            "l": view_type,
            "pl": f"c:{area_color},f:{area_color2},w:{w_line},{spider_list_str[int(spider.id) - 1]}",
            'pt': '~'.join(
                map(lambda x: ','.join(map(str, x)), [[*el, s] for el in points_making]))
        }
        img = f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}&pl={map_params["pl"]}&pt={map_params["pt"]}'
    else:
        map_params = {
            "ll": ",".join([str(x), str(y)]),
            "spn": ",".join([str(delta), str(delta)]),
            "size": "450,450",
            "l": view_type,
            'pt': '~'.join(
                map(lambda x: ','.join(map(str, x)), [[*el, s] for el in points_making]))
        }
        img = f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}&pt={map_params["pt"]}'
    # print(spider_list_str, map_params['pl'], map_params['pt'], spider.id)
    # print(map_params['pt'])
    if deletor_activated:
        return render_template('point_maker.html', title='Выбор точек', image=img, spider=spider.name,
                               button_desc='Расстановка точек')
    return render_template('point_maker.html', title='Выбор точек', image=img, spider=spider.name,
                           button_desc='Удаление точкек по одной')


@app.route('/points_done/<spider_name>')
def points_done(spider_name):
    global making_points, points_making, points_check
    if points_making:
        db_session.global_init('db/Spiders.db')
        db_sess = db_session.create_session()
        spider = db_sess.query(Spiders).filter(Spiders.name == str(spider_name)).first()
        # print(spider.points_unchecked)
        if not points_check:
            if spider.points_unchecked:
                spider.points_unchecked = spider.points_unchecked + '|' + '|'.join(
                    map(lambda x: '/'.join(x), points_making))
                # print(spider.points_unchecked)
            else:
                spider.points_unchecked = '|'.join(map(lambda x: '/'.join(x), points_making))
        else:
            spider.points_unchecked = None
            if spider.points != '0':
                points_making.extend([list(map(float, el2.split('/'))) for el2 in spider.points.split('|')])
                points_making = sort_points(points_making)
                spider.points = '|'.join(map(lambda x: '/'.join(map(str, x)), points_making))
                # print(spider.points_unchecked)
            else:
                print(0)
                points_making = sort_points(points_making)
                # spider.points_unchecked = '/'.join(map(str, mpoint))
                spider.points = '|'.join(map(lambda x: '/'.join(map(str, x)), points_making))
            points_check = False
        db_sess.commit()
        points_making = []
    making_points = False
    return redirect('/')


@app.route('/points_delete')
def points_delete():
    global points_making
    points_making = []
    return redirect('/points2')


@app.route('/change_mouse')
def change_mouse():
    global deletor_activated
    if deletor_activated:
        deletor_activated = False
    else:
        deletor_activated = True
    return redirect('/points2')


@app.route('/library')
def library():
    db_session.global_init('db/SpidersDescription.db')
    db_sess = db_session.create_session()
    sp_list = db_sess.query(SpidersDescription).all()
    spider_list = []
    # print(os.getcwd() + '\images\\' + sp_list[0].picture)
    for el in sp_list:
        spider_list.append(
            [el.name, el.size, el.color, el.Spider_type, el.time,
             url_for('static', filename=f'{el.picture[:-4]}_small{el.picture[-4:]}')])
    return render_template('library.html', spider_list=spider_list)


@app.route('/spider_description/<spider_name>')
def spider_description(spider_name):
    db_session.global_init('db/SpidersDescription.db')
    db_sess2 = db_session.create_session()
    spider = db_sess2.query(SpidersDescription).filter(SpidersDescription.name == str(spider_name)).first()
    spider_inf = [['Название', spider.name], ['Размер', spider.size], ['Цвет', spider.color],
                  ['Тип охоты', spider.Spider_type], ['Время активности', spider.time],
                  url_for('static', filename=spider.picture)]
    return render_template('spider_desc.html', spider_inf=spider_inf)


@app.route('/points_check')
def points_check():
    global points_check
    points_check = True
    return redirect('/willupdate')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def create_spider(name, points_unchecked=None, points='0'):
    spider = Spiders()
    spider.name = name
    spider.points_unchecked = points_unchecked
    spider.points = points
    return spider


def sort_points(points):
    x_list = []
    y_list = []
    for el in points:
        x_list.append(float(el[0]))
        y_list.append(float(el[1]))
    mid_point = [sum(x_list) / len(x_list), sum(y_list) / len(y_list)]
    points.sort()
    points = list(map(lambda x: [float(x[0]), float(x[1])], points))
    points1 = []
    points2 = []
    points3 = []
    points4 = []
    for i in range(len(points)):
        if points[i][0] - mid_point[0] > 0:
            if points[i][1] - mid_point[1] > 0:
                points1.append(points[i])
            if points[i][1] - mid_point[1] < 0:
                points2.append(points[i])
        if points[i][0] - mid_point[0] < 0:
            if points[i][1] - mid_point[1] < 0:
                points3.append(points[i])
            if points[i][1] - mid_point[1] > 0:
                points4.append(points[i])
        # angle = rad2deg(arctan(((points[i][0] - mid_point[0]) / (points[i][1] - mid_point[1]))))
        # if angle < 0:
        #     angle += 360
        # points2.append([angle, points[i]])

    # points2.sort(key=lambda x: x[0])
    # result = []
    # for el in points2:
    #     result.append(el[1])
    # print(points2)
    # print(result)
    # print(points)
    points2.reverse()
    points3.reverse()
    result = points1
    result.extend(points2)
    result.extend(points3)
    result.extend(points4)
    return result


def create_spider_description(name, size, color, type, time, picture='spider_without_picture.png'):
    spider_desc = SpidersDescription()
    spider_desc.name = name
    spider_desc.size = size
    spider_desc.color = color
    spider_desc.Spider_type = type
    spider_desc.time = time
    spider_desc.picture = picture
    return spider_desc


def create_user(name, password):
    db_session.global_init('db/Spiders.db')
    db_sess = db_session.create_session()
    user = User()
    user.name = name
    user.password = password
    db_sess.commit()
    db_sess.close()


if __name__ == '__main__':
    # create_spider('крестовик',
    #               '39.327781268701784/52.51593551259488|39.33333682425734/52.605935512594876|39.41944793536845/52.687602179261546|39.547225713146226/52.70260217926155|39.65833682425734/52.69926884592821|39.74722571314623/52.639268845928214|39.75278126870178/52.58593551259488|39.72222571314623/52.51093551259488|39.644447935368454/52.45426884592821|39.57222571314623/52.435935512594874|39.44722571314623/52.440935512594876|39.38055904647956/52.46760217926155')
    # create_spider('крестовик2',
    #               '39.580559046479564/52.61093551259488|39.513892379812894/52.660935512594875|39.516670157590674/52.76093551259488|39.641670157590674/52.82760217926155|39.81111460203512/52.810935512594874|39.922225713146226/52.74093551259488|39.83611460203512/52.64760217926155|39.736114602035116/52.61426884592821|39.68333682425734/52.60926884592821')
    # app.register_blueprint(spider_image_api.blueprint)
    app.run(host="127.0.0.1", port=5000)
