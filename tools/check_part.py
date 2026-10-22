#!/usr/bin/env python
"""Deterministic checks for a PythonPart batch (no LLM tokens needed).

Usage: python tools/check_part.py <package_dir> <pyp_file> [--template scriptobject|interactor] [--docs <docs_part_dir>]
Writes <docs>/reports/check.md and pytest.txt, prints a short summary, exits 1 on blocking issues.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ALIASES = {
    "NemAll_Python_AllplanSettings": "Settings",
    "NemAll_Python_ArchElements": "ArchElements",
    "NemAll_Python_BaseElements": "BaseElements",
    "NemAll_Python_BasisElements": "BasisElements",
    "NemAll_Python_Geometry": "Geometry",
    "NemAll_Python_IFW_ElementAdapter": "ElementAdapter",
    "NemAll_Python_IFW_Input": "Input",
    "NemAll_Python_Precast": "Precast",
    "NemAll_Python_Reinforcement": "Reinforcement",
    "NemAll_Python_Utility": "Utility",
}
FRAMEWORK_MODULES = {
    "BuildingElement", "BuildingElementAttributeList", "BuildingElementListService",
    "BuildingElementPaletteService", "ControlPropertiesUtil", "CreateElementResult",
    "PythonPartUtil", "PythonPartTransaction", "PreviewSymbols", "BaseScriptObject",
    "BaseInteractor", "ScriptObjectInteractors", "TypeCollections",
}
SHORT_NAMES = {"x", "res", "tmp", "obj", "val", "data"}
ENTRY_POINTS = {
    "scriptobject": {"check_allplan_version", "create_script_object"},
    "interactor": {"check_allplan_version", "create_preview", "create_interactor"},
}
ASSEMBLY_FILES = {"__init__.py", "main.py"}


class Report:
    def __init__(self) -> None:
        self.blocking: list[str] = []
        self.warnings: list[str] = []

    def block(self, location: str, message: str) -> None:
        self.blocking.append(f"| B{len(self.blocking) + 1} | {location} | {message} |")

    def warn(self, location: str, message: str) -> None:
        self.warnings.append(f"| W{len(self.warnings) + 1} | {location} | {message} |")


def check_python(path: Path, is_assembly: bool, siblings: set[str], report: Report) -> ast.Module | None:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        report.block(f"{path.name}:{error.lineno}", f"SyntaxError: {error.msg}")
        return None
    if not any(isinstance(n, ast.ImportFrom) and n.module == "__future__" for n in tree.body):
        report.block(path.name, "missing `from __future__ import annotations`")
    for node in ast.walk(tree):
        location = f"{path.name}:{getattr(node, 'lineno', 0)}"
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("NemAll_Python_"):
                    if not is_assembly:
                        report.block(location, f"ALLPLAN import in pure-calculation module: {alias.name}")
                    elif ALIASES.get(alias.name) != alias.asname:
                        report.block(location, f"forbidden alias for {alias.name}: {alias.asname} (expected {ALIASES.get(alias.name)})")
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if not is_assembly and root in FRAMEWORK_MODULES:
                report.block(location, f"framework import in pure-calculation module: {node.module}")
            if node.level == 0 and root in siblings:
                report.block(location, f"absolute local import `{node.module}` (use relative import)")
        if isinstance(node, ast.ExceptHandler):
            body_is_silent = all(isinstance(item, (ast.Pass, ast.Continue)) for item in node.body)
            too_broad = node.type is None or (isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"})
            if body_is_silent:
                report.block(location, "silent except")
            elif too_broad:
                report.warn(location, "overly broad except")
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id in SHORT_NAMES:
                    report.warn(location, f"forbidden short name `{target.id}`")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            if ast.get_docstring(node) is None:
                report.warn(location, f"public function `{node.name}` without docstring")
            if node.returns is None and node.name != "__init__":
                report.warn(location, f"public function `{node.name}` without return annotation")
    if not is_assembly and re.search(r"\bbuild_ele\b|NemAll_Python_", source):
        report.block(path.name, "reference to build_ele / NemAll_Python_ in pure-calculation module")
    return tree


def pyp_parameters(pyp: Path, report: Report) -> set[str]:
    raw = pyp.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        report.block(pyp.name, "UTF-8 BOM at start of .pyp (breaks ElementTree: 'invalid token line 1 column 1')")
    if b"\r\n" not in raw:
        report.warn(pyp.name, "line endings are not CRLF")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        report.block(pyp.name, f"invalid XML: {error}")
        return set()
    uuid_node = next((n for n in root.iter() if n.tag.lower() == "uuid"), None)
    if uuid_node is None or not (uuid_node.text or "").strip():
        report.block(pyp.name, "empty or missing <Uuid>")
    names: set[str] = set()
    for parameter in root.iter("Parameter"):
        name_node = parameter.find("Name")
        if name_node is not None and (name_node.text or "").strip():
            names.add(name_node.text.strip())
    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("pyp_file", type=Path)
    parser.add_argument("--template", choices=ENTRY_POINTS, default="scriptobject")
    parser.add_argument("--docs", type=Path, default=None)
    args = parser.parse_args()

    package = args.package_dir
    docs = args.docs or Path(__file__).resolve().parents[1] / "docs" / package.name
    (docs / "reports").mkdir(parents=True, exist_ok=True)
    report = Report()
    sources = [p for p in package.rglob("*.py") if "tests" not in p.parts]
    siblings = {p.stem for p in sources}

    used_parameters: set[str] = set()
    entry_defs: set[str] = set()
    for path in sources:
        is_assembly = path.name in ASSEMBLY_FILES
        tree = check_python(path, is_assembly, siblings, report)
        if tree and is_assembly:
            text = path.read_text(encoding="utf-8")
            used_parameters |= set(re.findall(r"build_ele\.(\w+)", text))
            if path.name == "__init__.py":
                entry_defs |= {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}

    init_defs = entry_defs
    main_path = package / "main.py"
    if main_path.exists():
        main_tree = ast.parse(main_path.read_text(encoding="utf-8"))
        main_defs = {n.name for n in main_tree.body if isinstance(n, ast.FunctionDef)}
        for name in sorted(init_defs & main_defs):
            report.block("__init__.py/main.py", f"function `{name}` defined in both files (template split violated)")
    missing = ENTRY_POINTS[args.template] - entry_defs
    if missing:
        report.block("__init__.py", f"missing framework entry points: {sorted(missing)}")

    placeholder = re.compile(r"__[A-Z][A-Z0-9_]*__")
    language_files = list(args.pyp_file.parent.glob(f"{args.pyp_file.stem}_*.xml"))
    for path in [*sources, args.pyp_file, *language_files]:
        for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            for found in placeholder.findall(line):
                report.block(f"{path.name}:{line_number}", f"unreplaced template placeholder {found}")

    declared = pyp_parameters(args.pyp_file, report)
    for name in sorted(used_parameters - declared):
        report.block(args.pyp_file.name, f"build_ele.{name} not declared in .pyp (case-sensitive)")
    for name in sorted(declared - used_parameters):
        report.warn(args.pyp_file.name, f"parameter `{name}` declared in .pyp but never read by script")

    # cwd and --rootdir scoped to tests/ so pytest never climbs to the package and imports its
    # __init__.py (which needs the ALLPLAN framework, absent from the system Python).
    tests_dir = package / "tests"
    if tests_dir.is_dir():
        pytest_run = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--rootdir", str(tests_dir), "."],
            cwd=str(tests_dir), capture_output=True, text=True)
        (docs / "reports" / "pytest.txt").write_text(pytest_run.stdout + pytest_run.stderr, encoding="utf-8")
        if pytest_run.returncode not in (0, 5):
            report.block("tests/", "pytest failed (see reports/pytest.txt)")
    else:
        (docs / "reports" / "pytest.txt").write_text("no tests directory\n", encoding="utf-8")

    header = "| Id | Location | Finding |\n|---|---|---|\n"
    lines = [f"# check_part — {package.name}", "", f"Blocking: {len(report.blocking)} | Warnings: {len(report.warnings)}", ""]
    lines += ["## Blocking", header + "\n".join(report.blocking or ["| - | - | none |"]), ""]
    lines += ["## Warnings", header + "\n".join(report.warnings or ["| - | - | none |"]), ""]
    (docs / "reports" / "check.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"check_part: {len(report.blocking)} blocking, {len(report.warnings)} warnings -> {docs / 'reports' / 'check.md'}")
    return 1 if report.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
