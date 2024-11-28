# ai-git-tool

This is an AI Agent that can generate commit messages for git.
It is intented to be used as a git alias, and it is able to generate a commit message based on the changes in the current git index.

The Agent is built using LangChain, and it is able to use any LLM that is supported by LangChain.

Currently, the Agent's prompt is composed of:
- The git diff in the current index
- The commit messages of the last X commits
- A personal prompt that can be customized by the user to add any additional knowledge
- A base prompt that contains the rules for generating the commit message
We plan to add more sources of knowledge in the future, such as:
- The project's README file
- An LLM-friendly overview of the codebase

We also plan to integrate [Critino](https://github.com/startino/critino) in the future to allow 
users to more easily provide feedback to the Agent.
