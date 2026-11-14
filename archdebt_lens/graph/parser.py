"""
Source code parser for dependency and symbol extraction.
Supports Java and Python source code.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ParsedCodeEntity:
    """Represents symbols declared and referenced in a single source file."""

    def __init__(self, file_path: str, package_name: str = ""):
        self.file_path = file_path
        self.package_name = package_name
        self.declared_classes: Set[str] = set()
        self.imports: Set[str] = set()
        self.referenced_types: Set[str] = set()
        self.sloc: int = 0
        self.cyclomatic_complexity: int = 1


class SourceCodeParser:
    """Parses Java and Python files to extract dependency relationships and complexity."""

    JAVA_CLASS_PATTERN = re.compile(r'\b(?:class|interface|enum)\s+([A-Za-z0-9_]+)')
    JAVA_PACKAGE_PATTERN = re.compile(r'^\s*package\s+([A-Za-z0-9_.]+);', re.MULTILINE)
    JAVA_IMPORT_PATTERN = re.compile(r'^\s*import\s+(?:static\s+)?([A-Za-z0-9_.*]+);', re.MULTILINE)
    JAVA_TYPE_USAGE_PATTERN = re.compile(r'\b(?:new\s+)?([A-Z][A-Za-z0-9_]+)\b')
    JAVA_BRANCH_PATTERN = re.compile(r'\b(if|for|while|case|catch|\?\s*.*:)\b|(&&|\|\|)')

    @classmethod
    def parse_file(cls, file_path: str, content: Optional_str = None) -> ParsedCodeEntity:
        """Parses a file from path or raw string content."""
        p = Path(file_path)
        if content is None:
            if not p.exists():
                return ParsedCodeEntity(file_path=file_path)
            content = p.read_text(encoding="utf-8", errors="ignore")

        if p.suffix == ".java":
            return cls.parse_java(file_path, content)
        elif p.suffix == ".py":
            return cls.parse_python(file_path, content)
        else:
            return cls._parse_generic(file_path, content)

    @classmethod
    def parse_java(cls, file_path: str, content: str) -> ParsedCodeEntity:
        pkg_match = cls.JAVA_PACKAGE_PATTERN.search(content)
        package_name = pkg_match.group(1) if pkg_match else ""

        entity = ParsedCodeEntity(file_path=file_path, package_name=package_name)

        # Declared classes
        for match in cls.JAVA_CLASS_PATTERN.finditer(content):
            entity.declared_classes.add(match.group(1))

        # Imports
        for match in cls.JAVA_IMPORT_PATTERN.finditer(content):
            entity.imports.add(match.group(1))

        # Referenced types (excluding primitives and common keywords)
        keywords = {
            "String", "Object", "Integer", "Boolean", "Long", "Double",
            "Exception", "Throwable", "Override", "Deprecated", "SuppressWarnings"
        }
        for match in cls.JAVA_TYPE_USAGE_PATTERN.finditer(content):
            token = match.group(1)
            if token not in keywords and token not in entity.declared_classes:
                entity.referenced_types.add(token)

        # SLOC
        lines = [line.strip() for line in content.splitlines()]
        sloc_lines = [
            l for l in lines
            if l and not l.startswith("//") and not l.startswith("/*") and not l.startswith("*")
        ]
        entity.sloc = max(1, len(sloc_lines))

        # Cyclomatic complexity: 1 + number of branch predicates
        branches = len(cls.JAVA_BRANCH_PATTERN.findall(content))
        entity.cyclomatic_complexity = 1 + branches

        return entity

    @classmethod
    def parse_python(cls, file_path: str, content: str) -> ParsedCodeEntity:
        entity = ParsedCodeEntity(file_path=file_path)

        lines = [line.strip() for line in content.splitlines()]
        entity.sloc = max(1, len([l for l in lines if l and not l.startswith("#")]))

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            entity.cyclomatic_complexity = 1
            return entity

        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.ClassDef):
                entity.declared_classes.add(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    entity.imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    entity.imports.add(f"{mod}.{alias.name}" if mod else alias.name)
            elif isinstance(node, ast.Name):
                if node.id and node.id[0].isupper():
                    entity.referenced_types.add(node.id)

        entity.cyclomatic_complexity = complexity
        return entity

    @classmethod
    def _parse_generic(cls, file_path: str, content: str) -> ParsedCodeEntity:
        entity = ParsedCodeEntity(file_path=file_path)
        lines = [line.strip() for line in content.splitlines()]
        entity.sloc = max(1, len([l for l in lines if l]))
        entity.cyclomatic_complexity = 1
        return entity
