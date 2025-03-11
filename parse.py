#!/usr/bin/env python3
from typing import List, Dict
import json

def getSet(team: str) -> str:
  team = team.upper()
  campus = "DTC" if "DTC" in team else "BBY"
  num = ""
  if "BBY" in team:
    num = team.split("BBY")[1]
  elif "DTC" in team:
    num = team.split("DTC")[1]
  elif "TEAM" in team:
    num =  team.split("TEAM")[1]
  elif "GROUP" in team:
    num = team.split("GROUP")[1]
  else:
    num = team

  num = int(num)  
  if campus == "BBY":
    if 17 <= num <= 24: return "A"
    if 1 <= num <= 8: return "B"
    if 9 <= num <= 16: return "C"
    if 25 <= num <= 32: return "D"
    else:
      print(team, num)
      return "X"
  elif campus == "DTC":
    if 1 <= num <= 8: return "E"
    if 9 <= num <= 15: return "F"
    else:
      print(team)
      return "X"
  else:
    print(team)
    return "Z"
  
def getCampus(team: str) -> str:
  team = team.upper()
  campus = "Downtown" if "DTC" in team else "Burnaby"
  return campus

def createTeamID(team: str) -> str:
  team = team.upper()
  campus = "DTC" if "DTC" in team else "BBY"
  num = ""
  if "BBY" in team:
    num = team.split("BBY")[1]
  elif "DTC" in team:
    num = team.split("DTC")[1]
  elif "TEAM" in team:
    num =  team.split("TEAM")[1]
  elif "GROUP" in team:
    num = team.split("GROUP")[1]
  else:
    num = team

  num = int(num)
  return f"{campus}-{'0' if num < 10 else ''}{num}"

def parse(teams: List[Dict[str, str|List]]) -> List[Dict[str, str|List]]:

  for team in teams:
    teamID = team["repo"].split("_")[len(team["repo"].split("_")) - 1]
    team["set"] = getSet(teamID)
    team["campus"] = getCampus(teamID)
    team["id"] = createTeamID(teamID)

  return teams
  # with open("teams.json", "w") as file:
  #   json.dump(teams, file, indent=2)

if __name__ == "__main__":
  parse()
