#!/usr/bin/env python3
from typing import List, Dict
from json import JSONDecodeError
import json
import asyncio
import os
import subprocess
import shutil

IGNORED: List[str] = [
  "node_modules/",
  ".min.",
  ".png",
  ".jpg",
  ".jpeg",
  ".webp",
  ".ico",
  ".svg",
  ".mp3",
  ".mp4",
  "bootstrap/",
  ".history/",
  "package-lock.json",
  "/@",
  "yarn.lock",
  ".lock",
  ".yml",
  "eslint-plugin",
  ".yy", 
  "lowercased-schools.json", # DTC-07 10k+ list of schools
  "schools.json",
  "school.json",
  "cleaned-schools.json",
  "Ladder2800.js", # BBY06 - Auto generated code detected. please dont rename this file at all.
  ".geojson", # Group has thousands of data points in a .geojson file
  "...", # It is possible someone has so many sub folders and such a long file name it gets ignored
]        # git log --stat kinda sucks that it doesnt always show the full folder path

urls: Dict[str, str] = {}
with open("urls.json", "r") as file:
  urls = json.load(file)

def setupDir(directory: str) -> None:
  folder = f'./{directory}'
  if not os.path.exists(folder):
    os.makedirs(folder) 

  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
    except Exception as e:
      print('Failed to delete %s. Reason: %s' % (file_path, e))


async def getInsights(repoURL: str, teamID: str) -> Dict[str, str|List]:
  repo: str = repoURL.split("/")[4].split(".git")[0]

  execDir: str = f"{os.getcwd()}/repos"
  repoDir: str = f"{execDir}/{repo}"

  clear: List[str] = ["rm", "-rf", repo]
  clone: List[str] = ["git", "clone", repoURL] 
  audit: List[str] = ["git", "log", "--stat"]

  subprocess.run(clear, cwd=execDir)
  subprocess.run(clone, cwd=execDir)

  with open(f"{repoDir}/audit.txt", "w") as auditFile:
    subprocess.run(audit, cwd=repoDir, stdout=auditFile, text=True)

  team: Dict[str, str|List] = {
    "team": teamID,
    "contributors": []
  }

  with open(f"{repoDir}/audit.txt", "r") as auditFile:
    lines = auditFile.readlines()

    authorStats: Dict[str, str|int] | None = None

    for i in range(len(lines)):
      line: str = lines[i].replace("\n", "")
      if "Author: " in line:
        author = line.split("Author: ")[1].split(" <")[0]
        email = line.split("<")[1].split(">")[0].lower()

        found: bool = False
        for authorStat in team["contributors"]:
          if found: break
          if authorStat["author"] == author or authorStat["email"] == email:
            authorStats = authorStat
            team["contributors"].remove(authorStat)
            found = True

        if not found and "@users.noreply.github.com" in email: continue

        if not found:
          authorStats = {
            "email": email,
            "author": author,
            "commits": 0,
            "added": 0,
            "deleted": 0
          }

        if "Merge: " in lines[i - 1]:
          authorStats["commits"] += 1
          team["contributors"].append(authorStats)
          continue

        offset: int = i + 5
        done: bool = False

        while not done:
          if "files changed," in lines[offset] or "file changed," in lines[offset]:
            done = True
            break

          ignore: bool = False
          for IGNORE in IGNORED:
            if IGNORE in lines[offset]:
              ignore = True
              break

          if ignore:
            offset += 1
            continue

          if " | " not in lines[offset]:
            offset += 1
            continue

          if " Bin " in lines[offset] and " bytes" in lines[offset] and " -> " in lines[offset]:
            offset += 1
            continue

          fileDiffNum: int = 0
          try:
            fileDiffNum = int(list(filter(None, lines[offset].split("|")[1].split(" ")))[0])
          except ValueError:
            offset += 1
            continue

          if fileDiffNum == 0:
            offset += 1
            continue

          ratioString: str = list(filter(None, lines[offset].split("|")[1].split(" ")))[1].replace("\n", "")

          numAdd: int = ratioString.count("+")
          numDel: int = ratioString.count("-")

          added:   int = round((numAdd / len(ratioString)) * fileDiffNum)
          deleted: int = round((numDel / len(ratioString)) * fileDiffNum)

          authorStats["added"] += added
          authorStats["deleted"] += deleted

          offset += 1

        authorStats["commits"] += 1
        team["contributors"].append(authorStats)

  return team

async def main() -> None:
  teamsOrigin: List[Dict] = []
  try:
    with open("teams.json", "r") as file:
      teamsOrigin = json.load(file)
  except (FileNotFoundError, JSONDecodeError):
    pass
  
  teams: List[Dict] = []

  for teamID in urls:
    if urls[teamID] == "": continue
    team: Dict[str, str|List] | None = None
    try:
      team = await getInsights(urls[teamID], teamID)
    except Exception:
      pass
    if team is not None:
      teams.append(team)

  print(f"Completed {len(teams)}/{len(urls)}")

  # If failed to get new team data, populate with old team data
  for original in teamsOrigin:
    originalID = original["team"]
    exists: bool = False
    for team in teams:
      if team["team"] == originalID:
        exists = True
        break
    
    if not exists:
      teams.append(original)

  with open("teams.json", "w") as file:
    json.dump(teams, file, indent=2)

if __name__ == "__main__":
  setupDir("repos")
  setupDir("boards")
  asyncio.run(main())
