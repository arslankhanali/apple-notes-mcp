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

## Installation

```bash
cd apple_notes
uv venv
source .venv/bin/activate
uv add "mcp[cli]"
```

## Usage

Run the server:
```bash
uv run apple_notes.py
```

Or add to your MCP configuration (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "apple-notes": {
      "command": "uv",
      "args": [
        "--directory",
        "~/Codes/mcp/apple_notes",
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

## Notes

- The server uses AppleScript to interact with the Notes app
- You may need to grant Terminal/iTerm/Cursor permission to control Notes in System Preferences > Security & Privacy > Accessibility
- Account names are case-sensitive (e.g., "iCloud" vs "icloud")

# apple-notes-mcp
