# ArchDebt-Lens: Automated Architectural Technical Debt (ATD) Lifecycle Platform

> **Project by:** Dev Pandya (M26CSE003) & Ayush Pundir (M26CSE001)

Implementation of the complete software platform based on the empirical research:  
> **"Tracing the Lifecycle of Architecture Technical Debt in Software Systems: A Dependency Approach"**  
> *Edi Sutoyo, Paris Avgeriou, Andrea Capiluppi (March 2025)*  
> arXiv: [2501.15387v2](https://arxiv.org/abs/2501.15387) | Replication Package: [Zenodo 14697268](https://doi.org/10.5281/zenodo.14697268)

---

## 🚀 Quick Start

### 1. Activate Environment
```bash
source venv/bin/activate
```

### 2. Run All 20 Unit & Benchmark Tests
```bash
pytest -v tests/
```

### 3. Use the CLI
```bash
# Display version and research attribution
atd-lens version

# Scan a codebase for Java class dependencies and metrics
atd-lens scan --path . --ext .java
```

---

## 📁 Codebase Architecture (Implemented Checkpoint by Checkpoint)

| Checkpoint | Module | Implementation Description | Test Suite |
| :---: | :--- | :--- | :---: |
| **CP 1** | `archdebt_lens.models` | Pydantic v2 schemas (`ATDItem`, `CommitSnapshot`, `FileMetricRecord`, `LifecycleTrace`) and dual SQLite/JSON storage engine. | [`tests/test_checkpoint_1.py`](file:///home/dev-pandya/Desktop/SDE%20Paper/tests/test_checkpoint_1.py) |
| **CP 2** | `archdebt_lens.miner` | Git history excavator & lifecycle tracer (`GitRepoMiner`, `LifecycleTracer`) tracking introduction commits, payment commits, and removed files. | [`tests/test_checkpoint_2.py`](file:///home/dev-pandya/Desktop/SDE%20Paper/tests/test_checkpoint_2.py) |
| **CP 3** | `archdebt_lens.graph` | Multi-language AST parser & directed dependency graph builder (`SourceCodeParser`, `DependencyGraphBuilder`, `MetricsCalculator`) extracting FAN-IN, FAN-OUT, SLOC, and Cyclomatic Complexity. | [`tests/test_checkpoint_3.py`](file:///home/dev-pandya/Desktop/SDE%20Paper/tests/test_checkpoint_3.py) |
| **CP 4** | `archdebt_lens.classifier` | Hybrid ATD Classifier (`NLPATDDetector` + `StructuralATDVerifier` + `HybridATDClassifier`) combining SATD text indicators with graph diffs to eliminate >50% false positives. | [`tests/test_checkpoint_4.py`](file:///home/dev-pandya/Desktop/SDE%20Paper/tests/test_checkpoint_4.py) |
| **CP 5** | `archdebt_lens.stats` | Statistical analytics & Debt Paradox risk engine (`calculate_cliffs_delta`, `calculate_mann_whitney_u`, `partial_spearman_correlation` controlling for SLOC, `DebtParadoxEvaluator`). | [`tests/test_checkpoint_5.py`](file:///home/dev-pandya/Desktop/SDE%20Paper/tests/test_checkpoint_5.py) |
| **CP 6** | `archdebt_lens.cli` & `guardrail` | Production Typer CLI (`atd-lens`) and CI/CD PR Guardrail (`PRGuardrailChecker`) detecting centralization spikes and generating GitHub PR markdown reviews. | [`tests/test_checkpoint_6.py`](file:///home/dev-pandya/Desktop/SDE%20Paper/tests/test_checkpoint_6.py) |
| **CP 7** | `archdebt_lens.ui` | Interactive standalone HTML report generator (`HTMLReportGenerator`) with D3.js force-directed dependency graphs and Code Avoidance scatter heatmaps. | [`tests/test_checkpoint_7.py`](file:///home/dev-pandya/Desktop/SDE%20Paper/tests/test_checkpoint_7.py) |
| **CP 8** | `archdebt_lens.replication` | Replication package dataset & benchmark suite (`ReplicationBenchmark`) replicating Apache Camel case study (`CAMEL-789`), Table III, IV, VII, and VIII. | [`tests/test_checkpoint_8.py`](file:///home/dev-pandya/Desktop/SDE%20Paper/tests/test_checkpoint_8.py) |

---

## 📊 Replicated Empirical Findings

1. **Repayment Paradox (Centralization):** Resolving ATD increases FAN-IN by an average of **+57.5%**, shifting incoming dependencies onto surviving central classes.
2. **Code Avoidance:** ATD files are modified significantly less frequently (**6.98 avg changes** vs. **16.12** for Non-ATD files).
3. **Complexity & Avoidance Correlation:** Partial Spearman correlation between cyclomatic complexity and modification frequency is **negative** in ATD files ($r = -0.089, p < 0.001$), proving developers actively avoid touching complex debt-ridden files.
