#!/usr/bin/env python3
from links import urls
from typing import List, Dict
import json
import asyncio
import aiohttp
import time
from tqdm import tqdm

from parse import parse
from key import token

MAX_RETRY: int = 5

async def getInsights(repoURL: str, attempt: int = 0) -> Dict[str, str|None] | None:
  owner: str = repoURL.split("/")[3]
  repo: str = repoURL.split("/")[4]

  query: str = f"https://api.github.com/repos/{owner}/{repo}/stats/contributors"
  headers: Dict[str, str] = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}",
    "X-GitHub-Api-Version": "2022-11-28" 
  }

  async with aiohttp.ClientSession() as session:
    async with session.get(query, headers=headers, timeout=5) as resp:
      if resp.status > 400:
        return None
      if resp.status == 202 and attempt <= MAX_RETRY:
        time.sleep(15)
        attempt += 1
        team = await getInsights(repoURL, attempt)
        return team
      elif attempt > MAX_RETRY: return None

      team: Dict[str, str|List] = {
        "repo": repoURL,
        "team": repo,
        "contributors": []
      }
      
      data: List[Dict[str, any]] = await resp.json()

      for contributor in data:
        newContributor: Dict[str, str|int] = {
          "author": contributor["author"]["login"],
          "commits": contributor["total"],
          "added": 0,
          "deleted": 0
        }

        for week in contributor["weeks"]:
          newContributor["added"] += week["a"]
          newContributor["deleted"] += week["d"]

        team["contributors"].append(newContributor)

  return team

async def main() -> None:
  teamsOriginal: List[Dict] = []
  try:
    with open("teams.json", "r") as file:
      teamsOriginal = json.load(file)
  except FileNotFoundError:
    pass

  teams: List[Dict] = []

  for i in tqdm(range(len(urls)),
                desc="Reading Insights",
                ascii=False, ncols=75):
    url = urls[i]
    team: Dict[str, str|List] = await getInsights(url)
    if team is not None:
      teams.append(team)
    time.sleep(5)

  print(f"Completed {len(teams)}/{len(urls)}")

  # Parse gets Campus, Set, and Team ID
  teams = parse(teams)

  for originalTeam in teamsOriginal:
    originalTeamID = originalTeam["id"]
    exists: bool = False
    for team in teams:
      if team["id"] == originalTeamID:
        exists = True
        break

    if not exists:
      teams.append(originalTeam)

  with open("teams.json", "w") as file:
    json.dump(teams, file, indent=2)

if __name__ == "__main__":
  asyncio.run(main())