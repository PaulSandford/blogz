from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import verify



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    def __init__(self, title, body, user_id):
        self.title = title
        self.body = body
        self.user_id = user_id

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    password = db.Column(db.String(32))
    blogs = db.relationship('Blog', backref='user', lazy=True)

    def __init__(self, name, password):
        self.name = name
        self.password = password
    #blogs = db.Column(db.String(16))  group = db.relationship(Group, backref='users')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'user', 'blog']
    if request.endpoint not in allowed_routes and 'id' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html',title="User Listing", users=users)
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title="Login")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(name=username)

        if user and user.password == password:
            session['id'] = user.id
            flash("Logged In")
            return render_template('addblog.html',title=username)
        else:
            return render_template('login.html', title="Login", error="Invalid Login", username=username)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', title="Sign Up")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        v_pwd = request.form['v_pwd']

        username_error, pwd_error = verify.create(username, password, v_pwd)
        user = User.query.filter_by(name=username)
        if user != None:
            username_error = "Username exists"
        
        if username_error == "" and pwd_error == "":
            new_user= User(username, password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('addblog.html',title=username)
        else:
            return render_template('signup.html', title="Sign Up", username_error=username_error, username=username, pwd_error = pwd_error)
    

@app.route('/blog')
def blog():
    blog_id = request.args.get('blog_id')
    
    if blog_id != None:
        blog = Blog.query.get(int(blog_id))
        return render_template('singlepost.html',title=blog.title,blog=blog)
    
    blogs = Blog.query.all()
    return render_template('blogs.html',title="Build-a-Blog", 
        blogs=blogs)

@app.route('/user')
def user():
    user_id = request.args.get('user_id')
    user = User.query.filter_by(id=user_id)
    blogs = Blog.query.filter_by(user_id=user_id)
    return render_template('singleUser.html',title="User Name", blogs=blogs, user=user)

#@app.route('/blog', defaults={'blog_id' : 'All'})    Original Attempt
#@app.route('/blog/<blog_id>')# one of these two are working
#@app.route('/blog/<int:blog_id>')
#def blog(blog_id):
#    if blog_id != 'All':
#        blog = Blog.query.get(int(blog_id))
#        return render_template('singlepost.html',title=blog.title,blog=blog)
#    
#    blogs = Blog.query.all()
#    return render_template('blogs.html',title="Build-a-Blog", 
#        blogs=blogs)

@app.route('/addblog')
def addblog():
    return render_template('addblog.html',title="Build-a-Blog")

@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():
    blog_title = request.form['title']
    blog_body = request.form['body']
    body_error = ""
    title_error = ""

    if blog_title == "":
        title_error = "Give your blog a title"
    if blog_body == "":
        body_error = "Tell us something"
    if body_error != "" or title_error != "":
        return render_template("addblog.html",title="Build-a-Blog",body_error=body_error,title_error=title_error,blog_title=blog_title,blog_body=blog_body)

    new_blog = Blog(blog_title, blog_body, session['id'])
    db.session.add(new_blog)
    db.session.commit()
    #add a query request for redirect
    blog = Blog.query.get(new_blog.id)
    return render_template('singlepost.html',title=blog.title,blog=blog)

@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()

    return redirect('/blog')


if __name__ == '__main__':
    app.run()