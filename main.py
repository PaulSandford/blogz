from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import verify



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
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
    name = db.Column(db.String(16))#distinct = True ??
    password = db.Column(db.String(32))
    blogs = db.relationship('Blog', backref='user', lazy=True)

    def __init__(self, name, password):
        self.name = name
        self.password = password
    #blogs = db.Column(db.String(16))  group = db.relationship(Group, backref='users')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'singleUser', 'blog']
    if request.endpoint not in allowed_routes and 'id' not in session:
        session['id'] = 'fruit'
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    session['id'] = 'fruit'
    return render_template('index.html',title="User Listing", ses=session['id'], users=users)
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    session['id'] = 'fruit'
    if request.method == 'GET':
        return render_template('login.html', title="Login", ses=session['id'])
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = User.query.all()
        for use in users:
            if use.name == username:
                user = User.query.get(use.id)
                break
        
        if user.name == username and user.password == password:
            session['id'] = user.id
            
            flash("Logged In")
            return render_template('addblog.html',title=username, ses=session['id'])
        else:
            return render_template('login.html', title="Login", ses=session['id'], error="Invalid Login", username=username)

@app.route('/logout')
def logout():
    session['id']= 'fruit'
    return redirect('/')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', title="Sign Up", ses=session['id'])
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        v_pwd = request.form['v_pwd']
        
        user = None
        username_error, pwd_error = verify.create(username, password, v_pwd)
        users = User.query.all()
        for use in users:
            if use.name == username:
                user = User.query.get(use.id)
                break
        
        
        if user != None:
            username_error = "Username exists"
        
        if username_error == "" and pwd_error == "":
            new_user= User(username, password)
            
            #this chunk is to prevent duplicate creations
            if user != None:
                if user.name == username:
                    return render_template('login.html',title="Login", ses=session['id'])

            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html',title="Login", ses=session['id'])
        else:
            return render_template('signup.html', title="Sign Up", ses=session['id'], username_error=username_error, username=username, pwd_error = pwd_error)
    

@app.route('/blog')
def blog():
    blog_id = request.args.get('blog_id')
    
    if blog_id != None:
        blog = Blog.query.get(blog_id)
        user = User.query.get(blog.user_id)
        return render_template('singlepost.html',title=blog.title, ses=session['id'], blog=blog, name=user.name)
    
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('blogs.html',title="Build-a-Blog", ses=session['id'], 
        blogs=blogs, users=users)

@app.route('/singleUser')
def user():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    blogs = Blog.query.filter_by(user_id=user_id)
    return render_template('singleUser.html',title="User Name", ses=session['id'], blogs=blogs, name=user.name)

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
    return render_template('addblog.html',title="Build-a-Blog", ses=session['id'])

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
        return render_template("addblog.html",title="Build-a-Blog", ses=session['id'], body_error=body_error, title_error=title_error,blog_title=blog_title,blog_body=blog_body)

    new_blog = Blog(blog_title, blog_body, session['id'])
    
    #this section is a measure to prevent redundant posts on refresh or other.
    blog_c = Blog.query.filter_by(title=blog_title)
    for blog in blog_c:
        if blog.body == new_blog.body:
            if session['id'] == blog.user_id:
                user = User.query.get(session['id'])
                blog = Blog.query.get(new_blog.id)
                return render_template('singlepost.html', title=blog.title, ses=session['id'], blog=blog, name=user.name)

    db.session.add(new_blog)
    db.session.commit()
    #add a query request for redirect
    user = User.query.get(session['id'])
    blog = Blog.query.get(new_blog.id)
    return render_template('singlepost.html', title=blog.title, ses=session['id'], blog=blog, name=user.name)

@app.route('/delete-blog', methods=['POST'])
def delete_blog():
    
    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    if session['id'] == blog.user_id:
        db.session.delete(blog)
        db.session.commit()
        return redirect('/blog')
    else:
        flash("Don't be a horrible person")
        return redirect('/blog')


if __name__ == '__main__':
    app.run()