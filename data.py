import csv, random
from flask import Flask
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ("mssql://@KEVINKAGWIMA/insuarance?driver=SQL SERVER")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bcrypt = Bcrypt()
db.init_app(app)

def main():
  f = open("data.csv")
  reader = csv.reader(f)

  for id,name,category,cost,avg_score,major in reader:
    major_insurance = Insurance_covers(
      id=id,
      unique_id=random.randint(10000000,99999999),
      name=name,
      category=category,
      cost=cost,
      avg_score=avg_score,
      major_category=major
    )
    db.session.add(major_insurance)
    db.session.commit()

if __name__ == '__main__':
  with app.app_context():
    main()
