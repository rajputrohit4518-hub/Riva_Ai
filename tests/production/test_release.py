import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.release.candidate import ProductionReleaseCandidate

def test_release_candidate_readiness():
    rc = ProductionReleaseCandidate()
    report = rc.verify_readiness()
    
    assert report["version"] == "1.0.0-rc1"
    assert report["structure_intact"] is True
    assert report["tests_passed"] is True
    assert report["ready_for_release"] is True
