import argparse
import tarfile
import time
import sys
from pathlib import Path
from compression import bz2, zstd

def progress_bar(task: str, duration=1.0):
    """Простая анимация прогресса"""
    chars = "|/-\\"
    for i in range(20):
        sys.stdout.write(f"\r⏳ {task}... {chars[i % len(chars)]}")
        sys.stdout.flush()
        time.sleep(duration / 20)
    sys.stdout.write("\r" + " " * (len(task) + 10) + "\r")  # очистка
    sys.stdout.flush()

def make_tar(source: Path, tar_path: Path):
    """Создание tar-архива из директории или файла"""
    with tarfile.open(tar_path, "w") as tar:
        tar.add(source, arcname=source.name)
    return tar_path

def extract_tar(tar_path: Path, output_dir: Path):
    """Распаковка tar-архива"""
    with tarfile.open(tar_path, "r") as tar:
        tar.extractall(path=output_dir)

def compress_file(source: Path, target: Path):
    """Сжатие файла (bz2 или zstd)"""
    ext = target.suffix.lower()
    with open(source, "rb") as src:
        data = src.read()

    if ext == ".bz2":
        compressed = bz2.compress(data)
    elif ext == ".zst":
        compressed = zstd.compress(data)
    else:
        raise ValueError(f"Неподдерживаемое расширение: {ext}")

    with open(target, "wb") as dst:
        dst.write(compressed)
    print(f"✅ Файл '{source.name}' сжат → {target.name}")

def decompress_file(source: Path, target: Path):
    """Распаковка bz2 или zstd файла"""
    ext = source.suffix.lower()
    with open(source, "rb") as src:
        data = src.read()

    if ext == ".bz2":
        decompressed = bz2.decompress(data)
    elif ext == ".zst":
        decompressed = zstd.decompress(data)
    else:
        raise ValueError(f"Неподдерживаемое расширение: {ext}")

    with open(target, "wb") as dst:
        dst.write(decompressed)
    print(f"✅ Файл '{source.name}' распакован → {target.name}")

def main():
    parser = argparse.ArgumentParser(
        description="Архиватор/распаковщик на стандартной библиотеке Python 3.14 (bz2 и zstd)."
    )
    parser.add_argument("source", type=Path, help="Источник (файл или директория)")
    parser.add_argument("target", type=Path, help="Целевой архив или распакованный файл/папка")
    parser.add_argument("--benchmark", action="store_true", help="Показать время выполнения")

    args = parser.parse_args()
    start = time.time()

    try:
        progress_bar("Выполняется операция")

        # Сжатие
        if args.target.suffix.lower() in (".bz2", ".zst"):
            if args.source.is_dir():
                temp_tar = args.source.with_suffix(".tar")
                make_tar(args.source, temp_tar)
                compress_file(temp_tar, args.target)
                temp_tar.unlink()
            else:
                compress_file(args.source, args.target)

        # Распаковка
        else:
            ext = args.source.suffix.lower()
            if ext in (".bz2", ".zst"):
                # Если целевой путь — папка, значит это архив директории
                if args.target.is_dir() or args.target.suffix == "":
                    temp_tar = args.target.with_suffix(".tar")
                    decompress_file(args.source, temp_tar)
                    args.target.mkdir(exist_ok=True)
                    extract_tar(temp_tar, args.target)
                    temp_tar.unlink()
                    print(f"📂 Распаковано в каталог: {args.target}")
                else:
                    # обычный файл
                    decompress_file(args.source, args.target)
            elif tarfile.is_tarfile(args.source):
                # исходник уже tar
                extract_tar(args.source, args.target)
                print(f"📂 Распаковано в каталог: {args.target}")
            else:
                raise ValueError("Формат не поддерживается для распаковки.")


    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        if args.benchmark:
            print(f"⏱ Время выполнения: {time.time() - start:.3f} сек.")

if __name__ == "__main__":
    main()


