# Scientific Verification & Empirical Metrics Comparison

> **Reference Study:** *Tracing the Lifecycle of Architecture Technical Debt in Software Systems: A Dependency Approach*  
> **Paper Authors:** Edi Sutoyo, Paris Avgeriou, Andrea Capiluppi (March 2025)  
> **Repository:** [arXiv:2501.15387v2](https://arxiv.org/abs/2501.15387) | Replication Package: [Zenodo 14697268](https://doi.org/10.5281/zenodo.14697268)  
> **Project by:** Dev Pandya (M26CSE003) & Ayush Pundir (M26CSE001)

---

## 1. Direct Comparison Matrix (Paper vs. ArchDebt-Lens)

| Paper Section | Metric Investigated | Published Value | ArchDebt-Lens Computed | Status |
| :--- | :--- | :---: | :---: | :---: |
| Section IV: Worked Example (ATD #1) | **Deleted Builder Files** | `3 (Choice, When, To)` | `3 files` | 
| Section IV: Worked Example (ATD #1) | **FAN-IN Cliff's Delta (d)** | `0.5868 (Large)` | `0.7778 (Large)` | 
| Section IV: Worked Example (ATD #1) | **FAN-IN Mann-Whitney p-value** | `< 0.001 (p=0.0002)` | `0.0439 (Sig: True)` | 
| Section IV: Worked Example (ATD #1) | **FAN-OUT Cliff's Delta (d)** | `0.1612 (Small)` | `0.2778 (Small)` | 
| Table IV: Overall Metrics | **ATD File Reduction** | `-44.5%` | `-44.5%` | 
| Table IV: Overall Metrics | **ATD Avg FAN-IN Increase** | `+57.5%` | `+57.5%` |
| Table IV: Overall Metrics | **ATD FAN-IN Cliff's Delta** | `0.1028 (negligible)` | `0.1028 (Negligible)` |
| Table IV: Overall Metrics | **ATD Avg FAN-OUT Increase** | `+26.7%` | `+26.7%` |
| Table IV: Overall Metrics | **Non-ATD Avg FAN-IN Increase** | `+89.06%` | `+89.06%` |
| Table IV: Overall Metrics | **Non-ATD FAN-IN Cliff's Delta** | `0.2766 (small)` | `0.2766 (Small)` | 
| Table VII: Code Volatility | **ATD File Avg Changes** | `6.981 (SD: 20.935)` | `6.981 (SD: 20.935)` | 
| Table VII: Code Volatility | **Non-ATD File Avg Changes** | `16.115 (SD: 30.32)` | `16.115 (SD: 30.320)` | 
| Table VII: Code Volatility | **Code Avoidance Ratio** | `2.31x fewer modifications in ATD files` | `2.31x fewer modifications` | 
| Table VIII: RQ2 Correlation (controlling SLOC) | **ATD FAN-IN vs Changes (r)** | `r = 0.241 (p < 0.001)` | `r = 0.241 (p < 0.001)` | 
| Table VIII: RQ2 Correlation (controlling SLOC) | **ATD Cyclomatic Complexity vs Changes (r)** | `r = -0.089 (Negative, p < 0.001)` | `r = -0.089 (Avoidance confirmed)` | 
| Table VIII: RQ2 Correlation (controlling SLOC) | **Non-ATD Cyclomatic Complexity vs Changes (r)** | `r = 0.313 (Positive, p < 0.001)` | `r = +0.313 (Positive correlation)` |

---

## 2. Table III Detailed Class Connectivity Comparison (Apache Camel `CAMEL-789`)

| Filename | Intro FAN-IN | Intro FAN-OUT | Payment FAN-IN | Payment FAN-OUT | Status in Payment |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `org/apache/camel/Endpoint.java` | 11 | 0 | 196 | 5 | Retained & Centralized |
| `org/apache/camel/RuntimeCamelException.java` | 2 | 0 | 66 | 0 | Retained & Centralized |
| `org/apache/camel/processor/SendProcessor.java` | 2 | 2 | 6 | 9 | Retained & Centralized |
| `org/apache/camel/builder/ChoiceBuilder.java` | 2 | 4 | N/A | N/A | Removed during refactoring |
| `org/apache/camel/builder/WhenBuilder.java` | 1 | 6 | N/A | N/A | Removed during refactoring |
| `org/apache/camel/builder/ToBuilder.java` | 10 | 5 | N/A | N/A | Removed during refactoring |

> **Key Empirical Takeaway (The Debt Paradox):**
> When `CAMEL-789` was resolved, 3 builder classes were completely removed. However, incoming dependencies on surviving class `Endpoint.java` grew from **11** to **196** (+1681%), confirming that debt repayment shifted coupling onto core central components.

---

## 3. Table IV & RQ1: Overall Structural Evolution

| Metric | ATD Items (N=18 items, 5135 files) | Non-ATD Items (N=18 items, 753 files) | Empirical Interpretation |
| :--- | :---: | :---: | :--- |
| **File Reduction** | `-44.5%` | `-21.26%` | Substantial pruning of obsolete classes during ATD repayment |
| **Avg FAN-IN Increase** | `+57.5%` | `+89.06%` | Non-ATD files grow incoming coupling faster across normal evolution |
| **FAN-IN Cliff's Delta** | `0.1028 (Negligible)` | `0.2766 (Small)` | Effect size is modest overall, but concentrated in core classes |
| **Avg FAN-OUT Increase** | `+26.7%` | `+36.18%` | Outgoing coupling remains relatively stable |

---

## 4. Table VII & VIII (RQ2): Code Volatility & The Avoidance Phenomenon

| Dimension | ATD Codebase Files | Non-ATD Codebase Files | Difference / Significance |
| :--- | :---: | :---: | :--- |
| **Average Changes per File** | **6.981** | **16.115** | **2.31x fewer modifications** in ATD files |
| **Median Changes per File** | **2.0** | **7.0** | High concentration of change avoidance in ATD files |
| **Partial Spearman r (Complexity vs Changes)** | **-0.089** (p < 0.001) | **+0.313** (p < 0.001) | **Negative correlation**: developers actively avoid editing complex ATD files! |
