#!/usr/bin/env python3
from insights import setupDir, main
from leaderboard import generateLeaderboards
import asyncio
import json
from typing import List, Dict

if __name__ == "__main__":
  setupDir("repos")
  setupDir("boards")
  asyncio.run(main())

  with open("teams.json", "r") as file:
    teams: List[Dict] = json.load(file)

  generateLeaderboards(teams)
