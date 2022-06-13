import os, random, datetime
from flask import Flask, render_template, request, flash,redirect, url_for
from flask_login import current_user, login_manager, LoginManager, login_user, login_required, logout_user
from questions import Life_insurance, Health_insurance, auto_insurance
from models import *
from form import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql://@KEVINKAGWIMA/insuarance?driver=SQL SERVER"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = os.environ['Hms_secret_key']

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = '/member-authentication'
login_manager.login_message_category = "danger"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  try:
    return User.query.filter_by(phone_number=user_id).first()
  except:
    flash(f"Failed to login the user", category="danger")

@app.route("/member-registration", methods=["POST", "GET"])
def registration():
  form = member_registration()
  if form.validate_on_submit():
    new_member = User(
      unique_id = random.randint(10000000, 99999999),
      first_name = form.first_name.data,
      last_name = form.last_name.data,
      age = form.age.data,
      phone_number = form.phone_number.data,
      email = form.email_address.data,
      passwords = form.password.data
    )
    db.session.add(new_member)
    db.session.commit()
    flash(f"Registration successfull", category="success")
    return redirect(url_for('login'))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}", category="danger")
    return redirect(url_for('registration'))

  return render_template("register.html", form=form)

@app.route("/member-authentication", methods=["POST", "GET"])
def login():
  form = member_login()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email_address.data).first()
    if user and user.check_password_correction(attempted_password=form.password.data):
      login_user(user, remember=True)
      flash(f"Login successfull", category="success")
      return redirect(url_for('home'))
    elif user is None:
      flash(f"No user with that email address", category="danger")
      return redirect(url_for('login'))
    else:
      flash(f"Invalid credentials", category="danger")
      return redirect(url_for('login'))

  return render_template("login.html", form=form)

@app.route("/logout")
def logout():
  logout_user()
  flash(f"Logout successfull", category="success")
  return redirect(url_for('login'))

@app.route("/")
@app.route("/home")
def home():
  if current_user.is_authenticated:
    session = Session.query.filter_by(user=current_user.id, status="Active").first()
    return render_template("home.html", session=session)
  else:
    return render_template("home.html")

@app.route("/session")
def session():
  session = Session.query.filter_by(user=current_user.id, status="Active").first()
  if session:
    flash(f"You have an active session, complete it before starting another one", category="warning")
    return redirect(url_for('questions'))
  new_session = Session(
    session_id = random.randint(10000000,99999999),
    user = current_user.id,
    start_date = datetime.datetime.now(),
    status = "Active"
  )
  db.session.add(new_session)
  db.session.commit()
  flash(f"Your questions are ready", category="success")
  return redirect(url_for('questions'))

@app.route("/select-major-insurance", methods=["POST", "GET"])
@login_required
def select_major_insurance():
  session = Session.query.filter_by(user=current_user.id, status="Active").first()
  if session:
    selected_type = request.form.get("type")
    selected_beneficiary = request.form.get("beneficiary")
    if selected_type is None:
      flash(f"Please select an insurance cover", category="danger")
    elif selected_beneficiary is None:
      flash(f"Please select a beneficiary for the insurance cover", category="danger")
    else:
      session.major_insurance = selected_type
      session.beneficiary = selected_beneficiary
      db.session.commit()
      flash(f"Insurance Cover selected successfully", category="success")
    return redirect(url_for('questions'))
  else:
    flash(f"No session has been created", category="danger")
    return redirect(url_for('home'))

@app.route("/questions")
@login_required
def questions():
  session = Session.query.filter_by(user=current_user.id, status="Active").first()
  major_insurances = Major_Insurance.query.all()
  questions = Life_insurance.items()

  return render_template("questions.html", session=session, major_insurances=major_insurances, questions=questions)

@app.route("/answers", methods=["POST", "GET"])
@login_required
def answers():
  session = Session.query.filter_by(user=current_user.id, status="Active").first()
  major_Insurance = Major_Insurance.query.filter_by(id=session.major_insurance).first()
  answers = request.form.getlist("answer")
  for answer in answers:
    if answer is None:
      flash(f"Please fill in all the questions", category="danger")
    else:
      new_answer = Answers(
        unique_id = random.randint(10000000,99999999),
        choice = answer,
        Hash = bcrypt.generate_password_hash("12345").decode("utf-8"),
        user = current_user.id,
        major_Insurance = major_Insurance.id,
        session = session.id
      )
      db.session.add(new_answer)
      if answer == "Yes":
        new_answer.point = 5
      else:
        new_answer.point = 2
    session.end_date = datetime.datetime.now()
    session.status = "Closed"
    # db.session.commit()
    flash(f"{len(answers)} answers received", category="success")
    return redirect(url_for('recommended_cover'))

@app.route("/recommended-cover")
def recommended_cover():
  session = Session.query.filter_by(user=current_user.id, status="Active").first()
  answers = Answers.query.filter_by(session=session.id).all()
  total_cost = []
  for answer in answers:
    total_cost.append(answer.point)
  return render_template("animate.html", info=f"Finding the best cover for you {sum(total_cost)}"), {"Refresh": f"8; url=http://127.0.0.1:5000/home"}

@app.route("/summary")
@login_required
def portal():
  session = Session.query.filter_by(user=current_user.id, status="Closed").first()
  if session:
    major_Insurance = Major_Insurance.query.filter_by(id=session.major_insurance).first()
    answers = Answers.query.filter_by(user=current_user.id, session=session.id).all()
    return render_template("portal.html", session=session, major_Insurance=major_Insurance, answers=answers)

  return render_template("portal.html")

if __name__ == '__main__':
  app.run(debug=True)
