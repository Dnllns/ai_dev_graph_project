"""Waterfall stage tracking system for continuous development.

This module manages the state of features through the waterfall stages,
ensuring no stage is skipped and progress is tracked.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel


class WaterfallStage(str, Enum):
    """Waterfall development stages."""

    ANALYSIS = "analysis"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    RELEASE = "release"
    COMPLETED = "completed"


# Stage order for validation
STAGE_ORDER = [
    WaterfallStage.ANALYSIS,
    WaterfallStage.DESIGN,
    WaterfallStage.IMPLEMENTATION,
    WaterfallStage.TESTING,
    WaterfallStage.DOCUMENTATION,
    WaterfallStage.RELEASE,
    WaterfallStage.COMPLETED,
]


class FeatureProgress(BaseModel):
    """Track progress of a feature through waterfall stages."""

    feature_id: str
    title: str
    current_stage: WaterfallStage
    started_at: str
    updated_at: str
    stage_history: List[Dict[str, str]] = []
    notes: str = ""

    def advance_stage(self) -> bool:
        """Advance to the next stage if possible.

        Returns:
            True if advanced successfully.
        """
        current_idx = STAGE_ORDER.index(self.current_stage)
        if current_idx < len(STAGE_ORDER) - 1:
            # Record stage completion
            self.stage_history.append(
                {
                    "stage": self.current_stage.value,
                    "completed_at": datetime.now().isoformat(),
                }
            )

            # Advance
            self.current_stage = STAGE_ORDER[current_idx + 1]
            self.updated_at = datetime.now().isoformat()
            return True
        return False

    def regress_stage(self) -> bool:
        """Go back to previous stage (when issues found).

        Returns:
            True if regressed successfully.
        """
        current_idx = STAGE_ORDER.index(self.current_stage)
        if current_idx > 0:
            self.current_stage = STAGE_ORDER[current_idx - 1]
            self.updated_at = datetime.now().isoformat()
            return True
        return False


class WaterfallTracker:
    """Manage waterfall stage tracking for all features."""

    def __init__(self, storage_path: str = "data/waterfall_state.json"):
        """Initialize tracker with storage path."""
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.features: Dict[str, FeatureProgress] = {}
        self._load()

    def _load(self):
        """Load state from disk."""
        if self.storage_path.exists():
            data = json.loads(self.storage_path.read_text())
            self.features = {
                fid: FeatureProgress(**fdata) for fid, fdata in data.items()
            }

    def _save(self):
        """Save state to disk."""
        data = {fid: feature.model_dump() for fid, feature in self.features.items()}
        self.storage_path.write_text(json.dumps(data, indent=2))

    def start_feature(self, feature_id: str, title: str) -> FeatureProgress:
        """Start tracking a new feature.

        Args:
            feature_id: Unique identifier for the feature.
            title: Human-readable title.

        Returns:
            The created FeatureProgress instance.
        """
        feature = FeatureProgress(
            feature_id=feature_id,
            title=title,
            current_stage=WaterfallStage.ANALYSIS,
            started_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.features[feature_id] = feature
        self._save()
        return feature

    def get_feature(self, feature_id: str) -> Optional[FeatureProgress]:
        """Get feature progress by ID.

        Args:
            feature_id: Feature identifier.

        Returns:
            FeatureProgress or None if not found.
        """
        return self.features.get(feature_id)

    def list_features(
        self, stage: Optional[WaterfallStage] = None
    ) -> List[FeatureProgress]:
        """List all features, optionally filtered by stage.

        Args:
            stage: Optional stage to filter by.

        Returns:
            List of matching features.
        """
        features = list(self.features.values())
        if stage:
            features = [f for f in features if f.current_stage == stage]
        return sorted(features, key=lambda f: f.updated_at, reverse=True)

    def advance_feature(self, feature_id: str) -> bool:
        """Advance a feature to the next stage.

        Args:
            feature_id: Feature to advance.

        Returns:
            True if successful.
        """
        feature = self.features.get(feature_id)
        if not feature:
            return False

        if feature.advance_stage():
            self._save()
            return True
        return False

    def regress_feature(self, feature_id: str, reason: str = "") -> bool:
        """Move feature back to previous stage.

        Args:
            feature_id: Feature to regress.
            reason: Reason for regression.

        Returns:
            True if successful.
        """
        feature = self.features.get(feature_id)
        if not feature:
            return False

        if feature.regress_stage():
            if reason:
                feature.notes = f"{feature.notes}\n[REGRESSION] {reason}".strip()
            self._save()
            return True
        return False

    def update_notes(self, feature_id: str, notes: str):
        """Update feature notes.

        Args:
            feature_id: Feature to update.
            notes: New notes to add.
        """
        feature = self.features.get(feature_id)
        if feature:
            feature.notes = f"{feature.notes}\n{notes}".strip()
            feature.updated_at = datetime.now().isoformat()
            self._save()

    def get_current_feature(self) -> Optional[FeatureProgress]:
        """Get the most recently updated feature.

        Returns:
            Most recent FeatureProgress or None.
        """
        if not self.features:
            return None
        return max(self.features.values(), key=lambda f: f.updated_at)

    def get_stats(self) -> Dict:
        """Get statistics about features.

        Returns:
            Dictionary with counts per stage.
        """
        stats = {stage.value: 0 for stage in STAGE_ORDER}
        for feature in self.features.values():
            stats[feature.current_stage.value] += 1

        return {
            "total_features": len(self.features),
            "by_stage": stats,
            "active_features": len(
                [
                    f
                    for f in self.features.values()
                    if f.current_stage != WaterfallStage.COMPLETED
                ]
            ),
        }
