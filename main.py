from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(255))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')


@app.route('/blog', defaults={'blog_id' : 'All'})
@app.route('/blog/<blog_id>')# one of these two are working
@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    if blog_id != 'All':
        blog = Blog.query.get(int(blog_id))
        return render_template('singlepost.html',title=blog.title,blog=blog)
    
    blogs = Blog.query.all()
    return render_template('blogs.html',title="Build-a-Blog", 
        blogs=blogs)

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

    new_blog = Blog(blog_title, blog_body)
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