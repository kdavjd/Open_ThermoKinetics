"""
NavigationManager - управление иерархической структурой навигации
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.core.logger_config import LoggerManager
from src.gui.user_guide_tab.user_guide_framework.core.content_manager import ContentManager
from src.gui.user_guide_tab.user_guide_framework.core.exceptions import NavigationError

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


@dataclass
class NavigationNode:
    """Represents a single node in the navigation tree"""

    section_id: str
    title: Dict[str, str]
    icon: Optional[str] = None
    children: Optional[List["NavigationNode"]] = None
    parent: Optional["NavigationNode"] = None
    content_file: Optional[str] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

    def add_child(self, child: "NavigationNode") -> None:
        """Add a child node and set parent reference"""
        child.parent = self
        self.children.append(child)

    def get_depth(self) -> int:
        """Get the depth of this node in the tree"""
        depth = 0
        current = self.parent
        while current is not None:
            depth += 1
            current = current.parent
        return depth

    def get_root(self) -> "NavigationNode":
        """Get the root node of the tree"""
        current = self
        while current.parent is not None:
            current = current.parent
        return current

    def find_child(self, section_id: str) -> Optional["NavigationNode"]:
        """Find a child node by section ID"""
        for child in self.children:
            if child.section_id == section_id:
                return child
        return None

    def find_descendant(self, section_id: str) -> Optional["NavigationNode"]:
        """Find a descendant node by section ID (recursive search)"""
        # Check direct children first
        child = self.find_child(section_id)
        if child:
            return child

        # Recursively search in children
        for child in self.children:
            result = child.find_descendant(section_id)
            if result:
                return result

        return None


class NavigationManager:
    """
    Manages the hierarchical navigation structure for the user guide.
    Builds and maintains the navigation tree from table of contents data.
    """

    def __init__(self, content_manager: ContentManager):
        """
        Initialize NavigationManager with ContentManager.

        Args:
            content_manager: ContentManager instance for accessing TOC data
        """
        logger.info("Initializing NavigationManager")
        self.content_manager = content_manager
        self.root_nodes: List[NavigationNode] = []
        self.node_map: Dict[str, NavigationNode] = {}
        self._languages: List[str] = []

        try:
            self.build_navigation_tree()
            logger.debug(f"Navigation tree built successfully with {len(self.root_nodes)} root nodes")
        except Exception as e:
            logger.error(f"Failed to build navigation tree: {e}")
            raise

    def build_navigation_tree(self) -> None:
        """Build navigation tree from TOC structure"""
        logger.debug("Building navigation tree from TOC structure")

        structure = self.content_manager.get_navigation_structure()
        metadata = self.content_manager.get_metadata()

        # Get available languages
        self._languages = metadata.get("languages", ["ru", "en"])
        logger.debug(f"Available languages: {self._languages}")

        if not structure:
            logger.error("No navigation structure found in table of contents")
            raise NavigationError("No navigation structure found in table of contents")

        # Clear existing data
        self.root_nodes.clear()
        self.node_map.clear()

        # Build tree from structure
        for section_id, section_data in structure.items():
            root_node = self._build_node(section_id, section_data)
            self.root_nodes.append(root_node)

    def _build_node(
        self, section_id: str, section_data: Dict[str, Any], parent: NavigationNode = None
    ) -> NavigationNode:
        """Recursively build navigation node and its children"""

        # Create the node
        node = NavigationNode(
            section_id=section_id,
            title=section_data.get("title", {section_id: section_id}),
            icon=section_data.get("icon"),
            content_file=section_data.get("content_file"),
            parent=parent,
        )

        # Add to node map for quick lookup
        self.node_map[section_id] = node

        # Build children if they exist
        children_data = section_data.get("children", {})
        for child_id, child_data in children_data.items():
            child_node = self._build_node(child_id, child_data, node)
            node.add_child(child_node)

        return node

    def get_node(self, section_id: str) -> Optional[NavigationNode]:
        """
        Get navigation node by section ID.

        Args:
            section_id: Unique identifier for the section

        Returns:
            NavigationNode or None if not found
        """
        return self.node_map.get(section_id)

    def get_breadcrumb(self, section_id: str) -> List[NavigationNode]:
        """
        Get breadcrumb path for section.

        Args:
            section_id: Section ID to get path for

        Returns:
            List of NavigationNode objects from root to target section
        """
        node = self.get_node(section_id)
        if not node:
            return []

        breadcrumb = []
        current = node
        while current is not None:
            breadcrumb.insert(0, current)
            current = current.parent

        return breadcrumb

    def get_siblings(self, section_id: str) -> List[NavigationNode]:
        """
        Get sibling nodes for given section.

        Args:
            section_id: Section ID to get siblings for

        Returns:
            List of sibling NavigationNode objects
        """
        node = self.get_node(section_id)
        if not node or not node.parent:
            return self.root_nodes  # Return root nodes if no parent

        return node.parent.children

    def get_next_node(self, section_id: str) -> Optional[NavigationNode]:
        """
        Get next node in navigation order.

        Args:
            section_id: Current section ID

        Returns:
            Next NavigationNode or None if at end
        """
        siblings = self.get_siblings(section_id)
        current_node = self.get_node(section_id)

        if not current_node or not siblings:
            return None

        try:
            current_index = siblings.index(current_node)
            if current_index + 1 < len(siblings):
                return siblings[current_index + 1]
        except ValueError:
            pass

        return None

    def get_previous_node(self, section_id: str) -> Optional[NavigationNode]:
        """
        Get previous node in navigation order.

        Args:
            section_id: Current section ID

        Returns:
            Previous NavigationNode or None if at beginning
        """
        siblings = self.get_siblings(section_id)
        current_node = self.get_node(section_id)

        if not current_node or not siblings:
            return None

        try:
            current_index = siblings.index(current_node)
            if current_index > 0:
                return siblings[current_index - 1]
        except ValueError:
            pass

        return None

    def search_nodes(self, query: str, language: str = "ru") -> List[NavigationNode]:
        """
        Search navigation nodes by title.

        Args:
            query: Search query
            language: Language code for search

        Returns:
            List of matching NavigationNode objects
        """
        results = []
        query_lower = query.lower()

        for node in self.node_map.values():
            title = node.title.get(language, "")
            if query_lower in title.lower():
                results.append(node)

        return results

    def get_all_sections(self) -> List[str]:
        """
        Get all section IDs in the navigation tree.

        Returns:
            List of all section IDs
        """
        return list(self.node_map.keys())

    def get_flat_structure(self, language: str = "ru") -> List[Dict[str, Any]]:
        """
        Get flattened navigation structure for UI purposes.

        Args:
            language: Language code for titles

        Returns:
            List of dictionaries with node info and hierarchy
        """
        structure = []

        def flatten_node(node: NavigationNode, depth: int = 0):
            structure.append(
                {
                    "section_id": node.section_id,
                    "title": node.title.get(language, node.section_id),
                    "depth": depth,
                    "icon": node.icon,
                    "has_children": len(node.children) > 0,
                    "content_file": node.content_file,
                }
            )

            for child in node.children:
                flatten_node(child, depth + 1)

        for root_node in self.root_nodes:
            flatten_node(root_node)

        return structure

    def validate_structure(self) -> List[str]:
        """
        Validate navigation structure for consistency.

        Returns:
            List of validation error messages
        """
        errors = []

        # Check for orphaned nodes
        for section_id, node in self.node_map.items():
            if node.parent is None and node not in self.root_nodes:
                errors.append(f"Orphaned node found: {section_id}")

        # Check for missing content files
        for section_id, node in self.node_map.items():
            if node.content_file:
                # This would need ContentManager to verify file existence
                pass

        # Check for duplicate section IDs (should not happen with dict)
        section_ids = list(self.node_map.keys())
        if len(section_ids) != len(set(section_ids)):
            errors.append("Duplicate section IDs found")

        # Check for missing titles in required languages
        for section_id, node in self.node_map.items():
            for lang in self._languages:
                if lang not in node.title:
                    errors.append(f"Missing title for section {section_id} in language {lang}")

        return errors

    def get_tree_info(self) -> Dict[str, Any]:
        """
        Get information about the navigation tree.

        Returns:
            Dictionary with tree statistics
        """
        total_nodes = len(self.node_map)
        root_count = len(self.root_nodes)
        max_depth = 0

        for node in self.node_map.values():
            depth = node.get_depth()
            max_depth = max(max_depth, depth)

        return {
            "total_nodes": total_nodes,
            "root_nodes": root_count,
            "max_depth": max_depth,
            "languages": self._languages,
        }

    def get_navigation_structure(self, language: str = "ru") -> List[NavigationNode]:
        """
        Get navigation structure as a list of root nodes.

        Args:
            language: Language code (used for compatibility, but not filtering here)

        Returns:
            List of root NavigationNode objects
        """
        return self.root_nodes

    def rebuild_tree(self) -> None:
        """Rebuild the navigation tree from current content manager data"""
        self.build_navigation_tree()
