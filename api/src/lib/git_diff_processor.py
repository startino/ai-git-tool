from git import Actor, Repo
from langchain_core.prompts import ChatPromptTemplate
import os
from typing import Optional
from dotenv import load_dotenv
from src.interfaces import llm
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from pathlib import Path

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

        # Read prompt template from markdown file
        prompt_path = Path(__file__).parent.parent / "prompts" / "git_diff_processor.md"
        with open(prompt_path, "r") as f:
            prompt_template = f.read()

        # Create prompt template using ChatPromptTemplate
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=f"""
{personal_prompt}

{prompt_template}

### PREVIOUS COMMITS ###
```
{self.get_previous_commits()}
```

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

    def generate_commit_message(self, diff_text: str) -> CommitMessage | None:
        """Generate a summary of the provided diff text using the LLM chain."""
        if not diff_text:
            return None
        
        try:
            result = self.chain.invoke({})

            if isinstance(result, CommitMessage):
                return result
            else:
                raise Exception(f"LLM returned invalid response: {result}")
        except Exception as e:
            raise Exception(f"Error generating commit message: {str(e)}")

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
            self.repo.index.commit(
                author=Actor(name="antopiahk", email="antopiahk@gmail.com"),
                message=message
            )
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

    personal_prompt = """
I only really use these commit types: feat, fix, refactor, chore, style.
"""
    repo_path = "/home/jorge/futino/ai-git-tool"
    processor = GitDiffProcessor(repo_path, personal_prompt)
    diff_text = processor.get_uncommitted_changes()
    commit_message = processor.generate_commit_message(diff_text)
    if commit_message:
        processor.create_commit_with_summary(commit_message)
