Using vertual environment is good practive.
below are the libraries required to run the app

Flask==2.2.5
Flask-JWT-Extended==3.18.2
Flask-RESTful==0.3.9
PyJWT==1.7.1
SQLAlchemy==2.0.23
Werkzeug==2.2.3

Source file is api.py file
Go to api.py file location on the terminal/command prompt

To persist the models to DB:
Then run the python on terminal to enter into python interactive mode

```>>> from api import app, db
>>> app.app_context().push()
>>> db.create_all()```

Above commands will create tables into Database.

To verify if table or created or not, run following commands on your command line.

D:>sqlite3 D:\inmar_git\inmar_jwt_auth\inmar_db.sqlite #sqlite db location
SQLite version 3.36.0 2021-06-18 18:36:39
Enter ".help" for usage hints.
sqlite> .table
location  user

Once steps are successfull, you can verify the APIs using postman.

To generate the token use below API.
http://127.0.0.1:5000/login






 