import asyncio
import math
import sys
from pathlib import Path
from typing import Union

import aioftp
import inspect
import cursor
from aioftp import StatusCodeError
from colorama import Fore


class FTPDownloader:

    def __init__(self, host, port, user, password, silence=False):
        self.HOST: str = host
        self.PORT: int = port
        self.USER: str = user
        self.PASSWORD: str = password
        self.SILENCE: bool = silence

        self._BASE_DIR: Union[Path, str] = self.get_caller_path()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        exit()

    async def download_dir_async(self, download_from_dir, upload_to_dir, exclude_ext, with_root_path):
        async with aioftp.Client.context(self.HOST, self.PORT, self.USER, self.PASSWORD) as client:
            files_list = await self.get_files_list(client, download_from_dir, exclude_ext)
            self.check_files_list(files_list)
            self.show_text_before_start(files_list, download_from_dir, upload_to_dir)
            await self.start_download(client, files_list, download_from_dir, upload_to_dir, with_root_path)

    async def get_files_list(self, client, download_from_dir, exclude_ext):
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
        return files_list

    def check_files_list(self, files_list):
        if not files_list:
            self.message_handler('Nothing to download', message_type='error')
            self.clear_tasks()

    def show_text_before_start(self, files_list, download_from_dir, upload_to_dir):
        files_list_count = len(files_list)
        self.message_handler(
            f'({files_list_count}) {download_from_dir} -> '
            f'{Path.joinpath(self._BASE_DIR, upload_to_dir)}\n',
            message_type='plus'
        )

    async def start_download(self, client, files_list, download_from_dir, upload_to_dir, with_root_path):
        for i, (path, info) in enumerate(files_list):
            upload_file_path = self.get_upload_file_path(path, download_from_dir, upload_to_dir, with_root_path)
            destination_dir = str(upload_file_path).replace(path.name, '')
            file_name = path.name

            download = self.download_file_or_not(info, upload_file_path, upload_to_dir)

            if download:
                await self.download_file(client, path, info, upload_file_path, destination_dir)
            self.message_handler(
                f'({i + 1}/{len(files_list)}) {file_name} -> ../{path}', end='', message_type='plus')
            self.message_handler(
                '\nLoading: Complete', message_type='success') if download else self.message_handler('')
        self.message_handler('\nFiles downloaded', message_type='success')

    def get_upload_file_path(self, path, download_from_dir, upload_to_dir, with_root_path):
        upload_file_path = Path.joinpath(
            self._BASE_DIR.joinpath(upload_to_dir),
            path if with_root_path else path.relative_to(download_from_dir)
        )
        return upload_file_path

    @staticmethod
    def download_file_or_not(info, upload_file_path, upload_to_dir):
        download = False
        if not Path(upload_to_dir).exists() or not Path(upload_file_path).exists():
            download = True
        if Path(upload_to_dir).exists() and Path(upload_file_path).exists():
            ftp_file_size = int(info['size'])
            local_file_size = upload_file_path.stat().st_size
            # TODO diff creation time too
            if ftp_file_size != local_file_size:
                download = True
        return download

    async def download_file(self, client, path, info, upload_file_path, destination_dir):
        self.message_handler(f'{path}', message_type='minus')
        stream = await self.get_stream(client, path)
        self.prepare_fs_before_writing(upload_file_path, destination_dir)
        await self.write_blocks(stream, info, upload_file_path)
        await stream.finish()

    def download_dir(self, download_from_dir, upload_to_dir='.', exclude_ext=None, with_root_path=True):
        cursor.hide()
        tasks = (
            self.download_dir_async(download_from_dir, upload_to_dir, exclude_ext, with_root_path),
        )
        asyncio.run(asyncio.wait(tasks))
        cursor.show()

    @staticmethod
    def prepare_fs_before_writing(upload_file_path, destination_dir):
        Path.unlink(upload_file_path, missing_ok=True)  # Remove file before append stream to file
        Path.mkdir(Path(destination_dir), exist_ok=True, parents=True)  # Create dirs

    async def get_stream(self, client, path):
        try:
            stream = await client.download_stream(path)
        except StatusCodeError as err:
            self.message_handler(
                f'Download error\n'
                f'{err}', message_type='error'
            )
            self.clear_tasks()
            return None
        return stream

    def show_progress_bar(self, downloaded_size, file_size):
        self.message_handler(
            f'Loading: {math.floor(downloaded_size / file_size * 100)}%...',
            end='\r', message_type='regular')

    @staticmethod
    def write_block(upload_file_path, block):
        open(upload_file_path, 'ab').write(block)

    async def write_blocks(self, stream, info, upload_file_path):
        downloaded_size = 0
        async for block in stream.iter_by_block():
            downloaded_size += sys.getsizeof(block)
            file_size = int(info.get('size', 0))

            self.write_block(upload_file_path, block)
            self.show_progress_bar(downloaded_size, file_size)

    def message_handler(self, message, message_type=None, end=None):
        if not self.SILENCE:
            message_types = {
                'minus': f'{Fore.RED}- {Fore.RESET}{message}',
                'error': f'{Fore.RED}{message}{Fore.RESET}',
                'plus': f'{Fore.GREEN}+ {Fore.RESET}{message}',
                'success': f'{Fore.GREEN}{message}{Fore.RESET}',
                'regular': f'{Fore.YELLOW}{message}{Fore.RESET}'
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
