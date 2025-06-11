"""
Test script to verify log aggregation system functionality.
"""

import os
import sys
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.core.state_logger import StateLogger


def test_log_aggregation():
    """Test the log aggregation system."""
    print("Testing Log Aggregation System...")

    # Create a test logger
    logger = StateLogger("test_component")

    print("\n1. Testing rendering operation aggregation (should create table):")

    # Simulate multiple rendering operations (should trigger aggregation)
    for i in range(5):
        logger.log_rendering_operation("text", success=True)
        logger.log_rendering_operation("code", success=True)
        logger.log_rendering_operation("image", success=False)
        time.sleep(0.1)  # Small delay to simulate real rendering

    print("   - Logged 15 rendering operations (5 text, 5 code, 5 image)")

    # Wait for aggregation window to pass
    print("   - Waiting for aggregation window (1.1 seconds)...")
    time.sleep(1.1)

    # Trigger one more operation to force flush
    logger.log_rendering_operation("list", success=True)

    print("\n2. Testing individual operations (should not aggregate):")

    # Test with fewer operations (should not aggregate)
    logger.log_rendering_operation("workflow", success=True)
    logger.log_rendering_operation("interactive", success=True)

    # Force flush to see individual logs
    print("   - Forcing flush of remaining logs...")
    logger.flush_aggregated_logs()

    print("\n3. Testing mixed operation types:")

    # Test mixed operations
    logger.log_operation_start("data_loading")
    logger.log_rendering_operation("text", success=True)
    logger.log_rendering_operation("text", success=True)
    logger.log_rendering_operation("text", success=True)
    logger.log_operation_end("data_loading", success=True)

    # Force final flush
    time.sleep(1.1)
    logger.flush_aggregated_logs()

    print("\nLog aggregation test completed!")


if __name__ == "__main__":
    test_log_aggregation()
