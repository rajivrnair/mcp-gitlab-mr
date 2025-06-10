# Install uv (curl or brew)
```
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc # It adds $HOME/.local/bin to your PATH
uv --version
```

# Create a new uv project
``` 
uv init mcp-gitlab-mr
cd mcp-gitlab-mr
uv venv
source .venv/bin/activate
python --version #should be 3.10+
```

# Add fastmcp to the project
```
uv add fastmcp
fastmcp version
```

# MCP config for Claude Code (~/.claude.json)
```json
"mcpServers": {
  "mcp-gitlab-mr": {
    "command": "uv",
    "args": [
      "--directory",
      "/<absolute-path-to-workspace>/mcp-gitlab-mr",
      "run",
      "gitlab_mr.py"
    ],
    "env": {
      "PROJECT_ID": <gitlab-project-id>,
      "DOWNLOAD_PATH": "/<absolute-path-to-workspace>/<repo-name>/.gitlab/reviews/diffs"
    }
  }
}
```