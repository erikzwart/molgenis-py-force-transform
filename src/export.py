'''export files'''
#from abc import ABC, abstractmethod

import configparser
import src.exceptions
import pathlib
import pandas as pd

class export():

    def is_dir(dir: pathlib.PosixPath) -> None:
        if not dir.is_dir():
            export.create_dir(dir)

    def is_empty(dir: pathlib.PosixPath) -> None:
        if any(dir.iterdir()):
            export.delete_files(dir)
            export.delete_dir(dir)
        export.create_dir(dir)

    def delete_dir(dir: pathlib.PosixPath) -> None:
        try:
            dir.rmdir()
        except OSError as e:
            print(f"Error:{ e.strerror}")

    def delete_files(dir: pathlib.PosixPath) -> None:
        def delete_file(file: pathlib.PosixPath) -> None:
            try:
                file.unlink()
            except OSError as e:
                print(f"Error:{ e.strerror}")

        for file in dir.iterdir():
            delete_file(file)

    def create_dir(dir: pathlib.PosixPath) -> None:
        try:
            dir.mkdir(parents=False, exist_ok=False)
        except OSError as e:
            print(f"Error:{ e.strerror}")
    
    def instrument_to_csv(data: pd.DataFrame, file: str) -> None:
        config = configparser.ConfigParser()
        config.read('src/config.ini')
        output = pathlib.Path().joinpath(config['settings']['output_folder'], file)
        if not output.is_file():
            data.to_csv(output, index=False, header=True)
        elif output.is_file():
            data.to_csv(output, index=False, header=False, mode='a')
        else:
            raise src.exceptions.ErrorWritingCsv()

