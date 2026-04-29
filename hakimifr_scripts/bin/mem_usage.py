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
from concurrent.futures import ThreadPoolExecutor
from textwrap import dedent

import psutil
from rich.console import Console
from rich.table import Table

console = Console()


def find_root_pids(name: str) -> list[int]:
    return [p.pid for p in psutil.process_iter(["name"]) if p.info["name"] == name]


def collect_pids(root_pids: list[int]) -> set[int]:
    all_pids = set(root_pids)
    for pid in root_pids:
        try:
            proc = psutil.Process(pid)
            all_pids.update(c.pid for c in proc.children(recursive=True))
        except psutil.NoSuchProcess:
            pass
    return all_pids


def sum_memory(pids: set[int]) -> tuple[int, int, int]:
    total_rss = total_pss = total_uss = 0
    for pid in pids:
        try:
            mem = psutil.Process(pid).memory_full_info()
            total_rss += mem.rss
            total_pss += mem.pss
            total_uss += mem.uss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return total_rss, total_pss, total_uss


def process_entry(name: str) -> tuple[str, int, int, int] | None:
    root_pids = find_root_pids(name)
    if not root_pids:
        return None
    pids = collect_pids(root_pids)
    rss, pss, uss = sum_memory(pids)
    return name, rss, pss, uss


def fmt(b: int) -> str:
    gib = b / (1024**3)
    if gib >= 1:
        return f"{gib:.3f} GiB"
    return f"{b / (1024**2):.3f} MiB"


def main():
    names = sys.argv[1:]
    if not names:
        console.print("[red]usage: mem_usage.py <process 1> \\[process 2] ...[/red]")
        sys.exit(1)

    with ThreadPoolExecutor() as pool:
        results = list(pool.map(process_entry, names))

    table = Table(title="Memory Usage", header_style="bold cyan")
    table.add_column("Process")
    table.add_column("RSS", justify="right")
    table.add_column("PSS", justify="right")
    table.add_column("USS", justify="right")

    for name, result in zip(names, results, strict=True):
        if result is None:
            table.add_row(name, "[red]not found[/red]", "[red]not found[/red]", "[red]not found[/red]")
        else:
            _, rss, pss, uss = result
            table.add_row(name, fmt(rss), fmt(pss), fmt(uss))

    console.print(table)
    console.print(
        dedent(
            """
            [grey50][bold] * note:[/bold]
                RSS = Resident Set Size
                PSS = Proportional Set Size
                USS = Unique Set Size

            [bold] * use PSS for casual comparison between apps.[/bold][/grey50]
            """
        ),
    )


if __name__ == "__main__":
    main()
