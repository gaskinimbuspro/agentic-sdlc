"""gofmt itself returns zero for unformatted files; fail on its actual output."""

import subprocess
import sys

result = subprocess.run(
    ["gofmt", "-l", "."], capture_output=True, text=True, check=False
)
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
sys.exit(result.returncode or int(bool(result.stdout.strip())))
