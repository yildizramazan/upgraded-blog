from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime


app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = 'anything-you-want'
Bootstrap5(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


class PostForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    name = StringField('Your Name', validators=[DataRequired()])
    img_url = StringField('Blog Image URL', validators=[DataRequired(), URL(message="Please Enter A Valid URL")])
    body = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit')


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()



@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route('/show-post/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = PostForm()
    h1 = "New Post"
    if form.validate_on_submit():
        blog_title = form.title.data
        blog_subtitle = form.subtitle.data
        blog_author = form.name.data
        blog_img = form.img_url.data
        blog_body = form.body.data

        new_blog = BlogPost(
            title = blog_title,
            subtitle = blog_subtitle,
            author = blog_author,
            img_url = blog_img,
            body = blog_body,
            date = datetime.now().strftime("%B %d %Y")
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, h1=h1)





@app.route('/edit-post/<int:post_id>', methods= ["GET","POST"])
def edit_post(post_id):
    h1 = "Edit Post"
    post_to_edit = db.get_or_404(BlogPost, post_id)
    edit_form = PostForm(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        img_url=post_to_edit.img_url,
        name=post_to_edit.author,
        body=post_to_edit.body
    )
    if edit_form.validate_on_submit():
        post_to_edit.title = edit_form.title.data
        post_to_edit.subtitle = edit_form.subtitle.data
        post_to_edit.author = edit_form.name.data
        post_to_edit.body = edit_form.body.data
        post_to_edit.img_url = edit_form.img_url.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_to_edit.id))
    return render_template("make-post.html", h1=h1, form=edit_form)

@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5004)
