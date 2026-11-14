"""
Pydantic data schemas representing ATD items, Git snapshots,
dependency metrics, and lifecycle traces.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, computed_field


class DebtType(str, Enum):
    VIOMOD = "Violation of Modularity"
    OBSTECH = "Using Obsolete Technology"
    NON_DEBT = "Non-Debt"


class ArtifactSource(str, Enum):
    IS = "Issue Section"
    PS = "Pull Request Section"
    CM = "Commit Message"
    CC = "Code Comment"


class LifecycleStage(str, Enum):
    INTRODUCTION = "introduction"
    INTERMEDIATE = "intermediate"
    PAYMENT = "payment"


class ATDItem(BaseModel):
    """Represents a validated Architectural Technical Debt item."""
    id: str = Field(..., description="Unique identifier (e.g. ATD-1, CAMEL-789)")
    project: str = Field(..., description="Project name (e.g. apache-camel)")
    debt_type: DebtType = Field(default=DebtType.VIOMOD)
    source: ArtifactSource = Field(default=ArtifactSource.IS)
    summary: str = Field(..., description="Summary or title of the debt item")
    description: Optional[str] = Field(default="", description="Detailed issue/commit body")
    payment_commit: Optional[str] = Field(default=None, description="Hash of commit that repaid debt")
    intro_commit: Optional[str] = Field(default=None, description="Hash of commit where debt was introduced")
    is_validated: bool = Field(default=True, description="True positive verified by reviewers")


class CommitSnapshot(BaseModel):
    """Snapshot of a Git commit relevant to ATD tracking."""
    commit_hash: str
    parent_hash: Optional[str] = None
    author: str
    timestamp: datetime
    message: str
    affected_files: List[str] = Field(default_factory=list)


class FileMetricRecord(BaseModel):
    """Static and dependency metrics for an individual file at a given commit."""
    file_path: str
    commit_hash: str
    stage: LifecycleStage
    fan_in: int = Field(ge=0, description="Number of incoming class dependencies")
    fan_out: int = Field(ge=0, description="Number of outgoing class dependencies")
    sloc: int = Field(ge=0, description="Source Lines of Code")
    cyclomatic_complexity: float = Field(ge=0.0, description="Average or total cyclomatic complexity")
    modification_count: int = Field(default=0, ge=0, description="Number of commits touching this file")

    @computed_field
    def fan_in_per_sloc(self) -> float:
        """SLOC-normalized incoming connectivity density."""
        if self.sloc <= 0:
            return 0.0
        return round(self.fan_in / self.sloc, 6)

    @computed_field
    def fan_out_per_sloc(self) -> float:
        """SLOC-normalized outgoing connectivity density."""
        if self.sloc <= 0:
            return 0.0
        return round(self.fan_out / self.sloc, 6)


class LifecycleTrace(BaseModel):
    """Lifecycle trace connecting introduction to payment for an ATD item."""
    atd_id: str
    intro_commit: str
    payment_commit: str
    payment_interval_days: float = Field(ge=0.0)
    files_at_intro: List[str] = Field(default_factory=list)
    files_at_payment: List[str] = Field(default_factory=list)
    files_removed: List[str] = Field(default_factory=list)
    intermediate_commit_count: int = Field(default=0, ge=0)
    metrics_intro: Dict[str, FileMetricRecord] = Field(default_factory=dict)
    metrics_payment: Dict[str, FileMetricRecord] = Field(default_factory=dict)


class CentralizationRisk(BaseModel):
    """Risk evaluation of the 'Debt Paradox' (centralization spike) during payment."""
    target_class: str
    intro_fan_in: int
    payment_fan_in: int
    fan_in_growth_percent: float
    intro_fan_out: int
    payment_fan_out: int
    fan_out_growth_percent: float
    is_paradox_risk: bool
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    recommendation: str
