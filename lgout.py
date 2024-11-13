from flask import Flask, render_template, Blueprint, request, session, redirect, url_for

lgout = Blueprint("lgout", __name__, template_folder="templates")

@lgout.route("/lgout", methods=["POST", "GET"])
def logout():
    if "user" in session:
        usr = session["user"]
    session.pop("user", None)
    import data
    data.records_list.clear()
    return redirect(url_for("homepg.home"))


