#!/usr/bin/env python3
"""
Apple Notes MCP Server
Provides tools to interact with Apple Notes on macOS using AppleScript.
"""

import subprocess
import json
import re
from typing import Any, List, Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("apple-notes")


def run_applescript(script: str) -> tuple[str, bool]:
    """Run an AppleScript command and return the output."""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip(), True
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return f"Error: {error_msg}", False
    except subprocess.TimeoutExpired:
        return "Error: AppleScript execution timed out", False
    except Exception as e:
        return f"Error: {str(e)}", False


def escape_applescript_string(text: str) -> str:
    """Escape special characters for AppleScript strings."""
    # Replace backslashes, quotes, and newlines
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("\n", "\\n")
    return text


@mcp.tool()
async def list_notes(account: Optional[str] = None, folder: Optional[str] = None) -> str:
    """List all notes or notes from a specific account/folder.
    
    Args:
        account: Optional account name (e.g., "iCloud", "On My Mac")
        folder: Optional folder name within the account
    """
    if account and folder:
        script = f'''
        tell application "Notes"
            set accountName to "{escape_applescript_string(account)}"
            set folderName to "{escape_applescript_string(folder)}"
            set noteList to {{}}
            try
                set targetAccount to account accountName
                set targetFolder to folder folderName of targetAccount
                repeat with aNote in notes of targetFolder
                    set end of noteList to (name of aNote) & "|" & (id of aNote) & "|" & (modification date of aNote as string)
                end repeat
            end try
            return noteList
        end tell
        '''
    elif account:
        script = f'''
        tell application "Notes"
            set accountName to "{escape_applescript_string(account)}"
            set noteList to {{}}
            try
                set targetAccount to account accountName
                repeat with aNote in notes of targetAccount
                    set end of noteList to (name of aNote) & "|" & (id of aNote) & "|" & (modification date of aNote as string)
                end repeat
            end try
            return noteList
        end tell
        '''
    else:
        script = '''
        tell application "Notes"
            set noteList to {}
            repeat with anAccount in accounts
                repeat with aNote in notes of anAccount
                    set end of noteList to (name of anAccount) & "::" & (name of aNote) & "|" & (id of aNote) & "|" & (modification date of aNote as string)
                end repeat
            end repeat
            return noteList
        end tell
        '''
    
    output, success = run_applescript(script)
    if not success:
        return output
    
    # Parse the output
    if not output or output == "{}":
        return "No notes found."
    
    # AppleScript returns a list like: {"Note 1|id1|date1", "Note 2|id2|date2"}
    # Parse it
    notes = []
    for item in output.split(", "):
        item = item.strip().strip('"').strip("'")
        if "|" in item:
            parts = item.split("|")
            if len(parts) >= 3:
                notes.append({
                    "name": parts[0],
                    "id": parts[1],
                    "modified": parts[2]
                })
    
    if not notes:
        return "No notes found."
    
    result = "Found notes:\n"
    for i, note in enumerate(notes, 1):
        result += f"{i}. {note['name']} (ID: {note['id']}, Modified: {note['modified']})\n"
    
    return result


@mcp.tool()
async def search_notes(query: str, account: Optional[str] = None) -> str:
    """Search for notes containing the specified text.
    
    Args:
        query: Text to search for in note content
        account: Optional account name to search within
    """
    if account:
        script = f'''
        tell application "Notes"
            set accountName to "{escape_applescript_string(account)}"
            set searchResults to {{}}
            try
                set targetAccount to account accountName
                repeat with aNote in notes of targetAccount
                    set noteContent to body of aNote
                    if noteContent contains "{escape_applescript_string(query)}" or name of aNote contains "{escape_applescript_string(query)}" then
                        set end of searchResults to (name of aNote) & "|" & (id of aNote)
                    end if
                end repeat
            end try
            return searchResults
        end tell
        '''
    else:
        script = f'''
        tell application "Notes"
            set searchResults to {{}}
            repeat with anAccount in accounts
                repeat with aNote in notes of anAccount
                    set noteContent to body of aNote
                    if noteContent contains "{escape_applescript_string(query)}" or name of aNote contains "{escape_applescript_string(query)}" then
                        set end of searchResults to (name of anAccount) & "::" & (name of aNote) & "|" & (id of aNote)
                    end if
                end repeat
            end repeat
            return searchResults
        end tell
        '''
    
    output, success = run_applescript(script)
    if not success:
        return output
    
    if not output or output == "{}":
        return f"No notes found containing '{query}'."
    
    results = []
    for item in output.split(", "):
        item = item.strip().strip('"').strip("'")
        if "|" in item:
            parts = item.split("|")
            if len(parts) >= 2:
                results.append({
                    "name": parts[0],
                    "id": parts[1]
                })
    
    if not results:
        return f"No notes found containing '{query}'."
    
    result = f"Found {len(results)} note(s) containing '{query}':\n"
    for i, note in enumerate(results, 1):
        result += f"{i}. {note['name']} (ID: {note['id']})\n"
    
    return result


@mcp.tool()
async def read_note(note_name: str, account: Optional[str] = None) -> str:
    """Read the content of a specific note by name.
    
    Args:
        note_name: Name of the note to read
        account: Optional account name where the note is located
    """
    if account:
        script = f'''
        tell application "Notes"
            set accountName to "{escape_applescript_string(account)}"
            set noteName to "{escape_applescript_string(note_name)}"
            try
                set targetAccount to account accountName
                set targetNote to note noteName of targetAccount
                return (body of targetNote)
            on error
                return "ERROR: Note not found"
            end try
        end tell
        '''
    else:
        script = f'''
        tell application "Notes"
            set noteName to "{escape_applescript_string(note_name)}"
            repeat with anAccount in accounts
                try
                    set targetNote to note noteName of anAccount
                    return (body of targetNote)
                end try
            end repeat
            return "ERROR: Note not found"
        end tell
        '''
    
    output, success = run_applescript(script)
    if not success or output == "ERROR: Note not found":
        return output if output else f"Note '{note_name}' not found."
    
    return f"Note: {note_name}\n\n{output}"


@mcp.tool()
async def create_note(title: str, content: str, account: Optional[str] = None, folder: Optional[str] = None) -> str:
    """Create a new note with the specified title and content.
    
    Args:
        title: Title/name for the new note
        content: Content/body of the note
        account: Optional account name (defaults to default account)
        folder: Optional folder name within the account
    """
    escaped_title = escape_applescript_string(title)
    escaped_content = escape_applescript_string(content)
    
    if account and folder:
        script = f'''
        tell application "Notes"
            set accountName to "{escape_applescript_string(account)}"
            set folderName to "{escape_applescript_string(folder)}"
            try
                set targetAccount to account accountName
                set targetFolder to folder folderName of targetAccount
                make new note at targetFolder with properties {{name:"{escaped_title}", body:"{escaped_content}"}}
                return "SUCCESS"
            on error errMsg
                return "ERROR: " & errMsg
            end try
        end tell
        '''
    elif account:
        script = f'''
        tell application "Notes"
            set accountName to "{escape_applescript_string(account)}"
            try
                set targetAccount to account accountName
                make new note at targetAccount with properties {{name:"{escaped_title}", body:"{escaped_content}"}}
                return "SUCCESS"
            on error errMsg
                return "ERROR: " & errMsg
            end try
        end tell
        '''
    else:
        script = f'''
        tell application "Notes"
            try
                make new note with properties {{name:"{escaped_title}", body:"{escaped_content}"}}
                return "SUCCESS"
            on error errMsg
                return "ERROR: " & errMsg
            end try
        end tell
        '''
    
    output, success = run_applescript(script)
    if not success or "ERROR" in output:
        return output if output else "Failed to create note."
    
    return f"Successfully created note '{title}'."


@mcp.tool()
async def update_note(note_name: str, new_content: str, account: Optional[str] = None) -> str:
    """Update the content of an existing note.
    
    Args:
        note_name: Name of the note to update
        new_content: New content for the note
        account: Optional account name where the note is located
    """
    escaped_name = escape_applescript_string(note_name)
    escaped_content = escape_applescript_string(new_content)
    
    if account:
        script = f'''
        tell application "Notes"
            set accountName to "{escape_applescript_string(account)}"
            set noteName to "{escaped_name}"
            try
                set targetAccount to account accountName
                set targetNote to note noteName of targetAccount
                set body of targetNote to "{escaped_content}"
                return "SUCCESS"
            on error errMsg
                return "ERROR: " & errMsg
            end try
        end tell
        '''
    else:
        script = f'''
        tell application "Notes"
            set noteName to "{escaped_name}"
            repeat with anAccount in accounts
                try
                    set targetNote to note noteName of anAccount
                    set body of targetNote to "{escaped_content}"
                    return "SUCCESS"
                end try
            end repeat
            return "ERROR: Note not found"
        end tell
        '''
    
    output, success = run_applescript(script)
    if not success or "ERROR" in output:
        return output if output else f"Failed to update note '{note_name}'."
    
    return f"Successfully updated note '{note_name}'."


@mcp.tool()
async def delete_note(note_name: str, account: Optional[str] = None) -> str:
    """Delete a note by name.
    
    Args:
        note_name: Name of the note to delete
        account: Optional account name where the note is located
    """
    escaped_name = escape_applescript_string(note_name)
    
    if account:
        script = f'''
        tell application "Notes"
            set accountName to "{escape_applescript_string(account)}"
            set noteName to "{escaped_name}"
            try
                set targetAccount to account accountName
                set targetNote to note noteName of targetAccount
                delete targetNote
                return "SUCCESS"
            on error errMsg
                return "ERROR: " & errMsg
            end try
        end tell
        '''
    else:
        script = f'''
        tell application "Notes"
            set noteName to "{escaped_name}"
            repeat with anAccount in accounts
                try
                    set targetNote to note noteName of anAccount
                    delete targetNote
                    return "SUCCESS"
                end try
            end repeat
            return "ERROR: Note not found"
        end tell
        '''
    
    output, success = run_applescript(script)
    if not success or "ERROR" in output:
        return output if output else f"Failed to delete note '{note_name}'."
    
    return f"Successfully deleted note '{note_name}'."


@mcp.tool()
async def list_accounts() -> str:
    """List all available Notes accounts."""
    script = '''
    tell application "Notes"
        set accountList to {}
        repeat with anAccount in accounts
            set end of accountList to name of anAccount
        end repeat
        return accountList
    end tell
    '''
    
    output, success = run_applescript(script)
    if not success:
        return output
    
    if not output or output == "{}":
        return "No accounts found."
    
    accounts = [acc.strip().strip('"').strip("'") for acc in output.split(", ")]
    
    result = "Available accounts:\n"
    for i, account in enumerate(accounts, 1):
        result += f"{i}. {account}\n"
    
    return result


def main():
    """Run the MCP server."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()

