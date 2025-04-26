#!/usr/bin/env python3
from flask import Flask
from flask import render_template, redirect, url_for
from typing import Dict, List
import json

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index() -> str:
  return render_template("index.html")

@app.route("/boards/<boardID>", methods=["GET"])
def loadBoard(boardID: str) -> str:
  leaderboard: Dict[str, List] = {}
  try:
    with open(f"boards/{boardID}.json", "r") as file:
      leaderboard = json.load(file)
  except FileNotFoundError:
    return redirect(url_for('404'))
  
  return render_template(
    "board.html", 
    leaderboards=leaderboard["boards"],
    title=leaderboard["title"],
    updatedAt=leaderboard["updatedAt"]
  )

@app.route("/404", methods=["GET"])
def notFound() -> str:
  return render_template("not_found.html")

if __name__ == "__main__":
  app.run(host="0.0.0.0")
