import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.regression.runner import ProductionRegressionRunner

def test_regression_runner_execution():
    # Verify the runner executes and captures test results successfully
    report = ProductionRegressionRunner.run_full_suite()
    assert "exit_code" in report
    assert "success" in report
    # We expect all accumulated tests to pass successfully
    assert report["success"] is True
