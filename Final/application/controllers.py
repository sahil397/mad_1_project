from datetime import datetime
from time import time
from flask import Flask, request, session, redirect
from flask import render_template, url_for
from flask import current_app as app
from matplotlib.pyplot import plot
from application.models import new_user, tracker_table, tracker_data
from application.database import db
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

def plot_graph(user_id):
    user_trackers = tracker_table.query.filter(tracker_table.User_ID == user_id).all()
    
    x_list = []
    y_list = []
    count = 0
    for i in user_trackers:
        x_list.append(i.tracker_name)
        plot_data = tracker_data.query.filter(tracker_data.user_ID == user_id, tracker_data.tracker_ID == i.ID).all()
        for j in plot_data:
            count = count + int(j.value)
        y_list.append(count)
        count = 0

    fig = plt.figure(figsize = (7, 5))
 
    # creating the bar plot
    plt.bar(x_list, y_list, color ='blue', width = 0.4)
    
    plt.xlabel("Trackers")
    plt.ylabel("Count")
    plt.title("Trackers count")
    plot_path = "static/graphs/all_tracker.png"
    plt.savefig(plot_path)
    plt.close()

    return plot_path

# route to plot individual graph
@app.route("/tracker/individual_graph/<string:name>/<int:uid>", methods=["POST", "GET"])
def plot_individual_graph(name, uid):
    # to plot individual graph
    if request.method=="GET":

        x_list = []
        y_list = []

        tracker = tracker_table.query.filter(tracker_table.tracker_name == name, tracker_table.User_ID == uid).first()
        plot_data = tracker_data.query.filter(tracker_data.tracker_ID == tracker.ID).order_by(tracker_data.s_no.desc()).all()

        for point in plot_data:
            x_list.append(point.timestamp)
            y_list.append(int(point.value))

        x_list = x_list[::-1]
        y_list = y_list[::-1]

        fig = plt.figure(figsize = (7, 5))
        plt.xlabel("Timestamps")
        plt.ylabel("Value")
        plt.title(name)
        plt.tight_layout()

        plt.plot(x_list, y_list, '-rD')
        plt.gcf().autofmt_xdate()
        plt.savefig("static/graphs/individual.png")
        plt.close()
            
    return redirect(url_for("main_page", uid=uid))

@app.route("/", methods=["GET", "POST"])
def login_page():
    if request.method=="GET":
        return render_template("login.html")
    
    if request.method == "POST":
        # read username from login form
        username = request.form.get("username")
        # read password from login form
        password = request.form.get("password")
        # take first value of user id from credentials database
        print ("username", username)
        print ("password", password)
        temp_user=new_user.query.filter_by(User_ID=username).first()
        print ("query result", temp_user.password)
        # verify if user exists and password is same

        if username is None or password is None:
            return redirect("/")

        else:
            if temp_user is not None and temp_user.password == password:
                session["username"] = username
                
                tracker_list = []

                session["tracker_list"] = tracker_list

                # return render_template("index.html")
                return redirect(url_for("main_page", uid=temp_user.id))
            else:
                session["message"] = "Incorrect password, try again."
                return render_template("signup.html")

@app.route("/index/<int:uid>", methods=["GET", "POST"])
def main_page(uid):
    plot_path = plot_graph(uid)
    print("plot path", plot_path)
    if request.method=="GET":
        # fetch trackers for respective user
        user_tracker_list = tracker_table.query.filter(tracker_table.User_ID == uid)
        # define empty lists to store ID and names of trackers for respective user
        tracker_id_list = []
        tracker_name_list = []

        # iterate in trackers to read tracker ID'a and names
        for tracker in user_tracker_list:
            tracker_id_list.append(tracker.ID)
            tracker_name_list.append((tracker.ID,tracker.tracker_name, tracker.units))

        tracker_data_list = []
        trackers = tracker_data.query.filter(tracker_data.tracker_ID.in_(tracker_id_list)).all()

        for tracker in trackers:
            for id in tracker_name_list:
                if tracker.tracker_ID == id[0]:
                    tracker_data_list.append((id[1],
                                             tracker.timestamp,
                                             tracker.value,
                                             id[2],
                                             tracker.notes,
                                             id[0],
                                             tracker.s_no))   
        
        user_trackers = tracker_table.query.filter(tracker_table.User_ID == uid).all()

        all_tracker_list = []

        for j in user_trackers:
            all_tracker_list.append(j.tracker_name)

        # session["tracker_data"] = tracker_data_list
        return render_template("index.html", user_id=uid,tracker_data=tracker_data_list, all_tracker_list=all_tracker_list,path=plot_path)

# create route to add new log
@app.route("/tracker/add_new_log/<int:uid>", methods=["GET","POST"])
def add_new_log(uid):
    if request.method=="POST":
        if request.form:
            selected_tracker=request.form["tracker_name"]
            time=request.form["timestamp"]
            time=time.replace('T', ' ')
            timestamp=datetime.strptime(time, '%Y-%m-%d %H:%M')
            value=request.form["value"]
            notes=request.form["notes"]

            id = tracker_table.query.filter(tracker_table.User_ID == uid, tracker_table.tracker_name == selected_tracker).first()

            new_log = tracker_data(tracker_ID=id.ID,
                                   user_ID=uid,
                                   timestamp=timestamp,
                                   value=value,
                                   notes=notes)
            
            db.session.add(new_log)
            db.session.commit()
    
    return redirect(url_for("main_page", uid=uid))

# create route to add new tracker
@app.route("/tracker/add_new_tracker/<int:uid>", methods=["GET","POST"])
def add_new_tracker(uid):
    if request.method=="POST":
        if request.form:
            new_tracker_name=request.form["new_tracker_name"]
            new_tracker_description=request.form["tracker_description"]
            new_tracker_units=request.form["new_tracker_units"]
            new_tracker_type=request.form["new_tracker_type"]

            new_tracker = tracker_table(tracker_name=new_tracker_name,
                                        User_ID=uid,
                                        tracker_data_type=new_tracker_type,
                                        units=new_tracker_units,
                                        Description=new_tracker_description)
            
            db.session.add(new_tracker)
            db.session.commit()
        
    return redirect(url_for("main_page", uid=uid))

# create route to delete tracker
@app.route("/tracker/delete_tracker/<string:tracker_name>/<int:uid>")
def delete_tracker(tracker_name, uid):
    if request.method == "GET":
        selected = tracker_table.query.filter(tracker_table.tracker_name == tracker_name, tracker_table.User_ID == uid).first()
        tracker_logs = tracker_data.query.filter(tracker_data.tracker_ID == selected.ID, tracker_data.user_ID == uid).all()

        for log in tracker_logs:
            db.session.delete(log)
        
        db.session.commit()

        delete_tracker = tracker_table.query.filter(tracker_table.ID == selected.ID).first()
        db.session.delete(delete_tracker)
        db.session.commit()

    return redirect(url_for("main_page", uid=uid))
    
# create route to delete log
@app.route("/tracker/delete/<int:uid>/<int:tracker_id>/<int:s_no>", methods=["GET", "POST"])
def delete_log(uid,tracker_id,s_no):
    if request.method=="GET":
        selected_log = tracker_data.query.filter(tracker_data.s_no == s_no).one()
        db.session.delete(selected_log)
        db.session.commit()

        return redirect(url_for("main_page", uid=uid))

# create route to update log
@app.route("/tracker/update/<int:uid>/<int:tracker_id>/<int:s_no>", methods=["GET", "POST"])
def update_log(uid, tracker_id, s_no):
    if request.method == "GET":
        prev_log = tracker_data.query.filter(tracker_data.user_ID == uid, tracker_data.s_no == s_no).first()
        selected_log_timestamp = prev_log.timestamp
        selected_log_value = prev_log.value
        selected_log_notes = prev_log.notes
    
        # define list to append values to be updated
        for_update = []
        for_update.append(selected_log_timestamp)
        for_update.append(selected_log_value)
        for_update.append(selected_log_notes)
        for_update.append(tracker_id)
        for_update.append(s_no)

        print(for_update)
        session["for_update"] = for_update

        return redirect(url_for("main_page", uid=uid))
    
    if request.method == "POST":

        selected_log = tracker_data.query.filter(tracker_data.user_ID == uid, tracker_data.s_no == s_no).first()
        selected_log.timestamp = request.form["timestamp"]
        selected_log.value = request.form["value"]
        selected_log.notes = request.form["notes"]

        db.session.commit()

        session.pop("for_update", None)

        return redirect(url_for("main_page", uid=uid))


# create route for signup page
@app.route("/signup", methods=['GET', 'POST'])
def signup_page():
    print("signup page")
    if request.method == 'GET':
        return render_template("signup.html")
    
    if request.method == 'POST':
        if request.form:
            new_user_ID = request.form["username"]
            new_password = request.form["password"]

            new = new_user.query.filter_by(User_ID=new_user_ID).first()
            if new is None:
                new_user_data = new_user(User_ID=new_user_ID,
                                        password=new_password)
                
                db.session.add(new_user_data)
                db.session.commit()

                session["username"] = new_user_ID

                return redirect("/")
    
    return render_template("signup.html")

# create route to logout page
@app.route("/logout")
def logout_page():
    session.pop("username", None)
    return redirect("/")