#!/usr/bin/env python3
from typing import List, Dict
import json
from datetime import datetime

# This is sooooo poorly written with this dumb structure but oh well
def generateLeaderboards(teams: List[Dict]) -> None:
  date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

  # Empty leaderboard structures
  projects_per_campus: Dict[str, List] = {
    "title": "Largest Project per Campus",
    "boards": [
      {
        "title": "Burnaby Campus",
        "headers": [
          "Rank",
          "Team",
          "Size",
          "Commits"
        ],
        "entries": []
      },
      {
        "title": "Downtown Campus",
        "headers": [
          "Rank",
          "Team",
          "Size",
          "Commits"
        ],
        "entries": []
      }  
    ],
    "updatedAt": date
  }
  projects_all_time: Dict[str, List] = {
    "title": "Largets Project of All",
    "boards": [
      {
        "title": "",
        "headers": [
          "Rank",
          "Team",
          "Size",
          "Commits"
        ],
        "entries": []
      }
    ],
    "updatedAt": date
  }
  contributors_per_campus: Dict[str, List] = {
    "title": "Top Contributor per Campus",
    "boards": [
      {
        "title": "Burnaby Campus",
        "headers": [
          "Rank",
          "Author",
          "Added",
          "Deleted",
          "Actual",
          "Commits"
        ],
        "entries": []
      },
      {
        "title": "Downtown Campus",
        "headers": [
          "Rank",
          "Author",
          "Added",
          "Deleted",
          "Actual",
          "Commits"
        ],
        "entries": []
      }
    ],
    "updatedAt": date
  }
  contributors_per_project: Dict[str, List] = {
    "title": "Top Contributor per Project",
    "boards": [], # Generated later
    "updatedAt": date
  }
  tracked_teams: int = 0
  teams_in_project: Dict[str, int] = {} # keep track of teams added to contributors_per_project
  contributors_all_time: Dict[str, List] = {
    "title": "Top Contributor of All",
    "boards": [
      {
        "title": "",
        "headers": [
          "Rank",
          "Author",
          "Added",
          "Deleted",
          "Actual",
          "Commits"
        ],
        "entries": []
      }
    ],
    "updatedAt": date
  }

  # === Populate leaderboards === #
  for team in teams:
    added, deleted, commits = 0, 0, 0
    for author in team["contributors"]:
      added   += author["added"]
      deleted += author["deleted"]
      commits += author["commits"]

      author["actual"] = author["added"] - author["deleted"]

      authorEntry: List[any] = [
        None, author["author"], author["added"], author["deleted"], author["actual"], author["commits"]
      ]

      campus: int = 0 if "BBY" in team["team"] else 1
      contributors_per_campus["boards"][campus]["entries"].append(authorEntry)
      
      if team["team"] not in teams_in_project:
        teams_in_project[team["team"]] = tracked_teams
        tracked_teams += 1
        contributors_per_project["boards"].append({
          "title": team["team"],
          "headers": [
            "Rank",
            "Author",
            "Added",
            "Deleted",
            "Actual",
            "Commits"
          ],
          "entries": []
        })

      contributors_per_project["boards"][teams_in_project[team["team"]]]["entries"].append(authorEntry)

      contributors_all_time["boards"][0]["entries"].append(authorEntry)

    size = added - deleted

    projectEntry: List[str|int] = [
      None,
      team["team"],
      size,
      commits
    ]
    
    campus: int = 0 if "BBY" in team["team"] else 1
    projects_per_campus["boards"][campus]["entries"].append(projectEntry)
    projects_all_time["boards"][0]["entries"].append(projectEntry)


    # === Sort leaderboards and write to JSON === #

    # Project per Campus
    for campus in range(len(projects_per_campus["boards"])):
      filtered = sorted(projects_per_campus["boards"][campus]["entries"], key=lambda e: e[2], reverse=True)
      for i in range(len(filtered)):
        filtered[i][0] = i + 1

      projects_per_campus["boards"][campus]["entries"] = filtered

    with open("boards/LargestProjectsPerCampus.json", "w") as file:
      json.dump(projects_per_campus, file, indent=2)

    # Projects all time
    filtered = sorted(projects_all_time["boards"][0]["entries"], key=lambda e: e[2], reverse=True)
    for i in range(len(filtered)):
      filtered[i][0] = i + 1

    projects_all_time["boards"][0]["entries"] = filtered

    with open("boards/LargestProjectAllTeams.json", "w") as file:
      json.dump(projects_all_time, file, indent=2)

    # Contributor per Campus
    for campus in range(len(contributors_per_campus["boards"])):
      filtered = sorted(contributors_per_campus["boards"][campus]["entries"], key=lambda e: e[2], reverse=True)
      for i in range(len(filtered)):
        filtered[i][0] = i + 1
    
      contributors_per_campus["boards"][campus]["entries"] = filtered

    with open("boards/TopContributorPerCampus.json", "w") as file:
      json.dump(contributors_per_campus, file, indent=2)

    # Contributor per Project
    for project in range(len(contributors_per_project["boards"])):
      filtered = sorted(contributors_per_project["boards"][project]["entries"], key=lambda e: e[2], reverse=True)
      for i in range(len(filtered)):
        filtered[i][0] = i + 1

      contributors_per_project["boards"][project]["entries"] = filtered

    with open("boards/TopContributorsPerTeam.json", "w") as file:
      json.dump(contributors_per_project, file, indent=2)

    # Contributor all time
    filtered = sorted(contributors_all_time["boards"][0]["entries"], key=lambda e: e[2], reverse=True)
    for i in range(len(filtered)):
      filtered[i][0] = i + 1

    contributors_all_time["boards"][0]["entries"] = filtered

    with open("boards/TopContributorsAllTime.json", "w") as file:
      json.dump(contributors_all_time, file, indent=2)

def main() -> None:
  with open("teams.json", "r") as file:
    teams: List[Dict] = json.load(file)

  generateLeaderboards(teams)

if __name__ == "__main__":
  main()
