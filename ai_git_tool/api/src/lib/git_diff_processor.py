from git import Repo
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from typing import Optional
from dotenv import load_dotenv
from src.interfaces import llm

class GitDiffProcessor:
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize the GitDiffProcessor with a repo path and LangChain components."""
        load_dotenv()
        self.repo = Repo(repo_path or os.getcwd())
        
        # Initialize the LLM
        self.llm = llm.gpt_4o()
        
        # Create prompt template using ChatPromptTemplate
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that summarizes git diffs concisely."),
            ("user", "Please summarize these changes briefly:\n{diff_text}")
        ])
        
        # Create the LCEL chain
        self.chain = self.prompt | self.llm | StrOutputParser()

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

    def create_commit_with_summary(self, summary: str) -> None:
        """Create a git commit with the provided summary."""
        try:
            # Stage all changes
            self.repo.git.add('.')
            
            # Create commit with the AI-generated summary
            self.repo.index.commit(summary)
        except Exception as e:
            raise Exception(f"Error creating commit: {str(e)}")


if __name__ == "__main__":
    # Example usage with a path
    try:
        repo_path = "/home/jorge/futino/wb"
        processor = GitDiffProcessor(repo_path)
        diff_text = processor.get_uncommitted_changes()
        summary = processor.generate_diff_summary(diff_text)
        processor.create_commit_with_summary(summary)
    except Exception as e:
        print(f"Error in main execution: {str(e)}")