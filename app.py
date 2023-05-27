from flask import Flask, request, flash, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taarikh.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)
bcrypt=Bcrypt(app)

class Admin(db.Model):
   email = db.Column(db.String(100), primary_key=True)
   password = db.Column(db.String(100))


   def __init__(self, email, password):
      self.email = email
      self.password = bcrypt.generate_password_hash(password).decode('utf-8')
      
class Advocate(db.Model):
   license_number = db.Column(db.String(100), primary_key=True)
   advocate_name = db.Column(db.String(100))
   email = db.Column(db.String(100))
   password = db.Column(db.String(100))


   def __init__(self, license_number, advocate_name, email, password):
      self.license_number = license_number
      self.advocate_name = advocate_name
      self.email = email
      self.password = bcrypt.generate_password_hash(password).decode('utf-8')
      
   
class Client(db.Model):
   id = db.Column(db.Integer,primary_key=True)
   name = db.Column(db.String(100),nullable=False)
   email = db.Column(db.String(100), primary_key=True)
   mobile = db.Column(db.String(10),nullable=False)



   def __init__(self, id, name,email, mobile):
      self.id = id
      self.name = name
      self.email = email
      self.mobile = mobile
      
class Case(db.Model):
   case_number = db.Column(db.Integer, primary_key=True)
   case_name = db.Column(db.String(300))
   client_name = db.Column(db.String(100), db.ForeignKey(Client.name))
   opponent = db.Column(db.String(300))
   court = db.Column(db.String(100))
   case_type = db.Column(db.String(100))
   description = db.Column(db.String(1000))
   opponent_advocate = db.Column(db.String(100))
   judge = db.Column(db.String(100))
   filing_date = db.Column(db.Date)
   assigned_advocates = db.Column(db.String(1000))

   def __init__(self, case_number, case_name,client_name, opponent, court, case_type, description, opponent_advocate, judge, filing_date, assigned_advocates):
      self.case_number = case_number
      self.case_name = case_name
      self.client_name = client_name
      self.opponent = opponent
      self.court = court
      self.case_type = case_type
      self.description = description
      self.opponent_advocate = opponent_advocate
      self.judge = judge
      self.filing_date = filing_date
      self.assigned_advocates = assigned_advocates
   
class Hearings(db.Model):
   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   case_number = db.Column(db.String(300))
   license_number = db.Column(db.String(100), db.ForeignKey(Advocate.license_number))
   description = db.Column(db.String(1000))
   hearing_date = db.Column(db.Date)
   next_hearing_date = db.Column(db.Date)

   def __init__(self, case_number, id,license_number, hearing_date, next_hearing_date, case_type, description, hearing_date_advocate, judge, filing_date, assigned_advocates):
      self.case_number = case_number
      self.id = id
      self.license_number = license_number
      self.hearing_date = hearing_date
      self.next_hearing_date = next_hearing_date
      self.description = description


@app.route('/')
def index():
   return render_template('index.html')

@app.route('/login-firm', methods=["POST", "GET"])
def loginfirm():
   if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
   
      user = Admin.query.filter_by(email=email).first()
      if user and bcrypt.check_password_hash(user.password, password):
         flash('Logged in successfully!', 'success')
         return render_template('admin_home.html')
      else:
         flash('Invalid email or password', 'error')
   return render_template('loginfirm.html')



#login for advocate
@app.route('/login-ind', methods=["POST", "GET"])
def loginInd():
   if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
   
      user = Advocate.query.filter_by(email=email).first()
      if user and bcrypt.check_password_hash(user.password, password):
         flash('Logged in successfully!', 'success')
         return render_template('advocate_home.html')
      else:
         flash('Invalid email or password', 'error')
   return render_template('loginindiv.html')



#create new client
@app.route('/add_client',methods=["POST"])
def addclient():
   id = request.form['id']
   name = request.form['name']
   email = request.form['email']
   mobile = request.form['mobile']

   new_client = Client(id=id, name=name, email=email, mobile=mobile)
   db.session.add(new_client)
   db.session.commit()
   
   flash('Client added successfully!', 'success')
   return render_template('same.html')

#get all cases
@app.route('/cases',methods=["GET"])
def cases():
   license_number = current_user.license_number()
   cases = Case.query.filter_by(license_number = license_number).order_by(Case.id).all()
   case_list = []
   for case in cases:
      case_data = {
         'Case_number': Case.case_number,
         'name': Case.case_name,
         'hearing_date': Case.hearing_date.strftime('%Y-%m-%d'),
         'court':Case.court
        }
      case_list.append(case_data)
   return jsonify(case_list)
   
   
#get dated cases
@app.route('/datedcases',methods=["GET"])
def datedcases():
   licence_number = current_user.licence_number()
   date = request.args.get('date')
   cases = Case.query.filter_by(licence_number = licence_number, hearing_date=date).order_by(Case.id).all()
   case_list = []
   for case in cases:
      case_data = {
         'Case_number': case.case_number,
         'name': case.case_name,
         'hearing_date': case.hearing_date.strftime('%Y-%m-%d'),
         'court':case.court
        }
      case_list.append(case_data)
   return jsonify(case_list)



#add advocate
@app.route('/add-advocate',methods=["POST"])   
def addadvocate():
   licence_number = request.form['licence_number']
   advocate_name = request.form['advocate_name']
   email = request.form['email']
   password = request.form['password']
   
   new_advocate = Advocate(licence_number=licence_number, advocate_name=advocate_name, email=email, password=password)
   db.session.add(new_advocate)
   db.session.commit()
   
   flash("Advocate added succesfully", "success")
   return render_template("firm.html")


#add cases

@app.route('/add-case',methods=["post"])
def addcase():
   case_number = request.form['case_number']
   case_name = request.form['case_name']
   client_name = request.form['client_name']
   opponent = request.form['opponent']
   court =request.form['court']
   case_type = request.form['case_type']
   description = request.form['description']
   opponent_advocate = request.form['opponent_advocate']
   judge = request.form['judge']
   filing_date = request.form['filing_date']
   assigned_advocates = request.form['assigned_advocates']
   
   
   new_case = Case(case_number = case_number, case_name=case_name, client_name=client_name, opponent=opponent, court=court, case_type = case_type, description=description, opponent_advocate=opponent_advocate, judge=judge,filing_date=filing_date, assigned_advocates=assigned_advocates)
   db.session.add(new_case)
   db.session.commit()
   flash("Case added succefully","success")
   return render_template('firm.html')

#add hearing
@app.route('/add-hearing',methods=["POST"])
def addhearing():
   case_number = request.form['case_number']
   id = request.form['id']
   license_number = request.form['license_number']
   hearing_date = request.form['hearing_date']
   next_hearing_date = request.form['next_hearing_date']
   description = request.form['description']
   
   new_hearing = Hearings(case_number = case_number, id=id, license_number=license_number, hearing_date=hearing_date, next_hearing_date=next_hearing_date,description=description)
   db.session.add(new_hearing)
   db.session.commit()
   
   
   flash("Hearing details added", "success")
   return render_template("firm.html")
   
if __name__ == '__main__':
   with app.app_context():
      db.create_all()
      app.run(debug = True)