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

import asyncio
import sys
from os import getenv
from pathlib import Path

from pyrogram.client import Client
from rich.console import Console
from rich.progress import Progress

HOME: str = getenv("HOME", "")
API_ID: int = int(getenv("API_ID", ""))
API_HASH: str = getenv("API_HASH", "")
global_tasks: list[asyncio.Task | asyncio.Future] = []
# BOT_TOKEN: str = getenv("BOT_TOKEN", "")

console: Console = Console()
progress: Progress = Progress(console=console, transient=True)

_ = sys.argv.pop(0)  # Executable name
chat_id: int = int(sys.argv[0])
_ = sys.argv.pop(0)

loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()


async def upload_file(app: Client, chat_id: int, file: str) -> None:
    task = progress.add_task(file, start=False, total=None)

    async def update_progress(current: int, total: int) -> None:
        progress.start_task(task)
        if current == total:
            global_tasks.append(
                loop.create_task(
                    asyncio.to_thread(
                        progress.update,
                        task,
                        total=total,
                        completed=current,
                        visible=False,
                    )
                )
            )
            global_tasks.append(
                loop.create_task(
                    asyncio.to_thread(
                        console.print,
                        f"[bold green]✔ [/bold green][bold #FFFFFF]{file}[/bold #FFFFFF]",
                    )
                )
            )
        else:
            global_tasks.append(
                loop.create_task(asyncio.to_thread(progress.update, task, total=total, completed=current))
            )
            global_tasks.append(loop.create_task(asyncio.to_thread(progress.refresh)))

    await app.send_document(chat_id, file, progress=update_progress)


async def main() -> None:
    # console.print(f"[cyan]Credentials info[/cyan] {API_ID=} {API_HASH=} {BOT_TOKEN=}")
    app: Client = Client(
        name="CLI Uploader",
        api_id=API_ID,
        api_hash=API_HASH,
        # bot_token=BOT_TOKEN,
    )

    good_files: list[str] = [file for file in sys.argv if Path(file).is_file()]
    if len(good_files) == 0:
        console.print(
            "[red]Either [bold]No file(s) is/are given[/bold], or [bold]none of the files given exist![/bold][/red]"
        )
        return

    if len(sys.argv) != len(good_files):
        console.print("[yellow][bold]Warning:[/bold] some files cannot be uploaded because they do not exist[/yellow]")

    _ = await app.start()

    progress.start()
    console.print(f"[cyan]uploading[/cyan] {good_files} {chat_id=}")
    tasks: list[asyncio.Task] = [asyncio.create_task(upload_file(app, chat_id, file)) for file in good_files]
    _ = await asyncio.wait(tasks)
    _ = await asyncio.wait(global_tasks)

    progress.refresh()
    console.print("[bold green]Done![/bold green]")
    progress.stop()
    _ = await app.stop()


def entry():
    loop.run_until_complete(main())
