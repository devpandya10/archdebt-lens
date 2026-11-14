"""
Directed dependency graph builder for software classes and files.
Constructs NetworkX DiGraph and resolves symbol bindings.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import networkx as nx
from archdebt_lens.graph.parser import ParsedCodeEntity, SourceCodeParser


class DependencyGraphBuilder:
    """Builds and analyzes a directed class/file dependency graph."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.entities: Dict[str, ParsedCodeEntity] = {}
        self.class_to_file: Dict[str, str] = {}

    def add_file(self, file_path: str, content: Optional[str] = None):
        """Parses and registers a file in the dependency graph."""
        entity = SourceCodeParser.parse_file(file_path, content=content)
        norm_path = str(Path(file_path))
        self.entities[norm_path] = entity
        self.graph.add_node(
            norm_path,
            classes=list(entity.declared_classes),
            sloc=entity.sloc,
            complexity=entity.cyclomatic_complexity,
        )

        for cls_name in entity.declared_classes:
            self.class_to_file[cls_name] = norm_path
            if entity.package_name:
                fqn = f"{entity.package_name}.{cls_name}"
                self.class_to_file[fqn] = norm_path

    def build_edges(self):
        """Resolves dependencies between files based on imports and symbol references."""
        for src_path, entity in self.entities.items():
            targets: Set[str] = set()

            # 1. Resolve direct imports
            for imp in entity.imports:
                for cls_name, dst_path in self.class_to_file.items():
                    if dst_path != src_path and (imp == cls_name or imp.endswith(f".{cls_name}")):
                        targets.add(dst_path)

            # 2. Resolve referenced types
            for ref in entity.referenced_types:
                if ref in self.class_to_file:
                    dst_path = self.class_to_file[ref]
                    if dst_path != src_path:
                        targets.add(dst_path)

            # Add directed edges: src depends on dst
            for target in targets:
                self.graph.add_edge(src_path, target)

    def get_fan_in(self, file_path: str) -> int:
        """FAN-IN: Number of incoming dependencies (other files that depend on this file)."""
        norm_path = str(Path(file_path))
        if norm_path not in self.graph:
            return 0
        return self.graph.in_degree(norm_path)

    def get_fan_out(self, file_path: str) -> int:
        """FAN-OUT: Number of outgoing dependencies (other files this file depends on)."""
        norm_path = str(Path(file_path))
        if norm_path not in self.graph:
            return 0
        return self.graph.out_degree(norm_path)

    def detect_cycles(self) -> List[List[str]]:
        """Finds circular dependency cycles across files."""
        try:
            return list(nx.simple_cycles(self.graph))
        except Exception:
            return []
