# AGENTS.md

## AI Code Assistant Guidelines for This Project

You are an expert macOS automation engineer and Python developer. Create a complete, production-quality repo for a privacy-first, semi-assisted workflow to retrieve data for contacts on a Mac, find logical associations using AI to help add useful associations (tags) and collect related contacts into useful groups. Your role is to assist in writing clean, efficient, and well-documented code that adheres to the project's standards and conventions.

## Project Overview

This project implements a privacy-first, semi-assisted workflow that:

1. Extracts communication relationship signals from:
    - macOS Messages database (iMessage/SMS/RCS) on the local Mac, focusing on GROUP chats first
    - Apple Mail exports (MBOX format) next
2. Compares participants against existing iCloud contacts (via vCard export) to identify:
    - high-value frequent contacts missing from Contacts
    - suggested groups/tags for organization
3. Uses an LLM (pluggable provider) to propose groupings + names with a human review step (semi-assisted)
4. Exports results in formats that can be applied back to iCloud Contacts using BusyContacts tagging (since BusyContacts tags map to iCloud Groups) and/or vCard imports

### Primary Goals

- **Minimal exposure of message/email content**: default to extracting only metadata (participants, counts, recency, thread membership, email header recipients, subject tokens) and never require message bodies
- **Semi-assisted workflow**: (a) generate suggestions, (b) present a review UI in Excel (xlsx) format with suggested tags and suggested groups as columns, (c) apply confirmed groups/tags via exported vCards + instructions for BusyContacts tagging

## Technical Requirements

### Platform Constraints

Hard facts and constraints you MUST respect in the implementation and documentation:

- **Messages data** can be read from the SQLite database at: `~/Library/Messages/chat.db` (macOS). Include extraction that uses sqlite queries. Document that reading may require granting Full Disk Access to the terminal/app accessing it
- Provide an alternative extraction path using the open-source "imessage-exporter" tool (CLI) as an optional method. Do not require it, but document how it can be used
- **Apple Mail** supports exporting mailboxes to .mbox via Mailbox > Export Mailbox. Document this and design the parser around standard MBOX exports
- **BusyContacts**:
  - Tags in BusyContacts map to Groups in Apple Contacts/iCloud. Design the output to create tags/groups accordingly
  - BusyContacts can import vCard (.vcf) but does NOT import CSV directly. The Excel (xlsx) review file is for human review only; final application uses vCard-based or Contacts-intermediary import flow

### Tech Stack

- Python 3.11+
- Standard libs where possible: sqlite3, mailbox, email, csv, json, argparse, datetime, re, pathlib
- DuckDB for data loading and manipulation (primary data processing tool)
- Pandas for smaller subsets of data and reporting
- Pydantic for schemas
- PyYAML for YAML file handling
- openpyxl or xlsxwriter for Excel (xlsx) report generation
- mkdocs for documentation with document source located in `docsrc/mkdocs/`
- Use a clean, testable architecture with module-level logging via `get_logger` function

## Standards and Conventions

Please follow these standards and conventions when generating or editing code:

### 1. Coding Standards

- **PEP8**: All Python code must comply with [PEP8](https://peps.python.org/pep-0008/) style guidelines.
- **Type Hints**: All functions and class methods must include explicit type hints for arguments and return values.
- **Docstrings**: Use the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings. 

  - Each function/class should have a docstring with an `Args:` section for parameters.
  - When applicable, include `Returns:` and `Raises:` sections. 
  - When iconic notes are needed, use the following format:

    - Use `!!! tip` for useful tips.
    - Use `!!! note` for general notes.
    - Use `!!! warning` for warnings.
    - Use `!!! danger` for critical warnings or dangers.

- **Code Samples**: When including code examples in docstrings avoid using `Example:`. Instead, use triple backticks for code examples within docstrings.

### 2. Docstring Example

```python

variable: str = "This is a variable with a docstring example."
"""This variable is an example of how to include a docstring for a variable."""

def example_function(param1: int, param2: str) -> bool:
    """
    Brief description of what the function does.

    !!! note
        Additional notes about the function.

    ??? note "Collaspsible Note with Title"
        This is a collapsible note section using a custom title.

    !!! warning
        Warnings about the function usage.

    ``` python
    result = example_function(10, "test")
    print(result)
    ```
    
    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        bool: Description of the return value.
    """
    ...
```

### 3. Project Structure

- Main source code is in `src/icloud-contacts-organizer/`
- Configuration files are in `config/`
- Any credentials or sensitive information should be stored in `config/secrets.yml` (not committed to version control)
- Scripts supporting specific tasks are in `scripts/`
- Data files are in the `data/` directory
- Any intermediate data, such as database exports, shall be stored in `data/intermediate`, and if the data is from a specific source put it in a named subdirecotry, such as data exported from the local Contacts shall be stored in `data/intermediate\contacts`.
- Notebooks are in `notebooks/`, and are for creating ready (or nearly ready) to run examples of using the Python package located in `/src`.
- Tests are in `testing/`
- Documentation is in `docsrc/mkdocs/` - add new documentation files here and update the mkdocs configuration as needed.

### 4. Documentation - MkDocs Guidance

- Use MkDocs for project documentation. Add new documentation files in `docsrc/mkdocs/`
- If it makes senese to order the documentation, prefix the filenames with numbers (e.g., `01_introduction.md`, `02_usage.md`) to control the order in the navigation, and set the title in the front matter of the markdown file to ensure it appears correctly in the navigation.
- Ensure indentation in markdown files is consistent, multiples of four spaces.
- Use headings (e.g., `#`, `##`, `###`) to structure the documentation clearly.
- For bulleted lists in markdown, use `-` for list items and ensure there is a space after the dash for proper formatting. Also ensure there is a line break before and after the list for better readability.
- Use fenced code blocks with triple backticks for code examples in markdown files, and specify the language for syntax highlighting (e.g., ```python).
- Utilize admonitions in markdown files for important notes, tips, warnings, and dangers using the following syntax:

  - Use `!!! tip` for useful tips.
  - Use `!!! note` for general notes.
  - Use `!!! warning` for warnings about potential issues.
  - Use `!!! danger` for critical warnings or dangers.
  - For collapsible sections in markdown, use the following syntax:

  ``` markdown
  ??? note "Collapsibe Note Title"
      This is the content of the collapsible note.
  ```

- For codeblocks in markdown lists, ensure proper indentation to maintain the list structure. For example:

  ``` markdown
  - Top level list item

    - Nested list item with a code block:

    ``` python
    def nested_example():
    pass
    ```
  ```

### 5. Additional Guidelines

- Prefer clear, descriptive variable and function names.
- Use list comprehensions and generator expressions where it logically makes sense for improved performance.
- When working with data, prefer to use DuckDB for loading and manipulating data.
- In all function calls, use keyword arguments following the first positional argument for clarity, especially when there are multiple parameters of the same type.
- When working with smaller subsets of data, prefer using Pandas DataFrames for data manipulation and analysis, and use vectorized operations instead of loops for better performance.
- Avoid global variables.
- Write modular, reusable code.
- Add comments for complex logic.
- For data manipulation prefer DuckDB, Pandas, NumPy, and SciKit-Learn when possible.
- Avoid early returns from functions.
- Use module level logging throughout codebase using the get_logger function.
- Add through multi-level facilitating detailed reporting if desried for debugging.
- Add through error catching providing clear explanation of failure and detailed information for debugging, typically as a through try/except logging out errors and then raising.

### 6. AI Assistant Usage

- When generating code, always check for existing functions/classes before creating new ones.
- When editing, preserve existing logic unless explicitly instructed to refactor.
- When adding new files, update relevant documentation and tests.

## Architecture & Deliverables

### Project Structure

Full project structure with:

- `src/icloud_contacts_organizer/` package (note underscore in package name)
- `testing/` directory for all tests
- `docsrc/mkdocs/` for documentation
- `scripts/` for utility scripts
- `config/` with config.yml and secrets.yml
- `data/` with subdirectories: external/, interim/, processed/, raw/

### CLI Commands

A CLI with subcommands:

- **extract-messages**: extract group chats + participants from chat.db (no message text by default)
- **extract-mail**: parse exported MBOX files; extract From/To/Cc + subject tokens (no body by default)
- **export-contacts**: help user export existing Contacts as vCard and parse it
- **build-graph**: unify identities, normalize emails/phones, build a weighted relationship graph
- **suggest-groups**: run clustering + LLM naming/suggestions (pluggable LLM providers)
- **report**: generate a human-reviewable Excel (xlsx) report with suggested tags and suggested groups as columns
- **export-vcards**: generate vCards for missing contacts (optional), and create a "tag assignment plan"

### Data Model & Schema

- **PersonIdentity**: email(s), phone(s), display_name if known
- **Thread**: id, participants, last_activity, msg_count
- **RelationshipEdge**: a, b, weight, sources: messages/mail
- **GroupSuggestion**: name, members, confidence, rationale, source_signals

### LLM Integration

Provide an interface: LLMProvider with implementations:

- **OpenAI-compatible**: via environment variable base URL + API key
- **Local model**: simple HTTP endpoint option
- **No-LLM mode**: deterministic clustering + heuristic naming

Prompts must be minimal: only send participant sets, counts, and subject keywords; never send message bodies unless the user explicitly enables it.

### Semi-Assisted Review

Generate an Excel (xlsx) report with the following columns:

- **Contact Name**: individual contact name
- **Contact Status**: exists in Contacts or missing
- **Suggested Tags**: recommended tags (comma-separated if multiple)
- **Suggested Groups**: recommended groups (comma-separated if multiple)
- **Confidence**: confidence score for the suggestion
- **Rationale**: why they were grouped (signals: "co-occur in group chat X", "frequent email recipients", "same domain")
- **Email**: contact email address(es)
- **Phone**: contact phone number(s)

Provide a confirmation step that outputs final "apply plan":

- group/tag name -> list of contact identifiers

### Apply Plan Outputs

- **A)** Excel (xlsx) file for human review with suggested tags and groups as columns
- **B)** YAML file with the apply plan for programmatic processing
- **C)** vCard files (per group or one combined) with NOTES field including proposed tag/group name
- **D)** Documentation describing how to apply tags as iCloud Groups using BusyContacts, emphasizing tags->iCloud Groups mapping

### Safety/Privacy and Compliance

- Do not modify user databases directly (do not write to chat.db, do not automate Contacts modifications without explicit user action)
- Redact or hash identifiers in logs
- Provide a "--privacy-mode" default ON that strips subjects to keywords and never reads bodies

### macOS Permissions

- Explain Full Disk Access requirements for reading `~/Library/Messages/chat.db`
- Provide steps and troubleshooting

## Implementation Details

### Messages Extraction

- Use sqlite3 to query chat.db for: chat IDs, participant handles, message counts, last activity. Focus on group chats first
- Provide query templates and adapt them carefully (schema differences can exist). Add a schema introspection step
- Store extracted data in `data/interim/messages/`

### Mail Extraction

- Parse .mbox packages or mbox files using Python's mailbox.mbox
- Extract address headers and subject, tokenize/normalize domains
- Store extracted data in `data/interim/mail/`

### Identity Resolution

- Normalize phone numbers (E.164-ish simple normalization) and email casing
- Link identities using vCard known info and heuristics (same email, same normalized phone)

### Graph/Clustering

- Use DuckDB for building and querying the relationship graph
- Provide deterministic grouping: connected components, Louvain-like approximation (or simple community detection) with weights
- Then LLM only names/refines and suggests merges/splits (optional)

### Performance

- Must handle large histories; stream where possible; avoid loading all messages/emails in memory
- Use DuckDB for efficient data processing of large datasets

### Code Quality

- Use module-level logging via `get_logger` function throughout
- Use keyword arguments after the first positional argument for clarity
- Avoid early returns from functions
- Implement thorough error catching with try/except blocks, logging errors before raising
- Include multi-level logging for detailed debugging when needed

### CLI UX

- Rich help text, examples
- Config file support: YAML format (config.yml, secrets.yml)
- Dry-run mode

## Documentation Requirements

Documents to include:

- **README** with:
  - prerequisites
  - export steps for Mail (MBOX export)
  - Messages DB access & Full Disk Access
  - sample usage commands
  - how to use BusyContacts to apply tags/groups
- **SECURITY.md** describing privacy posture
- **CONTRIBUTING.md**
- Duplicate both security and contributing (with names lowercase) in `docsrc/mkdocs/`, and keep these in sync

## Testing & Acceptance Criteria

### Testing Requirements

- Unit tests for parsing, normalization, clustering, and report generation using synthetic fixtures (NO real user data)
- Add a small synthetic example dataset in testing/fixtures

### Acceptance Criteria

- Running "extract-messages" produces a structured JSON listing group chats with participants and basic stats
- Running "extract-mail" produces a structured JSON of email recipient relationships
- "build-graph" merges them and outputs a graph JSON
- "suggest-groups" creates group suggestions JSON + Excel (xlsx) report with suggested tags and groups columns
- "export-vcards" produces vCard(s) and a tag assignment plan
- Tests pass

### Development Workflow

When implementing features, proceed to:

1. Propose the architecture and file tree
2. Implement the code for each file
3. Provide usage examples in README
4. Provide at least one synthetic end-to-end example using fixtures

**Important**: Do NOT use any proprietary APIs by default; LLM integrations must be optional and off by default.

---

For questions or clarifications, refer to the project README or contact the maintainers.
