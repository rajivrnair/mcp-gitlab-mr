# Install uv (curl or brew)
```
brew install uv
source ~/.zshrc # Installation adds $HOME/.local/bin to your PATH. So restart your terminal and source your shell config.
uv --version
```
See [UV installation](https://docs.astral.sh/uv/getting-started/installation/) for more options

# Setup the python environment (needs python 3.10+)
``` 
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
