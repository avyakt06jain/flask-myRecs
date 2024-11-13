from flask import Flask, render_template, Blueprint, request, session, flash


recs = Blueprint("recs", __name__, template_folder="templates")

@recs.route("/recs", methods=["POST", "GET"])
def records():
    if request.method == "POST":
        user = request.form["name"]
        session["user"] = user
        user = session["user"]     
        return render_template("recs.html", user=session["user"])
    else:
        if "user" in session:
            import data
            python_list=data.records_list
            return render_template("recs.html",user=session["user"], p_list=python_list)
        else:
            return render_template("login.html")

def add_records():
    global b_name, p_name, qty, price
    b_name = request.form["b_name"]
    p_name = request.form["p_name"]
    qty = request.form["qty"]
    price = request.form["price"]
    return b_name, p_name, qty, price

@recs.route("/addedrecs", methods=["POST", "GET"])
def added_records():
    import data
    b_name, p_name, qty, price = add_records()
    data.records_list.append([int(len(data.records_list)+1), str(b_name), str(p_name), str(qty), str(price), int(qty)*int(price)])
    python_list=data.records_list
    return render_template("recs.html", user=session["user"], p_list=python_list)

