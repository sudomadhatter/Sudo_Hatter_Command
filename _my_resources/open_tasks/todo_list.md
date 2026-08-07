# Todo List
<!-- Daniel's personal task notes for all projects. READ-ONLY for agents. Unless asked to update this file by me. -->

1. check that the python is all set up correctly accross all machines

## Sub-Projects Todo Lists
<!-- Read /open_tasks/todo_list.md for a quick view of what is going on in the sub projects listed below. -->
These are folder paths to see the open todo list in the sub projects: 
1. C:\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT\_my_resources\open_tasks\todo_list.md
2. C:\Sudo_Hatter_Command\Projects\OpenChat-Openrouter\_my_resources\open_tasks\todo_list.md

----

## New Tasks
<!-- Always cross-check against the live project files before trusting anything here. -->

1. Verify the new workflows for running python and vytests. We uptimized this for its solo lane, but with the new Mac we may be able to handle more. These documents are stored in the migrations folder, the new_machine references the python_vytest doc that will limit it to linear testing.
2. git-hooks-board-stale guide to set up the triggers for updating the scrum board, to move tickets to stale.
3. No more running on main_debug we have to do this the right way and do small branches and then merge them back to main no more main_debug, we need to fix this merge it to main and then continue the correct way.
4. Update Aviationchat ADK to 2.5 for both front and back end
5. Updates for the project Aviationchat and new standards
    -  Jira integration for tickets with hooks that block pushing with out updateing the tickets. We will use this instead of the sprint board we are doing now. 
    - add schema to user ids, get details from chat with gary
    - seperate the front and back end. if possible also seperate out the bmad and the other stuff from git and see if we can optimize the command center to handle all that stuff when it comes to work flows rules and commands.
    - set up database to share secrets the secure way
7. While updating the command center to handle all workflow related things, also apply the graph rag style for the workflows, have the /write-storys-epics decide here if its a quick dev or full dev. optimize the quick dev, if not there it can be when we write the storys, if its quick dev it prompts you down this path. 
    - Use this time to also impliment the Openwork Skill https://github.com/andrewyng/openworker
8. set up a master .env in sudo hatter command for my main computer


## Open Work
<!-- Add plan/PRP notes as <slug>.md alongside this file. -->
1. Live Testing
2. New Epic 18 for updating to google ADK 2.0
    - make sure to do this on its own branch this is a high risk change that could break our production system
3. /mobile-error_team still needs to be pushed to main to work, there is a note in claude memory about it, just ask. 

<!-- open_tasks files — auto-listed by /update-maps-indexes -->
- `plan_optimize-sudo-dev-story-tests.md`

----

<!-- CHECKPOINT id="ckpt_mrk3jkm0_qa7nw6" time="2026-07-14T03:33:28.728Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->

<!-- CHECKPOINT id="ckpt_mrx0p3jt_d0a9cj" time="2026-07-23T04:34:47.993Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->


