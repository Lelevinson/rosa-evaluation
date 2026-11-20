"""Release the temporary idle-sleep hold after the detached pipeline ends."""
from pathlib import Path
import time

campaign = Path('/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation/artifacts/reliability-v1-20261022')
deadline = time.monotonic() + 7 * 3600
receipt = campaign.parents[2] / 'reports/RELIABILITY_V1_POSTPROCESS_RECEIPT.json'
while time.monotonic() < deadline and not receipt.exists() and not (campaign / 'monitor.stop').exists():
    time.sleep(10)
(campaign / 'monitor.stop').touch()
