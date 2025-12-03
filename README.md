# Apple Notes MCP Server

An MCP (Model Context Protocol) server for interacting with Apple Notes on macOS.

## Features

- List notes from all accounts or specific accounts/folders
- Search notes by content
- Read note content
- Create new notes
- Update existing notes
- Delete notes
- List available accounts

## Requirements

- macOS (uses AppleScript to interact with Notes app)
- Python 3.10+
- Notes app must be installed and accessible

## Notes

- The server uses AppleScript to interact with the Notes app
- You will need to grant Terminal/iTerm/Cursor *PERMISSION* to control Notes in System Preferences > Security & Privacy > Accessibility
- Account names are case-sensitive (e.g., "iCloud" vs "icloud")


## Installation

```bash
git clone https://github.com/arslankhanali/apple-notes-mcp.git
cd apple-notes-mcp
uv venv
source .venv/bin/activate
uv add "mcp[cli]"

# To run
# uv run apple_notes.py
```

## Usage with Cursor
Add to your MCP configuration (`~/.cursor/mcp.json`):

> Change `/path/to/apple-notes-mcp` to where you cloned this repo

```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/apple-notes-mcp",
        "run",
        "apple_notes.py"
      ]
    }
  }
}
```

## Available Tools

- `list_notes` - List all notes or notes from a specific account/folder
- `search_notes` - Search for notes containing specific text
- `read_note` - Read the content of a specific note
- `create_note` - Create a new note with title and content
- `update_note` - Update the content of an existing note
- `delete_note` - Delete a note
- `list_accounts` - List all available Notes accounts

