from .database import db

class new_user(db.Model):
    """
    Table for user ID and password to log in.
    """
    __tablename__ = 'Credentials'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_ID = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable=False)

class tracker_table(db.Model):
    """
    Table to store list of trackers.
    """
    __tablename__ = 'tracker_list'
    ID = db.Column(db.Integer, nullable=False, primary_key=True, unique=True, autoincrement=True)
    tracker_name = db.Column(db.String, nullable=False)
    User_ID = db.Column(db.Integer, nullable=False)
    tracker_data_type = db.Column(db.String, nullable=False)
    units = db.Column(db.String, nullable=False)
    Description = db.Column(db.String)

class tracker_data(db.Model):
    """
    Table to store data of all trackers
    """
    __tablename__ = 'Tracker_data'
    s_no = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    tracker_ID = db.Column(db.Integer, nullable=False)
    user_ID = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)
    notes = db.Column(db.String)
