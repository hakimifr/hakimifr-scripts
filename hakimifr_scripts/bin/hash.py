# SPDX-License-Identifier: Apache-2.0
#
# Copyright 2026 Firdaus Hakimi <hakimifirdaus944@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from concurrent import futures
from hashlib import sha256
from os import cpu_count
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

console: Console = Console()
progress: Progress = Progress(transient=True, console=console)
cpu = cpu_count() or 2
executor = futures.ThreadPoolExecutor(max_workers=cpu + 8)

if hasattr(sys, "_is_gil_enabled"):
    gil_status = sys._is_gil_enabled()
else:
    gil_status = True

if gil_status:
    console.print(
        "[bold red]GIL is enabled. Parallel hashing speed will be slow. "
        "Use Python 3.13t/3.14t (freethreaded variant) for fast parallel hashing speed. "
        "If you use uv, export UV_PYTHON=3.14t[/bold red]"
    )
else:
    console.print("[bold green]GIL is disabled[/bold green]")


def compute_hash(file_path: str) -> None:
    with open(file_path, "rb") as f:
        hash_ = sha256(f.read()).hexdigest()
        console.print(f"[bold green]✔  SHA256 digest:[/bold green] {file_path} \t [bold #FFFFFF]{hash_}[/bold #FFFFFF]")


def main() -> None:
    futures = [
        executor.submit(compute_hash, file_path.as_posix()) for file_path in Path().rglob("*") if file_path.is_file()
    ]
    for f in futures:
        f.result()
