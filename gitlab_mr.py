import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("mcp-gitlab-mr",
  instructions="""This server provides GitLab merge request management tools.
  
  Available tools:
  
  1. list_mr() - Retrieve merge requests with comprehensive filtering options.
     The tool returns a 'display' field with formatted output that should be shown to users
     for visual presentation, plus structured data in 'merge_requests' field.
     
     State filtering:
     - "opened" (default): Show open merge requests
     - "closed": Show closed merge requests  
     - "merged": Show merged merge requests
     - "locked": Show locked merge requests
     - "all": Show merge requests in any state
     
     User filtering:
     - "all" (default): Show all merge requests regardless of user
     - "assigned_to_me": Show merge requests assigned to current user
     - "created_by_me": Show merge requests created by current user
     
     Email override:
     - git_email: Optional parameter to filter by a specific user's email instead of current GitLab user
  
  2. download_diff() - Download raw diff content for a specific merge request.
     Args:
     - mr_iid: The merge request IID (internal ID, e.g., "123")
     - save_to_file: Whether to save the diff to a timestamped file (default: True)
     - output_dir: Directory to save the diff file (default: current directory)
     
     Returns the raw diff content and optionally saves it to .gitlab/diffs/ directory.
  
  Examples:
  - list_mr() - Get open merge requests (default)
  - list_mr(state="merged", filter_by="created_by_me") - Get merged MRs created by current user
  - list_mr(state="all", filter_by="assigned_to_me", git_email="user@example.com") - Get all MRs assigned to specific user
  - download_diff("123") - Download diff for MR !123 and save to file
  - download_diff("123", save_to_file=False) - Get diff content without saving to file
  - download_diff("123", output_dir="/path/to/project") - Save diff in specific directory
  
  IMPORTANT: Always display the 'display' field content to show formatted merge request details to users.
  """)

class GitLabAPI:
    def __init__(self, project_id: str):
        self.base_url = "https://gitlab.com/api/v4"
        self.token = self._get_token()
        self.project_id = project_id
        self.current_user = None

    def _get_token(self) -> str:
        token = os.getenv('GITLAB_TOKEN')
        if not token:
            raise ValueError("GITLAB_TOKEN environment variable not set")
        return token


    def _make_request(self, endpoint: str) -> Dict:
        url = f"{self.base_url}{endpoint}"
        
        req = urllib.request.Request(url)
        req.add_header('PRIVATE-TOKEN', self.token)
        req.add_header('Content-Type', 'application/json')
        
        try:
            with urllib.request.urlopen(req) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise ValueError("Authentication failed. Check your GITLAB_TOKEN")
            elif e.code == 404:
                raise ValueError(f"Resource not found: {endpoint}")
            else:
                error_body = e.read().decode('utf-8') if e.fp else 'Unknown error'
                raise ValueError(f"API request failed with status {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise ValueError(f"Network error: {e.reason}")

    def get_current_user(self) -> Dict:
        """Get current user info"""
        if self.current_user is None:
            self.current_user = self._make_request("/user")
        return self.current_user

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address"""
        try:
            users = self._make_request(f"/users?search={email}")
            for user in users:
                if user.get('email') == email:
                    return user
            return None
        except Exception:
            return None

    def get_merge_requests(self, state: str = "opened", scope: str = "all", author_id: Optional[int] = None, assignee_id: Optional[int] = None) -> List[Dict]:
        """Fetch merge requests for the project"""
        endpoint = f"/projects/{self.project_id}/merge_requests?state={state}&scope={scope}"
        
        if author_id:
            endpoint += f"&author_id={author_id}"
        if assignee_id:
            endpoint += f"&assignee_id={assignee_id}"
            
        return self._make_request(endpoint)

    def get_raw_diffs(self, mr_iid: str) -> str:
        """Get raw diffs for the specified merge request"""
        endpoint = f"/projects/{self.project_id}/merge_requests/{mr_iid}/raw_diffs"
        url = f"{self.base_url}{endpoint}"

        req = urllib.request.Request(url)
        req.add_header('PRIVATE-TOKEN', self.token)

        try:
            with urllib.request.urlopen(req) as response:
                return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else 'Unknown error'
            raise ValueError(f"Failed to get diffs: {e.code} - {error_body}")
        except urllib.error.URLError as e:
            raise ValueError(f"Network error: {e.reason}")

def _display_merge_requests(merge_requests: List[Dict], show_details: bool = False) -> str:
    """Display list of merge requests in a visually appealing format"""
    if not merge_requests:
        return "No merge requests found."
    
    # Auto-enable details if there's only one merge request
    if len(merge_requests) == 1:
        show_details = True
    
    output = []
    output.append(f"\nMerge Requests ({len(merge_requests)} found):")
    output.append("=" * 60)
    
    for i, mr in enumerate(merge_requests, 1):
        status_emoji = "🟢" if mr['state'] == 'opened' else "🔴" if mr['state'] == 'closed' else "🟡"
        
        output.append(f"{i}. {status_emoji} MR !{mr['iid']} - {mr['title']}")
        output.append(f"   👤 Author: {mr['author']['name']}")
        output.append(f"   🌿 Source: {mr['source_branch']} → {mr['target_branch']}")
        output.append(f"   📅 Created: {mr['created_at'][:10]}")
        
        if show_details:
            output.append(f"   📝 Description: {mr.get('description', 'No description')[:100]}...")
            output.append(f"   ✅ Upvotes: {mr.get('upvotes', 0)}")
            output.append(f"   ❌ Downvotes: {mr.get('downvotes', 0)}")
            if mr.get('assignees'):
                assignee_names = [a['name'] for a in mr['assignees']]
                output.append(f"   👥 Assignees: {', '.join(assignee_names)}")
            if mr.get('labels'):
                output.append(f"   🏷️  Labels: {', '.join(mr['labels'])}")
        
        output.append(f"   🔗 URL: {mr['web_url']}")
        output.append("")
    
    return "\n".join(output)

def get_project_id() -> str:
    """Get project_id from PROJECT_ID environment variable"""
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        raise ValueError("PROJECT_ID environment variable not set")
    return project_id

gitlab_api = None

@mcp.tool
def list_mr(state: str = "opened", filter_by: str = "all", git_email: Optional[str] = None) -> Dict:
    """
    List merge requests for the GitLab project and displays the output in a visually appealing format.
    
    Args:
        state: The state of MRs to filter by ("opened", "closed", "merged", "locked", "all")
        filter_by: Filter MRs by user ("all", "assigned_to_me", "created_by_me")
        git_email: Optional git email to filter by instead of current user
    
    Returns:
        Dictionary with 'display' field containing formatted output for visual presentation
        and 'merge_requests' field containing structured data
    """
    global gitlab_api
    try:
        # Initialize gitlab_api if not already done
        if gitlab_api is None:
            project_id = get_project_id()
            gitlab_api = GitLabAPI(project_id)
        # Validate state parameter
        valid_states = ["opened", "closed", "merged", "locked", "all"]
        if state not in valid_states:
            return {"error": f"Invalid state '{state}'. Must be one of: {', '.join(valid_states)}"}
        
        # Determine user filtering
        author_id = None
        assignee_id = None
        
        if filter_by in ["assigned_to_me", "created_by_me"]:
            if git_email:
                user = gitlab_api.get_user_by_email(git_email)
                if not user:
                    return {"error": f"User with email '{git_email}' not found"}
                user_id = user['id']
            else:
                current_user = gitlab_api.get_current_user()
                user_id = current_user['id']
            
            if filter_by == "assigned_to_me":
                assignee_id = user_id
            elif filter_by == "created_by_me":
                author_id = user_id
        
        # Fetch merge requests
        merge_requests = gitlab_api.get_merge_requests(
            state=state,
            scope="all",
            author_id=author_id,
            assignee_id=assignee_id
        )
        
        # Display merge requests using the visual formatter
        display_output = _display_merge_requests(merge_requests)
        
        # Also return structured data
        result = {
            "display": display_output,
            "merge_requests": [],
            "total_count": len(merge_requests),
            "filter": {
                "state": state,
                "filter_by": filter_by,
                "git_email": git_email
            }
        }
        
        for mr in merge_requests:
            formatted_mr = {
                "iid": mr['iid'],
                "title": mr['title'],
                "state": mr['state'],
                "author": mr['author']['name'],
                "author_email": mr['author'].get('email', ''),
                "source_branch": mr['source_branch'],
                "target_branch": mr['target_branch'],
                "created_at": mr['created_at'],
                "updated_at": mr['updated_at'],
                "web_url": mr['web_url'],
                "description": mr.get('description', ''),
                "assignees": [a['name'] for a in mr.get('assignees', [])],
                "labels": mr.get('labels', []),
                "upvotes": mr.get('upvotes', 0),
                "downvotes": mr.get('downvotes', 0)
            }
            result["merge_requests"].append(formatted_mr)
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def download_diff(mr_iid: str, save_to_file: bool = True) -> Dict:
    """
    Download raw diff for a specific merge request and displays the output in a visually appealing format.
    
    Args:
        mr_iid: The merge request IID (internal ID, e.g., "123")
        save_to_file: Whether to save the diff to a timestamped file (default: True)
    
    Returns:
        Dictionary containing the raw diff content and metadata
    """
    global gitlab_api
    try:
        # Initialize gitlab_api if not already done
        if gitlab_api is None:
            project_id = get_project_id()
            gitlab_api = GitLabAPI(project_id)
        # Validate MR IID
        if not mr_iid.isdigit():
            return {"error": "MR IID must be a number"}
        
        # Download raw diff
        raw_diff = gitlab_api.get_raw_diffs(mr_iid)
        
        result = {
            "mr_iid": mr_iid,
            "raw_diff": raw_diff,
            "diff_size": len(raw_diff),
            "saved_to_file": False,
            "file_path": None
        }
        
        if save_to_file:
            # Get output_dir from environment variable DOWNLOAD_PATH
            output_dir = os.getenv('DOWNLOAD_PATH')
            if not output_dir:
                raise ValueError("DOWNLOAD_PATH environment variable not set")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"{timestamp}.merge-diff-{mr_iid}.txt"
            filepath = os.path.join(output_dir, filename)
            
            # Save diff to file
            with open(filepath, 'w') as f:
                f.write(raw_diff)
            
            result["saved_to_file"] = True
            result["file_path"] = filepath
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()
