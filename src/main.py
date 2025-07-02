import os
import hashlib
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import difflib
from datetime import datetime
from file_snapshots import load_snapshot, save_snapshot
from colorama import init, Fore, Style

init(autoreset=True)

os.makedirs("logs", exist_ok=True)
os.makedirs("reports", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/integrity_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

MONITOR_DIR = "sample_data"
HASH_RECORD_FILE = "reports/hash_records.txt"

def calculate_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing {filepath}: {e}")
        return None

def load_hashes():
    hashes = {}
    if os.path.exists(HASH_RECORD_FILE):
        with open(HASH_RECORD_FILE, "r", encoding="utf-8") as f:
            for line in f:
                path, hash_val = line.strip().split("||")
                hashes[path] = hash_val
    return hashes

def save_hashes(hashes):
    with open(HASH_RECORD_FILE, "w", encoding="utf-8") as f:
        for path, hash_val in hashes.items():
            f.write(f"{path}||{hash_val}\n")

def read_file_lines(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return ["[Unable to read file contents]"]

class IntegrityHandler(FileSystemEventHandler):
    def __init__(self, hashes):
        self.hashes = hashes

    def on_modified(self, event):
        if not event.is_directory:
            filepath = event.src_path
            current_hash = calculate_hash(filepath)
            stored_hash = self.hashes.get(filepath)

            if current_hash and stored_hash and current_hash != stored_hash:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("\n" + "=" * 100)
                print(f"{now}")
                print(f"File modified: {filepath}")
                print("-" * 100)

                before = load_snapshot(filepath)
                after = read_file_lines(filepath)

                before_str = "".join(before).strip()
                after_str = "".join(after).strip()

                print("Before content:\n")
                print(before_str)
                print("\n" + "_" * 80 + "\n")

                print("After content:\n")
                print(after_str)
                print("\n" + "_" * 80 + "\n")

                if not after:
                    print("Changes made:")
                    print("The entire file content was deleted.\n")
                else:
                    print("Changes made:\n")
                    print(f"Original line count: {len(before)}")
                    print(f"Updated line count : {len(after)}\n")

                    sm = difflib.SequenceMatcher(None, before, after)
                    added = []
                    removed = []

                    for tag, i1, i2, j1, j2 in sm.get_opcodes():
                        if tag == 'insert':
                            for idx, line in enumerate(after[j1:j2], start=j1 + 1):
                                added.append((idx, line.rstrip('\n')))
                        elif tag == 'delete':
                            for idx, line in enumerate(before[i1:i2], start=i1 + 1):
                                removed.append((idx, line.rstrip('\n')))
                        elif tag == 'replace':
                            for idx, line in enumerate(before[i1:i2], start=i1 + 1):
                                removed.append((idx, line.rstrip('\n')))
                            for idx, line in enumerate(after[j1:j2], start=j1 + 1):
                                added.append((idx, line.rstrip('\n')))

                    pad_width = max(len(str(max(len(before), len(after), 1))), 2)

                    if removed:
                        print("Removed lines:")
                        for idx, line in removed:
                            print(Fore.RED + f"{str(idx).rjust(pad_width)}  {line}")
                        print()

                    if added:
                        print("Added lines:")
                        for idx, line in added:
                            print(Fore.GREEN + f"{str(idx).rjust(pad_width)}  {line}")

                    if added and removed:
                        change_type = "modification"
                    elif added:
                        change_type = "addition"
                    elif removed:
                        change_type = "deletion"
                    else:
                        change_type = "unknown"

                    print(f"\nChange type    : {change_type}")
                    print(f"Affected lines : {len(added) + len(removed)}")

                print("=" * 100 + "\n")

            self.hashes[filepath] = current_hash
            save_hashes(self.hashes)
            save_snapshot(filepath, read_file_lines(filepath))

if __name__ == "__main__":
    if not os.path.exists(MONITOR_DIR):
        os.makedirs(MONITOR_DIR)

    hashes = load_hashes()

    for root, dirs, files in os.walk(MONITOR_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            hashes[filepath] = calculate_hash(filepath)
            save_snapshot(filepath, read_file_lines(filepath))

    save_hashes(hashes)

    event_handler = IntegrityHandler(hashes)
    observer = Observer()
    observer.schedule(event_handler, path=MONITOR_DIR, recursive=True)
    observer.start()
    print(f"Monitoring directory: {MONITOR_DIR}")
    print("Edit any file inside it and check terminal/logs\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
