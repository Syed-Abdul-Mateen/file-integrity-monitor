import os

SNAPSHOT_DIR = "reports/.snapshots"

def load_snapshot(path):
    try:
        full_path = os.path.join(SNAPSHOT_DIR, path.replace("\\", "_").replace("/", "_") + ".txt")
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                return f.readlines()
    except:
        return []
    return []

def save_snapshot(path, content_lines):
    try:
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        full_path = os.path.join(SNAPSHOT_DIR, path.replace("\\", "_").replace("/", "_") + ".txt")
        with open(full_path, "w", encoding="utf-8") as f:
            f.writelines(content_lines)
    except Exception as e:
        print(f"Snapshot error: {e}")
