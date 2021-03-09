import asyncio
from pathlib import Path
import aioftp
import inspect


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
            self.message_handler('Get files list')
            files_list = list(  # Filter list, exclude extensions and directories
                filter(
                    lambda item:
                    item[1]['type'] == 'file'
                    and item[0].suffix not in exclude_ext
                    and item[0].name != download_from_dir
                    ,
                    await client.list(path=download_from_dir, recursive=True)
                )
            )
            if not files_list:
                self.message_handler('Nothing to download')
                self.clear_tasks()
            self.message_handler(f'Files ({len(files_list)}) from {download_from_dir} start downloading to '
                                 f'{Path.joinpath(self.BASE_DIR, upload_to_dir)}')
            for i, (path, info) in enumerate(files_list):
                download = False
                upload_file_path = Path.joinpath(
                    Path.joinpath(self.BASE_DIR, upload_to_dir), path
                )
                destination_dir = str(upload_file_path).replace(path.name, '')
                if not Path(upload_to_dir).exists() or not Path(upload_file_path).exists():
                    download = True
                if Path(upload_to_dir).exists() and Path(upload_file_path).exists():
                    ftp_file_size = int(info['size'])
                    local_file_size = upload_file_path.stat().st_size
                    # TODO diff creation time too
                    if ftp_file_size != local_file_size:
                        download = True
                if download:
                    self.message_handler(f'- {path}')
                    await client.download(path, destination=destination_dir, write_into=False)
                self.message_handler(f'+ ({i + 1}/{len(files_list)}) {path} -> {upload_file_path}')
            self.message_handler('Files downloaded')

    def download_dir(self, download_from_dir, upload_to_dir='.', exclude_ext=[]):
        tasks = (
            self.download_dir_async(download_from_dir, upload_to_dir, exclude_ext),
        )
        asyncio.run(asyncio.wait(tasks))

    def message_handler(self, message):
        if not self.SILENCE:
            print(message)

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
