import sys
from colorsys import hsv_to_rgb

from flask import Flask, render_template, redirect
from data import db_session
from data.AuthorizationForm import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.Spiders import Spiders
from data.User import User
from data.SpiderFormUpdate import SpiderFormUpdate


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
spider_list = [[list(map(float, el2.split('/'))) for el2 in el.points.split('|')] for el in spiders]
spider_list_str = [coords_to_str(el) for el in spider_list]
color_list = [c for c in range(0, 360, 360 // len(spider_list_str))]
color_list2 = []
for i in range(len(color_list)):
    color_list2.append(''.join(list(map(lambda x: hex(int(x * 255))[2:] + '0' * (2 - len(hex(int(x * 255))[2:])),
                                        hsv_to_rgb(color_list[i] / 360, 1, 1)))))
print(spider_list, spider_list_str, color_list2, sep='\n')
db_sess.close()
spider_index = 0
making_points = False
point_spider_name = ''


@app.route('/', methods=['POST', 'GET'])
def main():
    global x, y, delta, view_type, spider_index, spider_list_str
    # print(points)
    point_color = color_list2[spider_index] + 'ff'
    point_color2 = color_list2[spider_index] + '88'
    w_line = 2
    print(spider_list_str[spider_index])
    map_params = {
        "ll": ",".join([str(x), str(y)]),
        "spn": ",".join([str(delta), str(delta)]),
        "size": "450,450",
        "l": view_type,
        "pl": f"c:{point_color},f:{point_color2},w:{w_line},{spider_list_str[spider_index]}",
        'pt': '~'.join(map(lambda x: ','.join(map(str, x)), points))
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # print('|'.join(map(lambda x: '/'.join(x), points)))
    return render_template("main.html",
                           image=f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}&pl={map_params["pl"]}&pt={map_params["pt"]}',
                           spider_list=[el.name for el in spiders], colors=color_list2)


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
        points_making.append([str(coords2[0]), str(coords2[1])])
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
        db_session.global_init('db/Users.db')
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
        db_session.global_init('db/Users.db')
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
    pass


@app.route('/willupdate', methods=['GET', 'POST'])
def updateForm():
    form = SpiderFormUpdate()
    if form.validate_on_submit():
        db_session.global_init('db/Spiders.db')
        db_sess3 = db_session.create_session()
        spider = db_sess3.query(Spiders).filter(Spiders.name == str(form.name.data)).first()
        if spider:
            global point_spider_name
            point_spider_name = spider.name
            return redirect(f'/points2')
        return render_template('UpdateSpider.html', message="Такого паука нет", form=form)
    return render_template('UpdateSpider.html', form=form)


@app.route('/points2')
def indexpoint():
    global x, y, delta, view_type, spider_index, spider_list_str, making_points, point_spider_name
    making_points = True
    db_session.global_init('db/Spiders.db')
    db_sess3 = db_session.create_session()
    spider = db_sess3.query(Spiders).filter(Spiders.name == point_spider_name).first()
    db_sess3.close()
    point_color = color_list2[int(spider.id) - 1] + 'ff'
    point_color2 = color_list2[int(spider.id) - 1] + '88'
    w_line = 2
    map_params = {
        "ll": ",".join([str(x), str(y)]),
        "spn": ",".join([str(delta), str(delta)]),
        "size": "450,450",
        "l": view_type,
        "pl": f"c:{point_color},f:{point_color2},w:{w_line},{spider_list_str[int(spider.id) - 1]}",
        'pt': '~'.join(map(lambda x: ','.join(map(str, x)), points_making))
    }
    return render_template('point_maker.html', title='Выбор точек',
                           image=f'http://static-maps.yandex.ru/1.x/?ll={map_params["ll"]}&spn={map_params["spn"]}&size={map_params["size"]}&l={map_params["l"]}&pl={map_params["pl"]}&pt={map_params["pt"]}',
                           )


@app.route('/points_done')
def points_done():
    global making_points, points_making
    points.extend(points_making)
    points_making = []
    making_points = False
    return redirect('/')


@app.route('/points_delete')
def points_delete():
    global points_making
    points_making = []
    return redirect('/points2')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def create_spider(name, points):
    db_session.global_init('db/Spiders.db')
    db_sess = db_session.create_session()
    spider = Spiders()
    spider.name = name
    spider.points = points
    db_sess.commit()
    db_sess.close()


def create_user(name, password):
    db_session.global_init('db/Users.db')
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
    app.run(host="127.0.0.1", port=5000)
