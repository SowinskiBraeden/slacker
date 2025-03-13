#!/usr/bin/env python3
from typing import List, Dict
import json
from prettytable import PrettyTable
import os, shutil
from datetime import datetime

def pretty_table(dct: Dict, title: str, add: str=""):
  table = PrettyTable()
  for c in dct.keys():
     table.add_column(c, [])
  table.add_row(['\n'.join(dct[c]) for c in dct.keys()])
  table.align = "l"
  with open(f"./boards/{title}.txt", "a") as file:
    if add != "":
      file.write(f"{add}\n")
    file.write(table.__str__())
    file.write("\n\n")

  # with open(f"./boards/{title}", "ab") as file:
  #   pickle.dump(dct, file)

def setupDir() -> None:
  if not os.path.exists("./boards"): 
    os.makedirs("./boards") 

  folder = './boards'
  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
    except Exception as e:
      print('Failed to delete %s. Reason: %s' % (file_path, e))

def main() -> None:
  date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

  teams: List[Dict[str, str|List]] = {}
  with open("teams.json", "r") as file:
    teams = json.load(file)

  projects_per_campus = {
    "Burnaby": [],
    "Downtown": []
  }
  projects_per_set = {
    "A": [],
    "B": [],
    "C": [],
    "D": [],
    "E": [],
    "F": []
  }
  projects_all_time = []
  contributors_per_campus = {
    "Burnaby": [],
    "Downtown": []
  }
  contributors_per_set = {
    "A": [],
    "B": [],
    "C": [],
    "D": [],
    "E": [],
    "F": []
  }
  contributors_per_project = {}
  contributors_all_time = []
  for team in teams:
    added, deleted, commits = 0, 0, 0
    for author in team["contributors"]:
      added += author["added"]
      deleted += author["deleted"]
      commits += author["commits"]

      author["contributed"] = author["added"] - author["deleted"]
      
      contributors_per_campus[team["campus"]].append(author)
      contributors_per_set[team["set"]].append(author)

      if team["id"] not in contributors_per_project:
        contributors_per_project[team["id"]] = []
      contributors_per_project[team["id"]].append(author)

      contributors_all_time.append(author)

    size = added - deleted

    project = {
      "team": team["id"],
      "size": size,
      "added": added,
      "deleted": deleted,
      "commits": commits
    }

    projects_per_campus[team["campus"]].append(project)
    projects_per_set[team["set"]].append(project)
    projects_all_time.append(project)

  #######################################################################

  # Largest project per campus
  for campus in projects_per_campus:        
    filtered = sorted(projects_per_campus[campus], key=lambda d: d['size'], reverse=True)
    
    data = {
      "Rank": [],
      "Team": [],
      "Size": []
    }

    rank = 0
    for project in filtered:
      rank += 1
      data["Rank"].append(str(rank))
      data["Team"].append(project["team"])
      data["Size"].append(str(project["size"]))

    pretty_table(data, "LargestProjectsPerCampus", f"{campus} Campus - Updated at {date}")

  # Largest project per set
  for set in projects_per_set:
    filtered = sorted(projects_per_set[set], key=lambda d: d['size'], reverse=True)
    
    data = {
      "Rank": [],
      "Team": [],
      "Size": []
    }

    rank = 0
    for project in filtered:
      rank += 1
      data["Rank"].append(str(rank))
      data["Team"].append(project["team"])
      data["Size"].append(str(project["size"]))

    pretty_table(data, "LargestProjectPerSet", f"Set {set} - Updated at {date}")

  # Largest project of all
  filtered = sorted(projects_all_time, key=lambda d: d['size'], reverse=True)
  
  data = {
    "Rank": [],
    "Team": [],
    "Size": []
  }

  rank = 0
  for project in filtered:
    rank += 1
    data["Rank"].append(str(rank))
    data["Team"].append(project["team"])
    data["Size"].append(str(project["size"]))

  pretty_table(data, "LargestProjectAllTeams", f"Updated at {date}")


  # Contributors ranker per campus
  for campus in contributors_per_campus:
    filtered = sorted(contributors_per_campus[campus], key=lambda d: d['added'], reverse=True)
    
    data = {
      "Rank": [],
      "Author": [],
      "Added": [],
      "Deleted": [],
      "Actual": [],
      "Commits": [],
    }

    rank = 0
    for author in filtered:
      rank += 1
      data["Rank"].append(str(rank))
      data["Author"].append(author['author'])
      data["Commits"].append(str(author['commits']))
      data["Added"].append(f"+{author['added']}")
      data["Deleted"].append(f"-{author['deleted']}")
      data["Actual"].append(str(author['contributed']))

    pretty_table(data, "TopContributorPerCampus", f"{campus} Campus - Updated at {date}")


  # Contributors ranked per set
  for set in contributors_per_set:
    filtered = sorted(contributors_per_set[set], key=lambda d: d['added'], reverse=True)
    
    data = {
      "Rank": [],
      "Author": [],
      "Added": [],
      "Deleted": [],
      "Actual": [],
      "Commits": [],
    }

    rank = 0
    for author in filtered:
      rank += 1
      data["Rank"].append(str(rank))
      data["Author"].append(author['author'])
      data["Commits"].append(str(author['commits']))
      data["Added"].append(f"+{author['added']}")
      data["Deleted"].append(f"-{author['deleted']}")
      data["Actual"].append(str(author['contributed']))

    pretty_table(data, "TopContributorPerSet", f"Set {set} - Updated at {date}")


  # Contributors ranked per Team
  for project in contributors_per_project:
    filtered = sorted(contributors_per_project[project], key=lambda d: d['added'], reverse=True)

    data = {
      "Rank": [],
      "Author": [],
      "Added": [],
      "Deleted": [],
      "Actual": [],
      "Commits": [],
    }

    rank = 0
    for author in filtered:
      rank += 1
      data["Rank"].append(str(rank))
      data["Author"].append(author['author'])
      data["Commits"].append(str(author['commits']))
      data["Added"].append(f"+{author['added']}")
      data["Deleted"].append(f"-{author['deleted']}")
      data["Actual"].append(str(author['contributed']))

    pretty_table(data, "TopContributorsPerTeam", f"{project} - Updated at {date}");

  # Contributors ranked all time
  contributors_all_time = sorted(contributors_all_time, key=lambda d: d['added'], reverse=True)
  
  data = {
    "Rank": [],
    "Author": [],
    "Added": [],
    "Deleted": [],
    "Actual": [],
    "Commits": [],
  }
  
  rank = 0
  for author in contributors_all_time:
    rank += 1
    data["Rank"].append(str(rank))
    data["Author"].append(author['author'])
    data["Actual"].append(str(author["contributed"]))
    data["Added"].append(f"+{author['added']}")
    data["Deleted"].append(f"-{author['deleted']}")
    data["Commits"].append(str(author['commits']))

  pretty_table(data, "TopContributorsAllTime", f"Updated at {date}")

if __name__ == "__main__":
  setupDir()
  main()
