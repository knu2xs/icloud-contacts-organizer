---
title: Development Plan
---

# Project Development Plan

## Overview

This document outlines the comprehensive development plan for the iCloud
Contacts Organizer project—a privacy-first, semi-assisted workflow for
organizing macOS contacts using communication data from Messages and Mail.

!!! note "Project Philosophy"
    This project prioritizes user privacy by extracting only metadata
    (participants, counts, recency) and never requiring message bodies
    unless explicitly enabled by the user.

## Project Phases

### Phase 1: Foundation & Core Infrastructure

#### 1.1 Project Setup ✓

- [x] Initialize project structure with proper directory hierarchy
- [x] Configure Python package (`src/icloud_contacts_organizer/`)
- [x] Set up configuration management (`config/config.yml`, `config/secrets.yml`)
- [x] Establish testing framework structure
- [x] Configure MkDocs documentation system

#### 1.2 Core Utilities

- [ ] Implement module-level logging system (`get_logger` function)
- [ ] Create configuration loader with YAML support
- [ ] Build CLI framework using argparse
- [ ] Establish error handling patterns and custom exceptions
- [ ] Create data validation schemas using Pydantic

**Deliverables:**

- Working logging system throughout codebase
- Configuration management with secrets handling
- CLI entry point with help text
- Base exception classes

### Phase 2: Data Extraction Layer

#### 2.1 Messages Extraction

**Priority: High** - Focus on group chats first

- [ ] Implement SQLite connection to `~/Library/Messages/chat.db`
- [ ] Create schema introspection for database compatibility
- [ ] Build query templates for:
  - Group chat identification
  - Participant handle extraction
  - Message count aggregation
  - Last activity timestamps
- [ ] Develop data normalization pipeline
- [ ] Add alternative extraction using imessage-exporter tool
- [ ] Implement privacy-mode filters (metadata only)

**Technical Requirements:**

- Handle Full Disk Access permissions detection
- Provide clear user guidance for permission setup
- Stream data to avoid memory issues with large histories
- Store extracted data in `data/interim/messages/`

**CLI Command:**

``` bash
python -m icloud_contacts_organizer extract-messages \
    --output data/interim/messages/extracted.json \
    --privacy-mode
```

#### 2.2 Mail Extraction

- [ ] Implement MBOX parser using Python's `mailbox` module
- [ ] Extract email headers (From, To, Cc, Bcc)
- [ ] Parse and tokenize subject lines
- [ ] Normalize email addresses and domains
- [ ] Build relationship frequency tracking
- [ ] Store extracted data in `data/interim/mail/`

**Technical Requirements:**

- Support both individual .mbox files and packages
- Handle malformed emails gracefully
- Extract only metadata in privacy-mode (default)
- Document Mail export process from Apple Mail

**CLI Command:**

``` bash
python -m icloud_contacts_organizer extract-mail \
    --mbox-path ~/Mail/Exports/AllMail.mbox \
    --output data/interim/mail/extracted.json
```

#### 2.3 Contacts Export & Parsing

- [ ] Create user guidance for exporting Contacts as vCard
- [ ] Implement vCard (.vcf) parser
- [ ] Extract contact identities:
  - Display names
  - Email addresses (all)
  - Phone numbers (all)
  - Groups/tags
- [ ] Normalize contact data to internal schema
- [ ] Store parsed contacts in `data/interim/contacts/`

**CLI Command:**

``` bash
python -m icloud_contacts_organizer export-contacts \
    --vcard-path ~/Desktop/MyContacts.vcf \
    --output data/interim/contacts/existing.json
```

**Deliverables:**

- Three extraction commands working end-to-end
- JSON structured outputs for each data source
- Clear documentation with macOS permission requirements
- Privacy-mode enabled by default

### Phase 3: Identity Resolution & Graph Building

#### 3.1 Identity Normalization

- [ ] Implement email address normalization (lowercase, strip whitespace)
- [ ] Build phone number normalization (E.164-ish format)
- [ ] Create domain extraction for organizational grouping
- [ ] Develop handle-to-identity mapping
- [ ] Implement identity deduplication logic

**Data Model:**

``` python
class PersonIdentity(BaseModel):
    """Unified person identity across data sources."""
    emails: list[str] = []
    phones: list[str] = []
    display_name: str | None = None
    sources: list[str] = []  # messages, mail, contacts
    contact_exists: bool = False
```

#### 3.2 Relationship Graph Construction

- [ ] Design graph schema in DuckDB:
  - Nodes: PersonIdentity records
  - Edges: RelationshipEdge records with weights
- [ ] Implement graph builder from multiple sources
- [ ] Calculate edge weights from:
  - Message frequency
  - Email co-occurrence
  - Thread/group participation
  - Recency of interaction
- [ ] Create graph export formats (JSON, GraphML)

**Data Model:**

``` python
class RelationshipEdge(BaseModel):
    """Weighted relationship between two identities."""
    person_a: str  # identifier
    person_b: str  # identifier
    weight: float
    sources: dict[str, dict]  # {"messages": {"count": 45}, "mail": {...}}
    last_interaction: datetime | None = None
```

#### 3.3 Thread & Group Tracking

- [ ] Implement thread/group chat entity model
- [ ] Track multi-person participation patterns
- [ ] Calculate group cohesion metrics
- [ ] Identify frequent group configurations

**Data Model:**

``` python
class Thread(BaseModel):
    """Communication thread or group chat."""
    id: str
    participants: list[str]  # identity references
    last_activity: datetime
    message_count: int
    source: str  # messages, mail
```

**CLI Command:**

``` bash
python -m icloud_contacts_organizer build-graph \
    --messages data/interim/messages/extracted.json \
    --mail data/interim/mail/extracted.json \
    --contacts data/interim/contacts/existing.json \
    --output data/processed/graph.json
```

**Deliverables:**

- Unified identity resolution system
- Weighted relationship graph in DuckDB
- Thread/group participation tracking
- Graph visualization capabilities

### Phase 4: Intelligent Grouping & Suggestions

#### 4.1 Clustering Implementation

- [ ] Implement deterministic clustering algorithms:
  - Connected components analysis
  - Community detection (Louvain-like)
  - Frequency-based grouping
- [ ] Calculate cluster cohesion scores
- [ ] Generate grouping candidates with confidence levels
- [ ] Create heuristic naming system (domain-based, frequency-based)

#### 4.2 LLM Integration Framework

**Architecture:** Pluggable provider interface

- [ ] Define `LLMProvider` abstract base class
- [ ] Implement OpenAI-compatible provider
- [ ] Implement local model HTTP endpoint provider
- [ ] Create no-LLM fallback mode (deterministic only)
- [ ] Build prompt templates with minimal data exposure
- [ ] Implement response parsing and validation

**Privacy Requirements:**

- Default: send only participant counts, frequency, domain keywords
- Never send message bodies unless `--llm-full-context` is explicitly set
- Support local LLM to avoid cloud transmission

**LLM Provider Interface:**

``` python
class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    async def suggest_group_name(
        self,
        participants: list[str],
        signals: dict[str, Any]
    ) -> GroupSuggestion:
        """Generate group name and rationale from participant data."""
        pass
```

#### 4.3 Group Suggestion System

- [ ] Combine clustering + LLM suggestions
- [ ] Generate confidence scores
- [ ] Create rationale explanations using source signals
- [ ] Identify missing contacts (high-value, frequent communication)
- [ ] Suggest tags for individual contacts

**Data Model:**

``` python
class GroupSuggestion(BaseModel):
    """AI-generated group suggestion."""
    name: str
    members: list[str]  # identity references
    confidence: float  # 0.0 to 1.0
    rationale: str
    source_signals: dict[str, Any]
    suggested_tags: list[str] = []
```

**CLI Command:**

``` bash
python -m icloud_contacts_organizer suggest-groups \
    --graph data/processed/graph.json \
    --llm-provider openai \
    --output data/processed/suggestions.json \
    --privacy-mode
```

**Deliverables:**

- Working clustering with multiple algorithms
- Pluggable LLM provider system
- Group suggestions with confidence and rationale
- No-LLM fallback mode

### Phase 5: Semi-Assisted Review System

#### 5.1 Excel Report Generation

**Primary Review Interface:** Human-editable Excel workbook

- [ ] Design Excel schema with columns:
  - Contact Name
  - Contact Status (exists/missing)
  - Suggested Tags (comma-separated)
  - Suggested Groups (comma-separated)
  - Confidence Score
  - Rationale
  - Email Address(es)
  - Phone Number(s)
  - Interaction Frequency
  - Last Interaction Date
  - Source Signals Summary
- [ ] Implement Excel generation using openpyxl
- [ ] Add conditional formatting for confidence levels
- [ ] Create filtering and sorting capabilities
- [ ] Include a summary sheet with statistics

**Technical Requirements:**

- Support large datasets (thousands of contacts)
- Format for easy review (color coding, filters)
- Allow manual edits to tags and groups
- Export to `.xlsx` format

#### 5.2 Review Workflow

- [ ] Generate review workbook with suggestions
- [ ] Provide instructions for manual review
- [ ] Implement confirmation parser (read edited Excel)
- [ ] Validate user changes
- [ ] Create "apply plan" from confirmed changes

**CLI Command:**

``` bash
python -m icloud_contacts_organizer report \
    --suggestions data/processed/suggestions.json \
    --contacts data/interim/contacts/existing.json \
    --output reports/review-$(date +%Y%m%d).xlsx
```

**Deliverables:**

- Excel report generator
- Review workflow documentation
- Apply plan creation system

### Phase 6: Export & Application

#### 6.1 vCard Export

- [ ] Implement vCard (.vcf) generator
- [ ] Support vCard 3.0 and 4.0 formats
- [ ] Add suggested tags to NOTES field
- [ ] Create group membership encoding
- [ ] Generate individual and combined vCard files
- [ ] Document BusyContacts import process

**Technical Requirements:**

- Generate valid vCard format
- Include all contact details
- Preserve existing data when updating
- Support batch exports

#### 6.2 Tag/Group Assignment Plan

- [ ] Create YAML apply plan format
- [ ] Generate instructions for BusyContacts tagging
- [ ] Document tags-to-iCloud-Groups mapping
- [ ] Provide step-by-step application guide
- [ ] Create verification checklist

**Apply Plan Format:**

``` yaml
groups:
  - name: "Family"
    contacts:
      - email: person1@example.com
      - phone: "+15555551234"
  - name: "Work - Engineering Team"
    contacts:
      - email: person2@example.com

tags:
  - name: "Frequent Contact"
    contacts:
      - email: person1@example.com
```

#### 6.3 BusyContacts Integration

- [ ] Document BusyContacts tag creation
- [ ] Explain tags→iCloud Groups mapping
- [ ] Provide import workflow instructions
- [ ] Create verification steps
- [ ] Document troubleshooting

**CLI Commands:**

``` bash
# Export vCards
python -m icloud_contacts_organizer export-vcards \
    --apply-plan data/processed/apply_plan.yml \
    --output data/exports/contacts/

# Export individual group vCards
python -m icloud_contacts_organizer export-vcards \
    --apply-plan data/processed/apply_plan.yml \
    --output data/exports/contacts/ \
    --separate-groups
```

**Deliverables:**

- vCard generation system
- YAML apply plan format
- BusyContacts integration guide
- Complete export workflow

### Phase 7: Testing & Quality Assurance

#### 7.1 Unit Testing

- [ ] Create synthetic test fixtures (no real user data)
- [ ] Test data extraction modules
- [ ] Test normalization functions
- [ ] Test graph building logic
- [ ] Test clustering algorithms
- [ ] Test LLM provider interfaces
- [ ] Test report generation
- [ ] Test vCard export

**Target:** 80%+ code coverage

#### 7.2 Integration Testing

- [ ] Create end-to-end test with synthetic data
- [ ] Test full pipeline from extraction to export
- [ ] Test CLI command interactions
- [ ] Test configuration loading
- [ ] Test error handling and recovery

#### 7.3 Privacy & Security Testing

- [ ] Verify privacy-mode default behavior
- [ ] Ensure no message bodies extracted by default
- [ ] Test secrets management
- [ ] Verify log redaction
- [ ] Review data retention policies

**Deliverables:**

- Comprehensive test suite in `testing/`
- Synthetic fixtures in `testing/fixtures/`
- CI/CD pipeline (optional)
- Test coverage > 80%

### Phase 8: Documentation

#### 8.1 User Documentation

- [ ] Write comprehensive README.md
- [ ] Create getting started guide
- [ ] Document macOS permissions setup (Full Disk Access)
- [ ] Document Mail export process
- [ ] Document Contacts export process
- [ ] Create CLI command reference
- [ ] Add troubleshooting guide
- [ ] Include BusyContacts usage guide

#### 8.2 Technical Documentation

- [ ] Document architecture and design decisions
- [ ] Create API reference
- [ ] Document data models and schemas
- [ ] Explain clustering algorithms
- [ ] Document LLM integration points
- [ ] Create development guide (AGENTS.md) ✓

#### 8.3 Security & Privacy Documentation

- [ ] Create SECURITY.md
- [ ] Document privacy-first approach
- [ ] Explain data handling practices
- [ ] List data retention policies
- [ ] Document LLM data exposure

#### 8.4 Contributing Guide

- [ ] Create CONTRIBUTING.md
- [ ] Document code style requirements
- [ ] Explain testing requirements
- [ ] Provide PR guidelines
- [ ] List development setup

**Deliverables:**

- Complete MkDocs documentation site
- README with quick start
- SECURITY.md and CONTRIBUTING.md
- API reference

## Development Milestones

### Milestone 1: MVP - Basic Extraction (Weeks 1-2)

- Messages extraction working
- Basic CLI framework
- Simple JSON output
- Documentation for permissions

**Success Criteria:**

- Can extract group chat participants from chat.db
- Produces structured JSON output
- Clear permission setup guide

### Milestone 2: Multi-Source Integration (Weeks 3-4)

- Mail extraction working
- Contacts parsing complete
- Identity resolution implemented
- Graph building functional

**Success Criteria:**

- Unified graph from all three data sources
- Identity deduplication working
- DuckDB integration complete

### Milestone 3: Intelligent Suggestions (Weeks 5-6)

- Clustering algorithms implemented
- LLM integration framework complete
- Group suggestions with rationale
- Excel report generation

**Success Criteria:**

- Generates reasonable group suggestions
- LLM naming produces useful results
- Excel report is human-reviewable

### Milestone 4: Export & Application (Week 7)

- vCard export working
- Apply plan format finalized
- BusyContacts documentation complete

**Success Criteria:**

- Generated vCards import successfully
- Tags can be applied in BusyContacts
- Clear application workflow

### Milestone 5: Polish & Release (Week 8)

- Complete test coverage
- Documentation finalized
- Error handling robust
- Ready for user testing

**Success Criteria:**

- Tests pass with >80% coverage
- End-to-end workflow documented
- Security review complete

## Technical Architecture

### Core Components

``` mermaid
graph TB
    CLI[CLI Entry Point] --> Extract[Data Extraction Layer]
    Extract --> Messages[Messages Extractor]
    Extract --> Mail[Mail Extractor]
    Extract --> Contacts[Contacts Parser]
    
    Messages --> Identity[Identity Resolution]
    Mail --> Identity
    Contacts --> Identity
    
    Identity --> Graph[Graph Builder]
    Graph --> DuckDB[(DuckDB)]
    
    Graph --> Cluster[Clustering Engine]
    Cluster --> LLM[LLM Provider]
    
    LLM --> Suggest[Group Suggestions]
    Suggest --> Report[Excel Report Generator]
    
    Report --> Review{Human Review}
    Review --> ApplyPlan[Apply Plan Generator]
    
    ApplyPlan --> VCard[vCard Exporter]
    VCard --> BusyContacts[BusyContacts]
```

### Data Flow

1. **Extraction**: Raw data → Interim JSON files
2. **Resolution**: Interim data → Unified identities
3. **Graph**: Identities → Relationship graph (DuckDB)
4. **Clustering**: Graph → Group candidates
5. **LLM**: Candidates → Named suggestions + rationale
6. **Report**: Suggestions → Excel workbook
7. **Review**: Human edits → Confirmed plan
8. **Export**: Confirmed plan → vCards + instructions

### Technology Stack

- **Language:** Python 3.11+
- **Data Processing:** DuckDB (primary), Pandas (reporting)
- **Parsing:** sqlite3, mailbox, email, vobject/vcard
- **Schemas:** Pydantic
- **Configuration:** PyYAML
- **Reporting:** openpyxl or xlsxwriter
- **CLI:** argparse
- **Testing:** pytest
- **Documentation:** MkDocs with Material theme

## Risk Management

### Privacy Risks

**Risk:** Accidental exposure of message content

**Mitigation:**

- Privacy-mode enabled by default
- Extract metadata only
- Clear documentation about data handling
- LLM prompt verification

### Performance Risks

**Risk:** Large message histories cause memory issues

**Mitigation:**

- Stream data processing
- Use DuckDB for large dataset operations
- Implement pagination/chunking
- Provide progress indicators

### Compatibility Risks

**Risk:** macOS Messages database schema changes

**Mitigation:**

- Implement schema introspection
- Version detection
- Graceful degradation
- Alternative extraction methods (imessage-exporter)

### User Experience Risks

**Risk:** Complex workflow confuses users

**Mitigation:**

- Clear step-by-step documentation
- Rich CLI help text
- Example workflows
- Dry-run mode for verification

## Success Metrics

### Functional Metrics

- [ ] Successfully extracts data from Messages and Mail
- [ ] Identifies 90%+ of existing contacts
- [ ] Suggests useful groups with clear rationale
- [ ] Exports valid vCards that import correctly

### Quality Metrics

- [ ] Test coverage > 80%
- [ ] Zero real user data in tests or examples
- [ ] All CLI commands have comprehensive help
- [ ] Documentation covers all major use cases

### Privacy Metrics

- [ ] Privacy-mode is default
- [ ] No message bodies in logs
- [ ] Identifiers hashed in logs
- [ ] Clear data handling documentation

## Next Steps

### Immediate Actions

1. **Read AGENTS.md** for detailed coding standards
2. **Set up development environment** with Python 3.11+
3. **Create core utilities** (logging, config, CLI framework)
4. **Begin Phase 2** with Messages extraction

### Regular Activities

- **Daily:** Commit code with clear messages
- **Weekly:** Review progress against milestones
- **Per Phase:** Update documentation
- **Per Feature:** Write tests first (TDD)

### Communication

- Use GitHub issues for feature tracking
- Document design decisions in commit messages
- Update this plan as requirements evolve

---

!!! tip "Getting Started"
    Begin by setting up the core logging and configuration utilities, then
    proceed to Phase 2 (Messages Extraction) as this provides the most value
    and is the foundation for other features.

!!! warning "Privacy First"
    Remember: privacy-mode should be the default for all operations. Never
    extract message bodies unless explicitly requested with
    `--llm-full-context` flag.
