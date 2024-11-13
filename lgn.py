from flask import Flask, render_template, Blueprint, request

lgn = Blueprint("lgn", __name__, template_folder="templates")

@lgn.route("/login", methods=["POST"])
def login():
    return render_template("login.html")


