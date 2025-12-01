## Overview
The application itself is an agentic pipeline that utilizes the following strategy:
- Firstly, an architect agent will use a user's prompt to plan a task, decide how many and what agents to use, and define a success criteria / tests.
- Then the planned agents are built and executed. Each agent builds its own part of an application with its own files assigned. Agents communicate with each other, sharing the functions, classes, methods, etc from their respective files.
- After an agent finished, their code is being reviewed and if something is wrong - it retries.
- At the end, the application specific unit tests are executed. We haven't implemented retries if the unit tests fail, but it will inform us what works as expected and what needs improvements.

## How to run it
Go to our repository (main branch), open the `backend/` folder, install dependencies (you can use `pyproject.toml` or pipreqs to do so), then run `python test_cli.py --help` for possible ways of execution. The frontend is now only integrated with an older version of our agentic pipeline (which is more "static") in dev branch, so better use cli.

## Current state of the project and future steps
- The project is completely functional and usable.
- The frontend integration is only done for an older backend version in dev.
- The codebase needs refactoring (removing old ver. parts of the code, deleting redundant files, structure improvements).