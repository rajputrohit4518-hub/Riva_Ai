import sys
import tempfile
import logging
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.logging.manager import ProductionLogManager

def test_logger_setup_and_file_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "riva.log"
        logger = ProductionLogManager.setup_logger(name="riva_test", level="DEBUG", log_file=str(log_file))
        
        logger.debug("Test debug message")
        logger.info("Test info message")
        
        # Explicitly close and remove handlers so Windows releases the file lock
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()
        
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Test debug message" in content
        assert "Test info message" in content
        assert "riva_test" in content
