from flask import Flask, request, render_template, url_for, logging, session, flash, redirect, Markup
import pymysql.cursors
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, FileField, ValidationError
from functools import wraps
import re
import sys
import json

app = Flask(__name__)

connection = pymysql.connect(host='localhost',
                             user='Jacob',
                             password='691748jw',
                             db='travelers',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash ('Unauthorized, please login.', 'danger')
            return redirect(url_for('login'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['admin'] == True:
            return f(*args, **kwargs)
        else:
            flash ('Unauthorized. Requires administrator access.', 'danger')
            return redirect(url_for('index'))
    return

@app.route('/')
def index():
    return render_template('home.html')

class RegisterForm(Form):
    username = StringField('', [
        validators.Length(min=4, max=25, message='Username must be 4 to 25 characters long')
        ], render_kw={"placeholder": "username"})
    email = StringField('', render_kw={"placeholder": "email"})
    firstName = StringField('', [
        validators.InputRequired()
    ], render_kw={"placeholder": "first name"})
    lastName = StringField('', [
        validators.InputRequired()
    ], render_kw={"placeholder": "last name"}) 
    password = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ], render_kw={"placeholder": "password"})
    confirm = PasswordField('', render_kw={"placeholder": "confirm password"})

    def validate_email(form, field):
        if len(field.data) < 5 or len(field.data) > 35:
            raise ValidationError('Email must be 5 to 35 characters long')
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", field.data):
            raise ValidationError('Please submit a valid email')

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        first = form.firstName.data
        last = form.lastName.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = connection.cursor()
        cur.execute("INSERT INTO users(Username, FirstName, LastName, Password, Email) "
                    "VALUES (%s, %s, %s, %s, %s)"
                    , (username, first, last, password, email))

        connection.commit()
        cur.close()

        flash('Congratulations! You are now registered.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_attempt = request.form['password']

        cur = connection.cursor()

        result = cur.execute("SELECT * "
                             "FROM users "
                             "WHERE Username = %s"
                             , [username])


        if result > 0:
            user = cur.fetchone()
            password = user['Password']
            userId = user['UserID']
            firstname = user['FirstName']

            #checks if passwords match and logs you in if they do
            if sha256_crypt.verify(password_attempt, password):
                session['logged_in'] = True
                session['user'] = userId

                #sets admin session status from db query
                cur.execute("SELECT IsAdmin "
                            "FROM users "
                            "WHERE UserID = %s"
                            , [userId])

                if cur.fetchone()['IsAdmin'] == 1:
                    session['admin'] = True
                else:
                    session['admin'] = False

                cur.close()
                flash('Welcome, ' + firstname + '. You are now logged in.', 'success')
                return redirect(url_for('index'))

            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()

        else:
            error = "Username not found."
            return render_template('login.html', error=error)

    return render_template('login.html')

class CountryForm(Form):
    cur = connection.cursor()

    name = StringField('Name', [validators.Length(min=1, max=300)])
    description = TextAreaField('Description')

@app.route('/countries')
@is_logged_in
def countries():
    cur = connection.cursor()
    result = cur.execute("SELECT c.CountryName, count(d.DestName) AS DestCount, c.CountryID "
                         "FROM Countries c LEFT OUTER JOIN Destinations d ON c.CountryID = d.CountryID "
                         "GROUP BY c.CountryName "
                         "ORDER BY c.CountryName")

    countries = cur.fetchall()
    cur.close()

    return render_template('countries.html', countries=countries)

@app.route('/country/<string:id>')
@is_logged_in
def country(id):
    countryCur = connection.cursor()
    destinationsCur = connection.cursor()
    imagesCur = connection.cursor()
    try:
        countryCur.execute("SELECT CountryName, Description, UpdateDate "
                           "FROM countries "
                           "WHERE CountryID = %s"
                           , [id])

        destinationsCur.execute("SELECT CountryName, DestName, DestID, c.Description, c.UpdateDate"
                    " FROM countries c JOIN destinations d"
                    " WHERE c.CountryID = d.CountryID AND c.CountryID = %s"
                    , [id])

        imagesCur.execute("SELECT c.CountryId, d.DestName, ImgUrl "
                "FROM countries c JOIN destinations d ON c.CountryID = d.CountryID "
                "JOIN dest_images i on d.DestID = i.DestID "
                "WHERE c.CountryID = %s"
                , [id])

        country = countryCur.fetchone()
        destinations = destinationsCur.fetchall()
        images = imagesCur.fetchall()
        countryCur.close()
        destinationsCur.close()
        return render_template('country.html', country=country, destinations=destinations, images=images)
    except:
        msg = "Country does not exist."
        return render_template('country.html', msg=msg)


@app.route('/edit_country/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_country(id):
    cur = connection.cursor()
    cur.execute("SELECT CountryName, Description "
                "FROM countries "
                "WHERE CountryID = %s"
                , [id])

    country = cur.fetchone()
    cur.close()

    form = CountryForm(request.form)

    form.name.data = country['CountryName']
    form.description.data = country['Description']

    if request.method == 'POST':
        if request.form['action'] == 'Submit':
            name = request.form['name']
            description = request.form['description']

            cur = connection.cursor()
            cur.execute("UPDATE countries "
                        "SET CountryName=%s, Description=%s "
                        "WHERE CountryID=%s"
                        ,(name, description, id))

            connection.commit()
            cur.close()

            flash('Country updated.', 'success')
            return redirect(url_for('countries'))

        elif request.form['action'] == 'Delete':
            cur = connection.cursor()
            cur.execute("DELETE FROM countries "
                        "WHERE CountryID = %s"
                        , [id])

            connection.commit()
            cur.close()

            flash('Country successfully deleted.', 'success')
            return redirect(url_for('destinations'))

    return render_template('edit_country.html', form=form)


class DestinationForm(Form):
    cur = connection.cursor()

    cur.execute("SELECT CountryID, CountryName "
                "FROM countries")

    countries = cur.fetchall()
    cur.close()

    countriesList = [(0, "")]
    for country in countries:
        countriesList.append((country['CountryID'], country['CountryName']))

    name = StringField('Name')
    countryId = SelectField('Country', choices=countriesList, coerce=int)
    category = SelectField('Category', choices=[
        (0, ""),
        (1, "Natural Site"),
        (2, "Cultural/Historic Site"),
        (3, "Activity")], coerce=int)
    description = TextAreaField('Description')
    imgUrl = StringField('Image Upload', [validators.URL(message="Not a valid url")])
    tags = StringField('Tags')

class DestImageForm(Form):
    imgUrl = StringField('Image URL', [validators.URL(message="Not a valid url")])

@app.route('/destinations-user')
@is_logged_in
def destinations_user():
    cur = connection.cursor()
    cur.execute("SELECT d.DestID, d.DestName, i.ImgURL "
                "FROM destinations d JOIN dest_images i on d.destID = i.DestID "
                "GROUP BY d.DestID "
                "ORDER BY RAND() "
                "LIMIT 3")
    recommended = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT d.DestID, d.DestName, i.ImgURL "
                "FROM destinations d "
                "JOIN dest_images i on d.DestID = i.DestID "
                "JOIN dest_tags dt on d.DestID = dt.DestID "
                "JOIN tags t ON dt.TagID = t.TagID "
                "WHERE t.TagName = 'Adventure' "
                "GROUP BY d.DestID "
                "ORDER BY RAND() "
                "LIMIT 3")
    topTag = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT d.DestID, d.DestName, i.ImgURL "
                "FROM destinations d "
                "JOIN dest_images i on d.DestID = i.DestID "
                "JOIN dest_tags dt on d.DestID = dt.DestID "
                "JOIN tags t ON dt.TagID = t.TagID "
                "WHERE t.TagName = 'Animals' "
                "GROUP BY d.DestID "
                "ORDER BY RAND() "
                "LIMIT 3")
    secondTag = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT COUNT(*) AS Count "
                "FROM Destinations")
    count=cur.fetchone()

    return render_template('destinations_user.html', count=count, recommended=recommended, topTag=topTag, secondTag=secondTag)

@app.route('/destinations')
@is_logged_in
def destinations():
    cur = connection.cursor()
    result = cur.execute("SELECT * "
                         "FROM destinations d JOIN countries c ON d.CountryID = c.CountryID "
                         "ORDER BY d.DestName")

    destinations = cur.fetchall()
    cur.close() 

    if result > 0:
        return render_template('destinations.html', destinations=destinations)
    else:
        msg="No destinations found."
        return render_template('destinations.html',  msg=msg)

@app.route('/destination/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def destination(id):
    if request.method == 'GET':
        cur = connection.cursor()
        imageCur = connection.cursor()
        result = cur.execute("SELECT DestName, CountryName, DestID, c.CountryID, d.Description, d.UpdateDate "
                             "FROM destinations d JOIN countries c ON d.CountryID = c.CountryID "
                             "WHERE DestID = %s", [id])

        imageCur.execute("SELECT ImgUrl "
                         "FROM dest_images "
                         "WHERE DestID = %s"
                         , [id])

        destination = cur.fetchone()
        images = imageCur.fetchall()
        cur.close()
        imageCur.close()

        if result > 0:
            return render_template('destination.html', destination=destination, images=images)
        else:
            flash('Destination does not exist.', 'danger')
            return redirect(url_for('destinations'))

    else:
        cur = connection.cursor()
        cur.execute("INSERT INTO favorites "
                    "VALUES (%s, %s)",
                    (session['user'], id))

        connection.commit()
        cur.close()

        flash('Added to favorites', 'success')

        return redirect(url_for('destinations'))

@app.route('/create-destination', methods=['POST', 'GET'])
@is_logged_in
def create_destination():
    form = DestinationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        countryId = form.countryId.data
        category = form.category.data
        description = form.description.data
        imgUrl = form.imgUrl.data
        tags = form.tags.data
        #lat = request.form['lat']
        #lng = request.form['lng']

        cur = connection.cursor()

        cur.execute("INSERT INTO destinations(DestName, CountryID, Category, Description) "
                    " VALUES (%s, %s, %s, %s)"
                    , (name, countryId, category, description))

        connection.commit()
        cur.close()

        cur = connection.cursor()

        cur.execute("SELECT DestID "
                    "FROM destinations "
                    "WHERE DestName = %s"
                    , [name])
        id = cur.fetchone()

        cur.execute("INSERT INTO dest_images "
                    " VALUES (%s, %s)",
                    (id['DestID'], imgUrl))

        #TODO: make it so the latLng is saved in db to avoid geocoding on page load
        # cur.execute("INSERT INTO dest_locations "
        #     " VALUES (%s, %s, %s)"
        #     , (id['DestID'], lat, lng))

        connection.commit()
        cur.close()

        ##TODO: figure out why this if statement isn't working... error is thrown if no tags input
        if tags != None:
            for tag in tags.split(','):
                cur = connection.cursor()

                cur.execute("SELECT TagID "
                            "FROM Tags "
                            "WHERE TagName = %s"
                            , [tag])
                tagId = cur.fetchone()
                
                cur.execute("INSERT INTO dest_tags "
                            "VALUES (%s, %s)"
                            , (id['DestID'], tagId['TagID']))
                connection.commit()
                cur.close()

        flash('Your new destination has been created!', 'success')

        return redirect(url_for('destinations'))
            
    cur = connection.cursor()
    cur.execute("SELECT TagName FROM tags")
    tags = cur.fetchall()
    cur.close()

    tagsList = []
    for tag in tags:
        tagsList.append(tag['TagName'])

    return render_template('create_destination.html', form=form, tags=tagsList)

@app.route('/edit_destination/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def edit_destination(id):
    cur = connection.cursor()

    cur.execute("SELECT * "
                "FROM destinations d JOIN dest_images i ON d.DestID = i.DestID "
                "WHERE DestID = %s"
                , [id])

    destination = cur.fetchone()
    cur.close()

    form = DestinationForm(request.form)

    form.name.data = destination['DestName']
    form.countryId.data = destination['CountryID']
    form.category.data = destination['Category']
    form.description.data = destination['Description']
    form.imgUrl.data = destination['ImgURL']
    # form.tags.data = tags['TagName'] --> gonna need to loop through

    if request.method == 'POST':
        #if request.form['action'] == 'Submit':
        name = request.form['name']
        countryId = request.form['countryId']
        category = request.form['category']
        description = request.form['description']
        tags = request.form['tags']
        imgUrl = request.form['imgUrl']

        cur = connection.cursor()
        cur.execute("UPDATE destinations "
                    "SET DestName=%s, CountryID=%s, Category=%s, Description=%s "
                    "WHERE DestID=%s"
                    , (name, countryId, category, description, id))

        cur.execute("UPDATE dest_images "
                    "SET ImgURL = %s "
                    "WHERE DestID=%s"
                    , (imgUrl, id))

        connection.commit()
        cur.close()

        cur = connection.cursor()

        cur.execute("SELECT DestID "
                    "FROM destinations "
                    "WHERE DestName = %s"
                    , [name])
        destId = cur.fetchone()

        if len(tags.split(',')) > 0:
            for tag in tags.split(','):
                cur = connection.cursor()       

                cur.execute("SELECT TagID "
                            "FROM Tags "
                            "WHERE TagName = %s"
                            , [tag])
                tagId = cur.fetchone()
                
                cur.execute("INSERT INTO dest_tags "
                            "VALUES (%s, %s)"
                            , (destId['DestID'], tagId['TagID']))
                connection.commit()
                cur.close()

        flash('Destination updated.', 'success')
        return redirect(url_for('destinations'))

        # # TODO: add JS here to have popup "Are you sure?"
        # elif request.form['action'] == 'Delete':
        #     cur = connection.cursor()
        #     cur.execute("DELETE FROM destinations "
        #                 "WHERE DestID = %s"
        #                 , [id])

        #     connection.commit()
        #     cur.close()

        #     flash('Destination successfully deleted.', 'success')
        #     return redirect(url_for('destinations'))

    cur = connection.cursor()
    cur.execute("SELECT TagName FROM tags")
    tags = cur.fetchall()
    cur.close()

    tagsList = []
    for tag in tags:
        tagsList.append(tag['TagName'])

    return render_template('edit_destination.html', form=form, tags=tagsList)

@app.route('/add_image/<string:id>', methods=['POST', 'GET'])
@is_logged_in
def add_image(id):
    form = DestImageForm(request.form)

    cur = connection.cursor()
    cur.execute("SELECT DestName "
                "FROM destinations "
                "WHERE DestID = %s"
                , ([id]))

    dest = cur.fetchone()

    if request.method == 'POST' and form.validate():
        imgUrl = form.imgUrl.data

        cur = connection.cursor()
        cur.execute("INSERT INTO dest_images "
                    "VALUES (%s, %s)",
                    (id, imgUrl))

        connection.commit()
        cur.close()

        flash('Image successfully upload.', 'success')
        return redirect(url_for('destinations'))

    return render_template('add_image.html', dest = dest, form=form)


@app.route('/account')
@is_logged_in
def account():
    cur = connection.cursor()
    cur.execute("SELECT f.DestID, DestName "
                "FROM favorites f JOIN destinations d ON d.DestID = f.DestID JOIN users u on u.UserID = f.UserID "
                "WHERE f.UserID = %s"
                , [session['user']])
    favorites = cur.fetchall()

    return render_template('account.html', favorites=favorites)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.secret_key='supersecretkey'
    app.run(port=8000, debug=True)
