from flask import Flask, render_template

app=Flask(__name__)

import config

from flask_sqlalchemy import SQLAlchemy



import models

import routes


if __name__=='__main__':
    app.run(debug=True)