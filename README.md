# ai-git-tool

An AI-powered tool that automatically generates meaningful commit messages by analyzing your git changes.

## Overview

This tool serves as a git alias that leverages AI to generate contextual commit messages based on the changes in your git index. Built with LangChain, it supports various Large Language Models (LLMs) to provide flexible integration options.

## Features

### Current Capabilities
- Generates commit messages by analyzing:
  - Git diff from the current index
  - Historical context from recent commits
  - User-customizable personal prompts
  - Base prompt with commit message generation rules

### Roadmap
- [ ] Integration with project documentation
  - README file analysis
  - LLM-friendly codebase overview
  - Project's communication resources like Discord/Slack, read.ai, etc.
- [ ] [Critino](https://github.com/startino/critino) integration for user feedback
  
## Installation

1. Clone the repository
2. Install the dependencies from the pyproject.toml file
3. Run the tool with `python src/lib/git_diff_processor.py <repository_name>`

## Usage

Run `python src/lib/git_diff_processor.py <repository_name>`

## How It Works

The tool constructs intelligent commit messages by combining multiple sources of context:
1. Current changes (git diff)
2. Historical context (previous commits)
3. User-defined knowledge (customizable prompts)
4. Base rules for commit message generation
