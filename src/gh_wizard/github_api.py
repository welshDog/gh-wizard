"""GitHub GraphQL API client."""

import os
import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel
from gh_wizard.utils.logger import setup_logger

logger = setup_logger(__name__)


class GitHubAPIClient(BaseModel):
    """Client for GitHub GraphQL API."""

    token: str
    endpoint: str = "https://api.github.com/graphql"

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token. If not provided, uses GH_TOKEN env var.
        """
        if not token:
            token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GitHub token not found. Set GH_TOKEN or GITHUB_TOKEN env var.")
        super().__init__(token=token)

    def query(self, query_string: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query.
        
        Args:
            query_string: GraphQL query string
            variables: Query variables
            
        Returns:
            Query response data
            
        Raises:
            Exception: If query fails
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        payload = {"query": query_string}
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if "errors" in data:
                logger.error(f"GraphQL error: {data['errors']}")
                raise Exception(f"GraphQL error: {data['errors']}")
            
            return data.get("data", {})
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def get_viewer_info(self) -> Dict[str, Any]:
        """Get authenticated user info."""
        query = """
            query {
                viewer {
                    login
                    name
                    bio
                    repositories(first: 10) {
                        nodes {
                            name
                            description
                            url
                        }
                    }
                }
            }
        """
        return self.query(query)

    def get_repos_status(self, first: int = 10) -> Dict[str, Any]:
        """Get status of user's repositories."""
        query = """
            query GetReposStatus($first: Int!) {
                viewer {
                    repositories(first: $first, orderBy: {field: UPDATED_AT, direction: DESC}) {
                        nodes {
                            name
                            description
                            url
                            issues(states: OPEN) {
                                totalCount
                            }
                            pullRequests(states: OPEN) {
                                totalCount
                            }
                            defaultBranchRef {
                                name
                            }
                        }
                    }
                }
            }
        """
        return self.query(query, {"first": first})

    def get_open_issues(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Get open issues for a repository."""
        query = """
            query GetIssues($owner: String!, $name: String!) {
                repository(owner: $owner, name: $name) {
                    issues(first: 20, states: OPEN) {
                        nodes {
                            number
                            title
                            labels(first: 5) {
                                nodes {
                                    name
                                }
                            }
                            createdAt
                        }
                    }
                }
            }
        """
        return self.query(query, {"owner": repo_owner, "name": repo_name})
