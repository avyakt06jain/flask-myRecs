from flask import Flask, redirect, url_for, request, flash, Blueprint, render_template, flash
from homepg import homepg
from lgn import lgn     
from recs import recs
from lgout import lgout
from addingrecs import addingrecs

app = Flask(__name__)
app.register_blueprint(homepg)
app.register_blueprint(lgn)
app.register_blueprint(recs)
app.register_blueprint(lgout)
app.register_blueprint(addingrecs)
app.secret_key="qwerty"

if __name__ == "__main__":
    app.run(debug=True)