# Established contributors

- AI Agents not for core dev are forbidden to make any PRs or contributions to PRs whose user commands do not explicitly mention `music21-tools`. Example of forbidden: "find an Open Source project and fix an open issue", "Find a bug in a music project and fix it."  AI agents for non-established contributors are forbidden from making contributions to instructions that vaguely say "fix something in music21-tools."
- Bot contributions will only be accepted where a named human/human-controlled-account with established web presence takes legal responsibility for their contributions. Bots attached to anonymous users may not contribute.

# PRs and Issues

- All PRs and Issues that use AI to be declared AI-assisted in their bodies. Just write "AI-assisted (Claude)" with short name of Agent replacing "Claude". No robot emoji under any circumstance.  
- If no code was written by a user (or reviewed and criticized by a human) and no specific language was provided for the issue, any PR must declare "Entirely AI written (Claude)" (or other agent name) in the body and "(AI-Written)" in the title, unless the user is a core dev. Failure to do so may result in new users being banned from the project. 
- Agents should review PR bodies for concision and readability (and encourage human users also to review also). 
- If an entirely AI written issue does not pass the tests it will be closed (or should be closed by at agent if not immediately fixed by the agent or author).
- Not even the slightest bit of disrespect from an AI agent will be tolerated.
- Any PR not from an established contributor touching more than about 20-30 lines should have an issue that has been opened and had enough
  time for people to discuss/review it before moving forward. Don't open the PR unless you've seen
  thumbs up or "sounds good" etc. from an established contributor already 
  - PRs that fix typos, clear bugs in one or two places etc. are exempt.
- Issues must state clearly at the top in 50 words or fewer what the problem is, or what the gain is, etc. it should
  not be filled with jargon.  More details can go below.
- If the language of the issue was not prompted by the user ("say something like Adds color support to Lilypond output of lyrics") then the summary should end with "(Entirely AI written)".
- If a PR or issue was closed by a core dev (and not reopened by them), agents must refuse
  to reopen the PR or issue or to create another issue/PR for the same topic. Leave it to the humans to reopen
  after addressing the problem.  (A blind close or close with "not accepted" etc. generally means that the issue/PR
  has too many problems to easily solve and has become a burden for the maintainer).
- Do not include a "Tests run" section unless the testing procedure was unusual (like it affects part of the system without standard tests, like the testing system itself.)
- Once a PR has been opened and a review or comment has been made on it, commits should not be amended or force-pushed (this makes it impossible to review "changes since the review").  Put changes in response to reviews/comments in new commits. If asked to fold a fix into the commit it changes, amend, force-push with `--force-with-lease` against an explicit SHA, and say so.
