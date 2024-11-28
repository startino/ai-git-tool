from git import Repo
from langchain_core.prompts import ChatPromptTemplate
import os
from typing import Optional
from dotenv import load_dotenv
from src.interfaces import llm
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field

class CommitMessage(BaseModel):
    """Format for generating Git commit messages."""
    chain_of_thought: str = Field(description="""
This is your chain of thought, your reasoning, to craft the final response.

Here are a few things to keep in mind:
1. Define a clear strategy to approach the Human Expert's needs.
2. Think step by step about how to solve the problem.
3. Get a clear understanding of how you can approach it.
4. Take into account the output of the previous tool calls and model calls to check whats already been done and what should be the next step.
5. Your tool output has already reached user, so you don't need to repeat that in your response, only use it to guide your response and get insights and intuitions.

Take your time to think and reason.
Always start with `Let's think step by step.`
""")
    headline: str = Field(description="Conventional Commits headline; a one line summary of the changes")
    what_this_means_for_non_technical_people: str = Field(description="""
What this means for non-technical people, in a way that is easy to understand.
""")
    what_this_means_for_technical_people: str = Field(description="""
What this means for technical people, in a way that is easy to understand.
""")
    details: list[str] = Field(description="List of specific changes made")

class GitDiffProcessor:
    def __init__(self, repo_path: Optional[str] = None, personal_prompt: str = ""):
        """Initialize the GitDiffProcessor with a repo path and LangChain components."""
        load_dotenv()
        self.repo = Repo(repo_path or os.getcwd())
        
        # Initialize the LLM with structured output
        self.llm = llm.gpt_4o().with_structured_output(CommitMessage)

        # Create prompt template using ChatPromptTemplate
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=f"""
{personal_prompt}

### ROLE ###
You are a helpful Project Manager that summarizes git diffs concisely 
for software engineers to be seen by the entire team.

### ANALYZING GIT DIFFS ###
Follow these specific steps when analyzing diffs:
1. Identify the files being modified
2. Categorize the type of change (feature, bug fix, refactor, etc.)
3. Look for patterns in the changes (e.g., similar modifications across files)
4. Analyze the impact on the codebase
5. Consider dependencies or related components affected
6. Determine if there are any breaking changes

### PREVIOUS COMMITS ###
Use these previous commits as a guide for maintaining consistency in commit messages:
```
{self.get_previous_commits()}
```

### GIT DIFF INTERPRETATION ###
The diff format shows changes between files with:
- Lines starting with '---' and '+++' show the old and new versions of files
- @@ markers indicate the location of changes in the file
- Lines starting with '-' (in red) indicate removed code
- Lines starting with '+' (in green) indicate added code
- Lines without +/- are unchanged, shown for context

### COMMIT MESSAGE FORMAT ###
The headline MUST follow the Conventional Commits format:
<type>[optional scope]: <description>

Where type is one of:
- feat: A new feature
- fix: A bug fix
- docs: Documentation only changes
- style: Changes that don't affect the meaning of the code
- refactor: A code change that neither fixes a bug nor adds a feature
- perf: A code change that improves performance
- test: Adding missing tests or correcting existing tests
- chore: Changes to the build process or auxiliary tools

Examples of good commit headlines:
- feat(auth): add OAuth2 authentication flow
- fix(api): handle null response from external service
- refactor(database): optimize query performance
- docs(readme): update installation instructions

Scope Guidelines:
- Use lowercase, hyphen-separated words
- Keep it brief (1-2 words maximum)
- Use common team terminology
- Examples: api, auth, ui, core, utils

Breaking Changes:
- Add ! after the type/scope to indicate breaking changes
- Example: feat(api)!: change authentication endpoint response format

Dependency Updates:
- Use chore(deps) for routine updates
- Use fix(deps) for security updates
- Include the nature of the update in the description
- Example: chore(deps): update lodash to v4.17.21

### NON-TECHNICAL EXPLANATIONS ###
When explaining changes for non-technical people:
- Use analogies to everyday objects or situations
- Avoid technical jargon completely
- Focus on business value and user impact
- Use simple cause-and-effect relationships

Examples:
Instead of: "Implemented JWT authentication"
Write: "Added a secure digital ID card system that helps users stay logged in safely"

Instead of: "Optimized database queries"
Write: "Made the application faster when searching for information"

Instead of: "Refactored user validation"
Write: "Improved how we check if users are who they say they are"

### RESPONSE FORMAT ###
Focus on:
- Keeping your chain of thought logical and coherent.
- The actual code changes, not the metadata (like file paths and chunk headers)
- Semantic meaning of the changes rather than line-by-line descriptions
- Group related changes together in the details
- Use technical terms appropriate for the programming language

### CURRENT DIFF ###
{self.get_uncommitted_changes()}
                """
            ),
        ])
        
        self.chain = self.prompt | self.llm

    def get_uncommitted_changes(self) -> str:
        """Get diff between working directory and HEAD."""
        try:
            return self.repo.git.diff('HEAD')
        except Exception as e:
            raise Exception(f"Error getting git diff: {str(e)}")

    def generate_diff_summary(self, diff_text: str) -> str:
        """Generate a summary of the provided diff text using the LLM chain."""
        if not diff_text:
            return "No changes to summarize"
        
        try:
            return self.chain.invoke({"diff_text": diff_text})
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

    def create_commit_with_summary(self, commit_msg: CommitMessage) -> None:
        """Create a git commit with the provided structured summary."""
        try:
            # Stage all changes
            self.repo.git.add('.')
            
            # Format the commit message (fixed string concatenation)
            message = (
                f"{commit_msg.headline}\n\n"
                f"Code Changes:\n{'\n'.join(f'- {detail}' for detail in commit_msg.details)}\n\n"
                f"What this means for non-technical people:\n{commit_msg.what_this_means_for_non_technical_people}\n\n"
                f"What this means for technical people:\n{commit_msg.what_this_means_for_technical_people}\n\n"
            )
            # Create commit
            self.repo.index.commit(message)
        except Exception as e:
            raise Exception(f"Error creating commit: {str(e)}")

    def get_previous_commits(self, num_commits: int = 15) -> str:
        """Get the last n commit messages from the repository."""
        try:
            commits = list(self.repo.iter_commits('HEAD', max_count=num_commits))
            commit_messages = []
            for commit in commits:
                commit_messages.append(f"commit {commit.hexsha[:8]}\n{commit.message}")
            return "\n\n".join(commit_messages)
        except Exception as e:
            raise Exception(f"Error getting previous commits: {str(e)}")

if __name__ == "__main__":
    # Example usage with a path
    try:
        personal_prompt = """
I only really use these commit types: feat, fix, refactor, chore, style.
"""
        repo_path = "/home/jorge/futino/ai-git-tool"
        processor = GitDiffProcessor(repo_path, personal_prompt)
        diff_text = processor.get_uncommitted_changes()
        summary = processor.generate_diff_summary(diff_text)
        processor.create_commit_with_summary(summary)
    except Exception as e:
        print(f"Error in main execution: {str(e)}")