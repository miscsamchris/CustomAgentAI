import os
from flask import Flask, render_template, redirect, url_for, send_from_directory,request, jsonify
from flask_sqlalchemy import SQLAlchemy
import openai
direc = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    direc, "data.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
db = SQLAlchemy(app)
app.app_context().push()
openai.api_key = "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"
