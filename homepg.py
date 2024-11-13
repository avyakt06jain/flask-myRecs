from flask import Flask, render_template, Blueprint, request

homepg = Blueprint("homepg", __name__, template_folder="templates")

@homepg.route("/", methods=["POST", "GET"])
@homepg.route("/home", methods=["POST", "GET"])
def home():
    return render_template("homepg.html")



