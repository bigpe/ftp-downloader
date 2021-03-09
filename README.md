# **FTP DOWNLOADER**

## Usage:

##### Install package:

```shell script
$ pip3 install ftp_downloader
```

##### Import add initialize class object:

```python
from ftp_downloader import FTPDownloader

ftp_client=FTPDownloader(FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD)
```

##### Examples:

Download all files in the selected ftp directory (And re-download only modified files for reused).

```python
ftp_client.download_dir(download_from_dir='directory')
```

##### Additions args:

###### download_dir():

- upload_to_dir (Str, Root directory for uploaded files)
- exclude_ext (Array, Exclude extensions from download)

###### FTPDownloader():

- SILENCE (Bool, Disable/Enable all prints output)

## Использование:

##### Установка пакета:

```shell script
$ pip3 install ftp_downloader
```

##### Импорт и инициализация объекта класса:

```python
from ftp_downloader import FTPDownloader

ftp_client=FTPDownloader(FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD)
```

##### Примеры:

Загрузить все файлы из выбранной FTP директории (При повторном вызове загрузить заново только измененные файлы)

```python
ftp_client.download_dir(download_from_dir='directory')
```
##### Дополнительные аргументы:

###### download_dir():

- upload_to_dir (Str, Корневая директория для загружаемых файлов)
- exclude_ext (Array, Исключить расширения файлов из загрузки)

###### FTPDownloader():

- SILENCE (Bool, Включить/Выключить вывод процессов)