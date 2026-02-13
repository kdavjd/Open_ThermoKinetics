# CHANGELOG Templates

Patterns and templates for updating CHANGELOG.md

## Format

```markdown
## [Unreleased]

### Added - [Feature/Component]
- [path/to/file1.py](../path/to/file1.py): Description of changes
  - Specific detail 1
  - Specific detail 2

### Changed - [Component]
- [path/to/file2.py](../path/to/file2.py): Description of modification

### Fixed - [Bug]
- [path/to/file3.py](../path/to/file3.py): Description of fix
```

## Entry Types

### Added
New features, new files, new functionality.

```markdown
### Added - ThermoCalc Integration
- [modules/thermocalc/client.py](../modules/thermocalc/client.py): HTTP client for ThermoCalc API
  - Connection pooling with httpx
  - Retry logic for failed requests
  - Health check and calculate methods
- [modules/thermocalc/schemas.py](../modules/thermocalc/schemas.py): Pydantic schemas for API
  - CalculationRequest, CalculationResponse models
  - ValidationError, APIError exceptions
```

### Changed
Modifications to existing functionality.

```markdown
### Changed - Authentication
- [auth/security.py](../auth/security.py): Updated JWT token expiration
  - Changed from 24 hours to 7 days
  - Added refresh token support
- [api/auth.py](../api/auth.py): Enhanced login response
  - Added refresh_token field
  - Updated token format
```

### Fixed
Bug fixes.

```markdown
### Fixed - Database
- [database/base.py](../database/base.py): Fixed async session closing
  - Properly await session.close() in lifespan
  - Resolves connection pool exhaustion
```

### Removed
Deleted features or files.

```markdown
### Removed - Legacy Code
- [services/old_service.py](../services/old_service.py): Removed deprecated service
  - Functionality moved to new_service.py
```

## Link Format

From `.ai/CHANGELOG.md`, use relative paths:

```markdown
- [modules/thermocalc/client.py](../modules/thermocalc/client.py)
```

This resolves to: `c:\IDE\repository\web_portal\modules\thermocalc\client.py`

## Examples by Change Type

### Feature Addition
```markdown
### Added - ThermoCalc Integration
- [modules/thermocalc/router.py](../modules/thermocalc/router.py): API endpoints for ThermoCalc
  - GET /health - health check endpoint
  - POST /calculate - calculation endpoint
- [modules/thermocalc/events.py](../modules/thermocalc/events.py): Domain events
  - CalculationRequestedEvent
  - CalculationCompletedEvent
```

### Refactoring
```markdown
### Changed - Message Bus
- [infrastructure/bus/message_bus.py](../infrastructure/bus/message_bus.py): Refactored event handling
  - Changed from sync to async handlers
  - Added error recovery mechanism
```

### Bug Fix
```markdown
### Fixed - Authentication
- [auth/dependencies.py](../auth/dependencies.py): Fixed role validation
  - Properly check user role in require_role()
  - Return 403 instead of 401 for forbidden access
```

### Documentation
```markdown
### Changed - Documentation
- [README.md](../README.md): Updated installation instructions
  - Added Windows-specific setup notes
  - Clarified dependency requirements
```

## Writing Style

### Be Specific
✅ "Added ThermocalcClient with connection pooling and retry logic"
❌ "Added client"

### Include Impact
✅ "Fixed authentication bug where expired tokens returned 500 instead of 401"
❌ "Fixed auth bug"

### Group Related Changes
✅ Group all ThermoCalc changes under "### Added - ThermoCalc Integration"
❌ Separate entries for each file

## Update Workflow

1. Before committing, edit `.ai/CHANGELOG.md`
2. Add entry under `## [Unreleased]`
3. Group by type (Added/Changed/Fixed)
4. Use relative file links
5. Include specific details in sub-bullets
6. Stage CHANGELOG.md with commit

## Version Release

When releasing a version:

```markdown
## [Unreleased]

### Added - New Feature
- Changes here...

## [1.0.0] - 2025-01-07

### Added - Previous Feature
- Previous changes...
```
