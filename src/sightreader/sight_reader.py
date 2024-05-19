from .sight import Sight
import os

class SightReader:
    @staticmethod
    def read_from_directory(directory: str) -> list[Sight]:
        directory_path = os.path.join(os.path.curdir, directory)
        __class__.__check_root_directory(directory_path)
        return __class__.__process_directory(directory_path)

    @staticmethod
    def __process_directory(directory_path) -> list[Sight]:
        sights: list[Sight] = []
        images_path = os.path.join(directory_path, "images")
        __class__.__check_images_directory(images_path)
        for entry in os.scandir(directory_path):
            if entry.is_file():
                sights.append(__class__.__process_file(entry.path, images_path))
        return sights

    @staticmethod
    def __process_file(file_str, images_path) -> Sight:
        with open(file_str, encoding="utf-8") as file:
            file_iter = iter(file)
            image_str = next(file_iter, None)
            if image_str is None:
                print(f"Ошибка при обработке файла {file_str}. Файл оказался пустой. Удалите его пожалуйста.")
                raise Exception(f"Ошибка при обработке файла {file_str}. Файл оказался пустой. Удалите его пожалуйста.")
            image_path = os.path.join(images_path, image_str.strip())
            if not os.path.isfile(image_path):
                print(f"Ошибка при обработке файла {file_str}. Изображение \"{image_path}\" не найдено! Поправьте ошибку")
                raise Exception(f"Ошибка при обработке файла {file_str}. Изображение \"{image_path}\" не найдено! Поправьте ошибку")
            line = next(file_iter, None)
            while line is not None and len(line.strip()) == 0:
                line = next(file_iter, None)
            if line is None:
                print(f"Ошибка при обработке файла {file_str}. Неожиданный конец файла. Ожидалось Name:")
                raise Exception(f"Ошибка при обработке файла {file_str}. Неожиданный конец файла. Ожидалось Name:")
            name = line.split(":")[-1].strip()
            line = next(file_iter, None)
            while line is not None and len(line.strip()) == 0:
                line = next(file_iter, None)
            if line is None:
                print(f"Ошибка при обработке файла {file_str}. Неожиданный конец файла. Ожидалось Place:")
                raise Exception(f"Ошибка при обработке файла {file_str}. Неожиданный конец файла. Ожидалось Place:")
            place = line.split(":")[-1].strip()
            line = next(file_iter, None)
            while line is not None and len(line.strip()) == 0:
                line = next(file_iter, None)
            if line is None:
                print(f"Ошибка при обработке файла {file_str}. Неожиданный конец файла. Ожидалось описание")
                raise Exception(f"Ошибка при обработке файла {file_str}. Неожиданный конец файла. Ожидалось описание")
            description = line
            line = next(file_iter, None)
            while line is not None:
                if len(line.strip()) != 0:
                    description += line
                line = next(file_iter, None)
            if not description:
                print(f"Ошибка при обработке файла {file_str}. Неожиданный конец файла. Ожидалось описание")
                raise Exception(f"Ошибка при обработке файла {file_str}. Неожиданный конец файла. Ожидалось описание")
            sight = Sight()
            sight.image = image_path
            sight.place = place
            sight.description = description
            sight.name = name
            return sight


    @staticmethod
    def __check_root_directory(directory_path):
        if not os.path.isdir(directory_path):
            print(f"Директория {directory_path} не найдена! Проверьте что вы сложили все файлы в {directory_path}")
            raise Exception(f"Директория {directory_path} не найдена! Проверьте что вы сложили все файлы в {directory_path}")
        
    @staticmethod
    def __check_images_directory(images_path):
        if not os.path.isdir(images_path):
            print(f"Директория {images_path} не найдена! Проверьте что вы сложили все изображения достопримечательностей в {images_path}")
            raise Exception(f"Директория {images_path} не найдена! Проверьте что вы сложили все изображения достопримечательностей в {images_path}")

