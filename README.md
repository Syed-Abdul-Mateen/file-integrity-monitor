# Real-Time File Integrity Monitoring System

This is a Python-based system that monitors file changes in real time, detects content modifications, and displays detailed, color-coded diffs with line numbers and timestamps.

## Features

- Real-time monitoring of file changes using `watchdog`
- Detection of additions, deletions, and modifications
- Displays both "before" and "after" file content
- Highlights line-level changes with corresponding line numbers
- Identifies and categorizes the type of change (addition, deletion, modification)
- Handles complete file deletions gracefully
- Color-coded terminal output using `colorama`
- Logs all file change events to a log file

## Folder Structure

```
FileIntegrityMonitoringSystem/
├── sample_data/               # Directory being monitored
├── reports/
│   └── .snapshots/            # Historical file snapshots
├── logs/
│   └── integrity_log.txt      # Log file capturing all events
├── src/
│   ├── main.py                # Core logic for monitoring and diff analysis
│   └── file_snapshots.py      # Snapshot storage and retrieval functions
└── README.md
```

## Installation

Install the required dependencies using pip:

```bash
pip install watchdog colorama
```

## Usage

1. Place the files to be monitored inside the `sample_data` directory.
2. Start the monitoring service:

   ```bash
   python src/main.py
   ```

3. Make any edits to files inside the `sample_data` directory. Changes will be detected and displayed in the terminal with details including:
   - Timestamps
   - Before and after content
   - Exact lines added or removed
   - Line numbers and change type
   - Total lines affected

## Logging

All events are logged in `logs/integrity_log.txt` for persistent tracking and audit purposes.

## License

This project is licensed under the MIT License.
