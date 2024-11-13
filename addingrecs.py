from flask import Flask, render_template, Blueprint, request, session, flash

addingrecs = Blueprint("addingrecs", __name__, template_folder="templates")

@addingrecs.route("/addingrecs", methods=["POST", "GET"])
def add_records():
    return render_template("addingrecs.html")


