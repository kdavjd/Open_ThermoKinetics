"""
ContentManager - управление загрузкой и кэшированием контента
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger_config import LoggerManager
from src.gui.user_guide_tab.user_guide_framework.core.exceptions import ContentNotFoundError, GuideFrameworkError

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


@dataclass
class ContentSection:
    """Data class representing a content section"""

    section_id: str
    title: Dict[str, str]
    content: Dict[str, List[Dict[str, Any]]]
    metadata: Dict[str, Any]
    related_sections: List[str]
    attachments: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []


class ContentManager:
    """
    Manages loading, caching, and retrieval of content sections from JSON files.
    Provides centralized content management with caching for performance.
    """

    def __init__(self, data_directory: Path):
        """
        Initialize ContentManager with data directory path.

        Args:
            data_directory: Path to the directory containing content JSON files
        """
        logger.info(f"Initializing ContentManager with data directory: {data_directory}")
        self.data_dir = Path(data_directory)
        self.toc_data: Optional[Dict[str, Any]] = None
        self.content_cache: Dict[str, ContentSection] = {}
        self._metadata_cache: Dict[str, Any] = {}
        self.load_toc()
        logger.debug("ContentManager initialization completed")

    def _count_sections_in_structure(self, structure: Dict[str, Any]) -> int:
        """Count total number of sections in structure"""
        count = 0
        for key, value in structure.items():
            count += 1  # Count the current section
            if isinstance(value, dict) and "children" in value:
                count += self._count_sections_in_structure(value["children"])
        return count

    def load_toc(self) -> None:
        """Load table of contents from toc.json"""
        toc_path = self.data_dir / "toc.json"
        logger.debug(f"Loading table of contents from: {toc_path}")

        if not toc_path.exists():
            logger.error(f"Table of contents not found at {toc_path}")
            raise ContentNotFoundError(f"Table of contents not found at {toc_path}")

        try:
            with open(toc_path, "r", encoding="utf-8") as f:
                self.toc_data = json.load(f)
                # Count sections in structure properly
                structure = self.toc_data.get("structure", {})
                section_count = self._count_sections_in_structure(structure)
                logger.info(f"Successfully loaded table of contents with {section_count} sections")
        except json.JSONDecodeError as e:
            raise GuideFrameworkError(f"Invalid JSON in table of contents: {e}")
        except Exception as e:
            logger.error(f"Failed to load table of contents from {toc_path}: {e}")
            raise GuideFrameworkError(f"Error loading table of contents: {e}")

    def get_section_content(self, section_id: str) -> Optional[ContentSection]:
        """
        Get content for specific section with caching.

        Args:
            section_id: Unique identifier for the content section

        Returns:
            ContentSection object or None if not found
        """
        # Check cache first
        if section_id in self.content_cache:
            return self.content_cache[section_id]

        # Find content file from TOC structure
        content_file = self._find_content_file(section_id)
        if not content_file:
            return None

        # Load content from file
        content_path = self.data_dir / "content" / content_file

        if not content_path.exists():
            logger.warning(f"Content file not found for section: {section_id}")
            return None

        try:
            with open(content_path, "r", encoding="utf-8") as f:
                content_data = json.load(f)

            # Усиленная валидация структуры
            if not isinstance(content_data, dict):
                logger.error(f"Content data for section {section_id} is not a dict: {type(content_data)}")
                return None
            if not isinstance(content_data.get("content", {}), dict):
                logger.error(
                    f"'content' field for section {section_id} is not a dict: {type(content_data.get('content', {}))}"
                )
                return None
            if not isinstance(content_data.get("metadata", {}), dict):
                logger.error(
                    f"'metadata' field for section {section_id} is not a dict: {type(content_data.get('metadata', {}))}"
                )
                return None

            section = ContentSection(
                section_id=content_data.get("section_id", section_id),
                title=content_data.get("metadata", {}).get("title", {}),
                content=content_data.get("content", {}),
                metadata=content_data.get("metadata", {}),
                related_sections=content_data.get("related_sections", []),
                attachments=content_data.get("attachments", []),
            )

            # Cache the section
            self.content_cache[section_id] = section
            return section

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in content file {content_file}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading content file {content_file}: {e}")
            return None

    def get_navigation_structure(self) -> Dict[str, Any]:
        """
        Get hierarchical navigation structure from TOC.

        Returns:
            Dictionary containing the navigation structure
        """
        if not self.toc_data:
            return {}

        return self.toc_data.get("structure", {})

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get framework metadata from TOC.

        Returns:
            Dictionary containing metadata
        """
        if not self.toc_data:
            return {}

        return self.toc_data.get("metadata", {})

    def get_settings(self) -> Dict[str, Any]:
        """
        Get framework settings from TOC.

        Returns:
            Dictionary containing settings
        """
        if not self.toc_data:
            return {}

        return self.toc_data.get("settings", {})

    def search_content(self, query: str, language: str = "ru") -> List[Dict[str, Any]]:
        """
        Search content across all sections.

        Args:
            query: Search query string
            language: Language code for search

        Returns:
            List of search results with section info and matches
        """
        results = []
        query_lower = query.lower()

        # Get all sections from navigation structure
        all_sections = self._get_all_section_ids()

        for section_id in all_sections:
            section = self.get_section_content(section_id)
            if not section:
                continue

            # Search in title
            title = section.title.get(language, "")
            if query_lower in title.lower():
                results.append({"section_id": section_id, "title": title, "match_type": "title", "match_text": title})
                continue

            # Search in content blocks
            content_blocks = section.content.get(language, [])
            for block in content_blocks:
                if self._search_in_block(block, query_lower):
                    results.append(
                        {
                            "section_id": section_id,
                            "title": title,
                            "match_type": "content",
                            "match_text": self._extract_match_text(block, query_lower),
                        }
                    )
                    break  # Only one match per section

        return results

    def _find_content_file(self, section_id: str) -> Optional[str]:
        """Find content file for given section ID in TOC structure"""

        def search_structure(structure: Dict[str, Any]) -> Optional[str]:
            for key, value in structure.items():
                if key == section_id:
                    if isinstance(value, dict):
                        return value.get("content_file")
                    else:
                        logger.warning(f"Section {section_id} value is not a dict: {type(value)}")
                        return None

                if isinstance(value, dict) and "children" in value:
                    result = search_structure(value["children"])
                    if result:
                        return result
            return None

        if not self.toc_data:
            return None

        return search_structure(self.toc_data.get("structure", {}))

    def _get_all_section_ids(self) -> List[str]:
        """Get all section IDs from navigation structure"""
        section_ids = []

        def extract_ids(structure: Dict[str, Any]):
            for key, value in structure.items():
                section_ids.append(key)
                if isinstance(value, dict) and "children" in value:
                    extract_ids(value["children"])

        if self.toc_data:
            extract_ids(self.toc_data.get("structure", {}))

        return section_ids

    def _search_in_block(self, block: Dict[str, Any], query: str) -> bool:
        """Search for query in content block"""
        # Search in text content
        if "text" in block:
            return query in block["text"].lower()

        # Search in list items
        if "items" in block:
            for item in block["items"]:
                if query in str(item).lower():
                    return True

        # Search in code content
        if "code" in block:
            return query in block["code"].lower()

        return False

    def _extract_match_text(self, block: Dict[str, Any], query: str) -> str:
        """Extract relevant text snippet containing the match"""
        if "text" in block:
            text = block["text"]
            # Find the query position and extract surrounding context
            query_pos = text.lower().find(query)
            if query_pos != -1:
                start = max(0, query_pos - 50)
                end = min(len(text), query_pos + len(query) + 50)
                return "..." + text[start:end] + "..."

        return str(block)[:100] + "..." if block else ""

    def clear_cache(self) -> None:
        """Clear the content cache"""
        self.content_cache.clear()
        self._metadata_cache.clear()

    def reload_toc(self) -> None:
        """Reload table of contents and clear cache"""
        self.clear_cache()
        self.load_toc()
