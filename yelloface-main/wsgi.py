from werkzeug.utils import secure_filename
from flask import Flask, render_template, session, redirect, url_for, request, flash
import pymysql
import os
import string
from flask_wtf.csrf import CSRFProtect

ENDPOINT="database-2.ckyq3bzfwfat.us-east-1.rds.amazonaws.com"
PORT="3306"
USR="admin"
PASSWORD="942KfPX6VmtKcSK"
DBNAME="webapp"

def redirect_back(default='home'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

def user_check_logged():
    if "email" in session:
        return True
    
    return False

class DB:
    db = None
    def __init__(self):
        self.db = pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
    
    def front_page_ads(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM advert ORDER BY adv_id LIMIT 12")
        return cursor.fetchall()
    
    def user_by_mail(self,email):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s",(email,))
        results = cursor.fetchall()
            
        if len(results) != 1:
            return None
            
        return results[0]
    
    def user_check_creds(self,email,password):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s",(email,password))
        results = cursor.fetchall()
            
        if len(results) != 1:
            return False
            
        return True
    
    def user_register(self,email,password):
        cursor = self.db.cursor()
        
        if cursor.execute("INSERT INTO user (email,password) VALUES (%s, %s)",(email,password)) != 1:
            return False
        
        self.db.commit()
        
        return True
    
    def user_change_password(self,email,password):
        cursor = self.db.cursor()
        
        if cursor.execute("UPDATE user SET password = '%s' WHERE email = '%s'",(password,email)) != 1:
            return False
        
        self.db.commit()
        return True
    
    def advert_add(self,title, email, phone, street, postal, building, flat, city, www, owner):
        cursor = self.db.cursor()
        
        if cursor.execute("INSERT INTO advert (title, email, phone, street, postal, building, flat, city, www, owner) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                          (title, email, phone, street, postal, building, flat, city, www, owner)) != 1:
            return False
        
        self.db.commit()
        
        return True
    
    def advert_update(self,email, phone, street, postal, building, flat, city, www, owner):
        cursor = self.db.cursor()
        
        if cursor.execute("UPDATE advert SET (title=%s, email=%s, phone=%s, street=%s, postal=%s, building=%s, flat=%s, city=%s, www=%s)",
                          (title, email, phone, street, postal, building, flat, city, www)) != 1:
            return False
        
        self.db.commit()
        
        return True
    
    def advert_by_id(self,id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s",(email,))
        results = cursor.fetchall()
            
        if len(results) != 1:
            return None
            
        return results[0]
    
    def advert_search(self,query):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM advert WHERE MATCH(title, email, phone, street, postal, building, flat, city, www) AGAINST(%s)",(query,))
        return cursor.fetchall()
    
    def advert_delete(self,id):
        cursor = self.db.cursor()
        
        if cursor.execute("DELETE FROM advert WHERE adv_id = %d",(id,)) != 1:
            return False
        
        self.db.commit()
        
        return True
    
    @staticmethod
    def init_db():
        db = pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS user")
        cursor.execute("CREATE TABLE user (user_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255), password VARCHAR(255), UNIQUE(email))")
        cursor.execute("DROP TABLE IF EXISTS advert")
        cursor.execute("CREATE TABLE advert (adv_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), email VARCHAR(255), phone VARCHAR(255), \
                            street VARCHAR(255), postal VARCHAR(255), building VARCHAR(255), flat VARCHAR(255), city VARCHAR(255), www VARCHAR(255), owner INT(11), FULLTEXT(title, email, phone, street, postal, building, flat, city, www))")
        
        
app = Flask(__name__)
app.secret_key = b'_cbtu(n8utm*8xt$ym7&rt7'
csrf = CSRFProtect(app)
app.jinja_env.globals.update(is_logged=user_check_logged)

@app.route('/',methods=["GET"])
@app.route('/index.html', methods=["GET"])
def home():
    try:
        db = DB()
        print(db.front_page_ads())
        return render_template("index.html", ads=db.front_page_ads())
    except Exception as e:
        flash("/index.html failed due to {}".format(e))
        return render_template("index.html")

@app.route("/user/login.html", methods = [ "GET", "POST" ])
def user_login():
    if user_check_logged():
        return redirect(redirect_back())
    
    try:
        if request.method == 'POST':
            db = DB()
            
            if not "email" in request.form or not "password" in request.form or len(request.form["email"]) == 0 or len(request.form["password"]) == 0:
                flash("/user/login.html failed due to invalid form data")
                return render_template("login.html")
            
            if db.user_check_creds(request.form["email"],request.form["password"]):
                flash("Login successful")
                session["email"] = request.form["email"]
                session["uid"] = db.user_by_mail(request.form["email"])[0]
                return redirect("/")
            else:
                flash("Login failed")
                return render_template("login.html")
        else:
            return render_template("login.html")
    except Exception as e:
        flash("/user/login.html failed due to {}".format(e))
        return render_template("login.html")

@app.route("/user/register.html", methods = [ "GET", "POST" ])
def user_register():
    if user_check_logged():
        return redirect(redirect_back())
    
    try:
        db = DB()
        
        if request.method == 'POST':
            if not "email" in request.form or not "password" in request.form or not "retype" in request.form \
                or len(request.form["email"]) == 0 or len(request.form["password"]) == 0 or len(request.form["retype"]) == 0:
                flash("User register failed invalid form data")
                return render_template("register.html")
            
            if db.user_register(request.form["email"],request.form["password"]):
                flash("User register successful")
                return redirect("/")
        else:
            return render_template("register.html")
        
    except Exception as e:
        flash("/user/register.html failed due to {}".format(e))
        return render_template("register.html")

@app.route("/user/update.html", methods = [ "GET", "POST" ])
def user_update():
    if not user_check_logged():
        return redirect(redirect_back())
    
    try:
        db = DB()
        
        if request.method == 'POST':
            if not "password" in request.form or not "retype" in request.form or len(request.form["password"]) == 0 or len(request.form["retype"]) == 0:
                flash("User update failed invalid form data")
                return render_template("update.html")
            
            if db.user_update(session["email"],request.form["password"]):
                flash("User update successful")
                return redirect("/")
        else:
            return render_template("update.html",user=db.user_by_mail(session["email"]))
        
    except Exception as e:
        flash("/user/update.html failed due to {}".format(e))
        return render_template("user_update.html")

@app.route("/user/logout.html", methods = [ "GET" ])
def user_logout():
    if not user_check_logged():
        return redirect(redirect_back())
    
    session.clear()
    
    return redirect("/")
    
@app.route("/ad/add.html", methods = [ "GET", "POST" ])
def adv_add():
    if not user_check_logged():
        return redirect(redirect_back())

    try:
        if request.method == 'POST':
            db = DB()
            
            if not "email" in request.form or not "phone" in request.form or not "street" in request.form or not "postal" in request.form or not "building" in request.form or not "flat" in request.form or not "city" in request.form or not "www" in request.form or len(request.form["email"]) == 0 or len(request.form["phone"]) == 0 or len(request.form["street"]) == 0 or len(request.form["postal"]) == 0 or len(request.form["building"]) == 0 or len(request.form["flat"]) == 0 or len(request.form["city"]) == 0 or len(request.form["www"]) == 0:
                flash("Failed to add advertisement invalid form data")
                return render_template("advert_add.html")

            if db.advert_add(request.form["title"], request.form["email"], request.form["phone"], request.form["street"], request.form["postal"], request.form["building"], request.form["flat"], request.form["city"], request.form["www"], session["uid"]):
                flash("advertisement added successfuly")
                return render_template("advert_add.html")
            else:
                flash("Failed to add advertisement")
                return render_template("advert_add.html")
        else:
            return render_template("advert_add.html")
    except Exception as e:
        flash("/ad/add.html failed due to {}".format(e))
        return render_template("advert_add.html")

@app.route("/ad/edit/<int:adv_id>.html", methods = [ "GET", "POST" ])
def adv_edit(adv_id):
    if not user_check_logged():
        return redirect(redirect_back())
    
    try:
        db = DB()
        
        if request.method == 'POST':
            if not "email" in request.form or not "phone" in request.form or not "street" in request.form or not "postal" in request.form or not "building" in request.form or not "flat" in request.form or "city" in request.form or "www" in request.form or len(request.form["email"]) == 0 or len(request.form["phone"]) == 0 or len(request.form["street"]) == 0 or len(request.form["postal"]) == 0 or len(request.form["building"]) == 0 or len(request.form["flat"]) == 0 or len(request.form["city"]) == 0 or len(request.form["www"]) == 0:
                flash("Failed to add advertisement invalid form data")
                return redirect("/")
            
            if db.advert_update(request.form["email"], request.form["phone"], request.form["street"], request.form["postal"], request.form["building"], request.form["flat"], request.form["city"], request.form["www"]) != 1:
                flash("Failed to update advertisement")
                return redirect("/")
            
            flash("Advertisement updated")
            return redirect("/")
        else:
            return render_template("advert_edit.html", advert=db.advert_by_id(adv_id))
        
    except Exception as e:
        flash("/ad/edit.html failed due to {}".format(e))
        return render_template("advert_edit.html")

@app.route("/ad/delete/<int:adv_id>.html",methods = [ "GET"])
def adv_delete(adv_id):
    if not user_check_logged():
        return redirect(redirect_back())
    
    try:
        db = DB()
        db.adv_delete(adv_id)
        return redirect(redirect_back())
        
    except Exception as e:
        flash("/ad/delete.html failed due to {}".format(e))
        return render_template("advert_delete.html")

@app.route("/ad/search.html", methods = [ "POST", "GET" ])
def adv_search():
    try:
        db = DB()
        
        if request.method == 'POST':
            if not "query" in request.form:
                flash("Failed to search query missing")
                return render_template("advert_search.html")
            return render_template("index.html", ads=db.advert_search(request.form["query"]))
        else:
            return render_template("index.html")
    except Exception as e:
        flash("/ad/search.html failed due to {}".format(e))
        return render_template("index.html")

@app.route("/adv/<int:adv_id>.html", methods = [ "GET" ])
def adv_view(adv_id):
    try:
        db = DB()
        return render_template("advert_view.html",advert=db.advert_by_id(adv_id))
    except Exception as e:
        flash("/ad/search.html failed due to {}".format(e))
        return render_template("advert_view.html")

@app.route("/initialize", methods = [ "GET" ])
def initialize():
    try:
        db = DB()
        db.init_db()
        return redirect("/")
    except Exception as e:
        flash("Database initialize failed due to {}".format(e))
        return redirect("/")

if __name__== "__main__":
    app.run(debug=True)
