#!/usr/bin/env python3
from flask import Flask, Response
from flask import render_template
import os

app = Flask(__name__)

def root_dir():
  return os.path.abspath(os.path.dirname(__file__))

def get_file(filename):
  try:
      src = os.path.join(root_dir(), filename)
      return open(src).read()
  except IOError as exc:
      return str(exc)

@app.route("/", methods=["GET"])
def index() -> str:
  return render_template("index.html")

@app.route("/boards/<boardID>", methods=["GET"])
def loadBoard(boardID: str) -> str:
  path = os.path.join(root_dir(), f"boards/{boardID}.txt")
  return Response(get_file(path), mimetype="text/plain")

if __name__ == "__main__":
  app.run(host="0.0.0.0")
