# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added - Claude Configuration Refactor
- [CLAUDE.md](../CLAUDE.md): Complete rewrite for PyQt6 desktop application architecture
  - Signal-slot communication patterns (BaseSignals/BaseSlots)
  - 4-panel adaptive layout (MainTab)
  - Scientific visualization with matplotlib
  - Calculation modules: deconvolution, model-fit, model-free, model-based

- [.ai/ARCHITECTURE.md](../.ai/ARCHITECTURE.md): Application architecture documentation
  - Core modules structure (src/gui/, src/core/)
  - Request-Response pattern implementation
  - Data flow diagrams
  - Calculation orchestration

- [.ai/UI_ARCHITECTURE.md](../.ai/UI_ARCHITECTURE.md): GUI architecture documentation
  - MainWindow and tab structure
  - Sidebar navigation with QTreeView
  - SubSideHub dynamic content switching
  - Interactive matplotlib canvas with draggable anchors

- [.ai/DATA_MODELS.md](../.ai/DATA_MODELS.md): Data structures documentation
  - FileData: experimental data management
  - CalculationsData: reaction configurations with path_keys
  - SeriesData: multi-heating-rate experiments
  - Data operation flows

- [.claude/skills/gui-testing/](../.claude/skills/gui-testing/): New skill for PyQt6 testing
  - pytest + pytest-qt integration
  - Test patterns for Qt widgets
  - CI/CD with pytest-xvfb for headless testing

### Changed
- [CLAUDE.md](../CLAUDE.md): Removed web_portal references, added PyQt6 architecture
- [.claude/skills/spec-implementer/](../.claude/skills/spec-implementer/SKILL.md): Updated next_skill to gui-testing
- [.claude/skills/merge-helper/](../.claude/skills/merge-helper/SKILL.md): Replaced Playwright with pytest-qt
- [.claude/skills/spec-creation/](../.claude/skills/spec-creation/SKILL.md): Updated workflow references

### Removed
- `.claude/skills/parallel-mode/`: Simplified workflow (removed alternative implementation mode)
- `.claude/skills/web-portal-testing/`: Replaced with gui-testing skill
