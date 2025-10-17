import logging
import json
from datetime import datetime

audit_logger = logging.getLogger("audit")


def record(event, source_ip=None, user=None, details=None, level="INFO"):
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "source_ip": source_ip,
        "user": user,
        "details": details,
    }
    if level == "INFO":
        audit_logger.info(json.dumps(entry, ensure_ascii=False))
    else:
        audit_logger.warning(json.dumps(entry, ensure_ascii=False))
