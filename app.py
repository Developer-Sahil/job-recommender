import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# Resume matching imports
from backend.ml.model import match_jobs
from backend.ml.processes import process_resume
from backend.utilities.resume_parser import parse_resume

# User model
from backend.models.user import db, User
from backend.models.job import Job

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    user_exists = False
    user_not_found = request.args.get("user_not_found", False)

    if request.method == "POST":
        existing_user = User.query.filter(
            (User.email == request.form["email"]) | (User.username == request.form["username"])
        ).first()
        
        if existing_user:
            user_exists = True
        else:
            hashed_pw = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
            user = User(
                username=request.form["username"],
                email=request.form["email"],
                password=hashed_pw,
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))

    return render_template("register.html", user_exists=user_exists, user_not_found=user_not_found)




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if not user:
            return redirect(url_for("register", user_not_found=True))  # Redirect to register with flag

        if bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Incorrect password.", "danger")

    return render_template("login.html")



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/jobs")
@admin_required
def admin_jobs():
    jobs = Job.query.all()
    return render_template("admin_jobs.html", jobs=jobs)

@app.route("/admin/job/new", methods=["GET", "POST"])
@admin_required
def new_job():
    if request.method == "POST":
        job = Job(
            title=request.form["title"],
            company=request.form["company"],
            description=request.form["description"],
            skills=request.form["skills"]
        )
        db.session.add(job)
        db.session.commit()
        flash("Job added successfully.", "success")
        return redirect(url_for("admin_jobs"))
    return render_template("edit_job.html", job=None)

@app.route("/admin/job/edit/<int:job_id>", methods=["GET", "POST"])
@admin_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == "POST":
        job.title = request.form["title"]
        job.company = request.form["company"]
        job.description = request.form["description"]
        job.skills = request.form["skills"]
        db.session.commit()
        flash("Job updated.", "success")
        return redirect(url_for("admin_jobs"))
    return render_template("edit_job.html", job=job)

@app.route("/admin/job/delete/<int:job_id>")
@admin_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted.", "warning")
    return redirect(url_for("admin_jobs"))


@app.route("/", methods=["GET", "POST"])
@login_required

def home():
    if request.method == "POST":
        if "resume" not in request.files:
            return render_template("index.html", error="No resume uploaded.")
        resume = request.files["resume"]
        if resume.filename == "":
            return render_template("index.html", error="Empty filename. Please upload a valid file.")
        try:
            text = parse_resume(resume)
            processed_text = process_resume(text)
            matches = match_jobs(processed_text)
            return render_template("index.html", matches=matches)
        except Exception as e:
            return render_template("index.html", error=str(e))
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures users.db gets created
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
