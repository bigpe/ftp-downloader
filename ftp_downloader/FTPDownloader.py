import asyncio
import math
import sys
from pathlib import Path
import aioftp
import inspect
import cursor
from colorama import Fore


class FTPDownloader:

    def __init__(self, HOST, PORT, USER, PASSWORD, SILENCE=False):
        self.HOST = HOST
        self.PORT = PORT
        self.USER = USER
        self.PASSWORD = PASSWORD
        self.SILENCE = SILENCE
        self.BASE_DIR = self.get_caller_path()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        exit()

    async def download_dir_async(self, download_from_dir, upload_to_dir, exclude_ext):
        async with aioftp.Client.context(self.HOST, self.PORT, self.USER, self.PASSWORD) as client:
            cursor.hide()
            self.message_handler('Get files list\n', message_type='regular')
            files_list = list(  # Filter list, exclude extensions and directories
                filter(
                    lambda item:
                    item[1]['type'] == 'file'
                    and item[0].suffix not in exclude_ext
                    and item[0].name != download_from_dir,
                    await client.list(path=download_from_dir, recursive=True)
                )
            )
            if not files_list:
                self.message_handler('Nothing to download', message_type='error')
                self.clear_tasks()
            self.message_handler(f'({len(files_list)}) {download_from_dir} -> '
                                 f'{Path.joinpath(self.BASE_DIR, upload_to_dir)}\n', message_type='plus')
            for i, (path, info) in enumerate(files_list):
                download = False
                upload_file_path = Path.joinpath(
                    Path.joinpath(self.BASE_DIR, upload_to_dir), path
                )
                destination_dir = str(upload_file_path).replace(path.name, '')
                file_name = path.name
                if not Path(upload_to_dir).exists() or not Path(upload_file_path).exists():
                    download = True
                if Path(upload_to_dir).exists() and Path(upload_file_path).exists():
                    ftp_file_size = int(info['size'])
                    local_file_size = upload_file_path.stat().st_size
                    # TODO diff creation time too
                    if ftp_file_size != local_file_size:
                        download = True
                if download:
                    self.message_handler(f'{path}', message_type='minus')
                    stream = await client.download_stream(path)
                    downloaded_size = 0
                    Path.unlink(upload_file_path, missing_ok=True)  # Remove file before append stream to file
                    Path.mkdir(Path(destination_dir), exist_ok=True, parents=True)  # Create dirs
                    async for block in stream.iter_by_block():
                        downloaded_size += sys.getsizeof(block)
                        file_size = int(info['size'])
                        open(upload_file_path, 'ab').write(block)
                        self.message_handler(
                            f'Loading: {math.floor(downloaded_size / file_size * 100)}%...',
                            end='\r', message_type='regular')
                    await stream.finish()
                self.message_handler(
                    f'({i + 1}/{len(files_list)}) {file_name} -> ../{path}', end='', message_type='plus')
                self.message_handler(
                    '\nLoading: Complete', message_type='success') if download else self.message_handler('')
            self.message_handler('\nFiles downloaded', message_type='success')

    def download_dir(self, download_from_dir, upload_to_dir='.', exclude_ext=[]):
        tasks = (
            self.download_dir_async(download_from_dir, upload_to_dir, exclude_ext),
        )
        asyncio.run(asyncio.wait(tasks))
        cursor.show()

    def message_handler(self, message, message_type=None, end=None):
        if not self.SILENCE:
            message_types = {
                'minus':    f'{Fore.RED}- {Fore.RESET}{message}',
                'error':    f'{Fore.RED}{message}{Fore.RESET}',
                'plus':     f'{Fore.GREEN}+ {Fore.RESET}{message}',
                'success':  f'{Fore.GREEN}{message}{Fore.RESET}',
                'regular':  f'{Fore.YELLOW}{message}{Fore.RESET}'
            }
            if message_type:
                message = message_types[message_type]
            print(message, end=end)

    @staticmethod
    def get_caller_path():
        frame = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        file_path = Path(module.__file__).resolve().parent
        return file_path

    @staticmethod
    def clear_tasks():
        for task in asyncio.current_task(asyncio.get_running_loop()):
            task.cancel()
