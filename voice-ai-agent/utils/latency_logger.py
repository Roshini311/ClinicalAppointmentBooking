import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LatencyLogger")

class LatencyLogger:
    def __init__(self):
        self.timestamps = {}
        self.start_time = None

    def start(self):
        self.start_time = time.time()
        self.timestamps["start"] = self.start_time

    def mark(self, stage_name: str):
        if self.start_time is None:
            self.start()
        self.timestamps[stage_name] = time.time()

    def get_summary(self) -> dict:
        summary = {}
        last_time = self.timestamps.get("start")
        total_latency = 0
        for stage, t in self.timestamps.items():
            if stage == "start":
                continue
            latency = (t - last_time) * 1000  # ms
            summary[stage] = f"{latency:.2f} ms"
            total_latency += latency
            last_time = t
        
        summary["total_latency"] = f"{total_latency:.2f} ms"
        return summary

    def log_summary(self):
        summary = self.get_summary()
        logger.info(f"--- Pipeline Latency Summary ---")
        for k, v in summary.items():
            logger.info(f"{k}: {v}")
        logger.info(f"--------------------------------")
