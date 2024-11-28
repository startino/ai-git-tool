from git import Repo
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from typing import Optional
from dotenv import load_dotenv
from src.interfaces import llm
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

class CommitMessage(BaseModel):
    """Format for generating Git commit messages."""
    headline: str = Field(description="Brief one-line summary of the changes")
    details: list[str] = Field(description="List of specific changes made")

class GitDiffProcessor:
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize the GitDiffProcessor with a repo path and LangChain components."""
        load_dotenv()
        self.repo = Repo(repo_path or os.getcwd())
        
        # Initialize the LLM with structured output
        self.llm = llm.gpt_4o().with_structured_output(CommitMessage)
        
        # Create prompt template using ChatPromptTemplate
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content="""
### ROLE ###
You are a helpful Project Manager that summarizes git diffs concisely 
for software engineers to be seen by the entire team.

### GIT DIFF INTERPRETATION ###
The diff format shows changes between files with:
- Lines starting with '---' and '+++' show the old and new versions of files
- @@ markers indicate the location of changes in the file
- Lines starting with '-' (in red) indicate removed code
- Lines starting with '+' (in green) indicate added code
- Lines without +/- are unchanged, shown for context

### RESPONSE FORMAT ###
Generate a commit message with:
1. A clear summary line describing the main change
2. A list of specific changes made

Focus on:
- The actual code changes, not the metadata (like file paths and chunk headers)
- Semantic meaning of the changes rather than line-by-line descriptions
- Group related changes together in the details
- Use technical terms appropriate for the programming language

### CURRENT DIFF ###
{diff_text}
                """
            ),
        ])
        
        # Create the LCEL chain
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
            
            # Format the commit message
            message = f"{commit_msg.headline}\n\n" + "\n".join(f"- {detail}" for detail in commit_msg.details)
            
            # Create commit
            self.repo.index.commit(message)
        except Exception as e:
            raise Exception(f"Error creating commit: {str(e)}")


if __name__ == "__main__":
    # Example usage with a path
    try:
        repo_path = "/home/jorge/futino/ai-git-tool"
        processor = GitDiffProcessor(repo_path)
        diff_text = processor.get_uncommitted_changes()
        summary = processor.generate_diff_summary(diff_text)
        processor.create_commit_with_summary(summary)
    except Exception as e:
        print(f"Error in main execution: {str(e)}")