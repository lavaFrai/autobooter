import serial.tools.list_ports
import tkinter as tk
import tkinter.ttk as ttk
import urllib.error
import urllib.request
import hashlib
import shutil
import sys
import serial
import glob
import os

repository = "https://github.com/lavaFrai/lostis"
avrdude_link = "https://github.com/lavaFrai/autobooter/blob/main/host/avrdude.exe?raw=true"
config_link = "https://github.com/lavaFrai/autobooter/blob/main/host/avrdude.conf?raw=true"


def serial_ports():
    return list(map(str, list(serial.tools.list_ports.comports())))


def md5(f_name):
    hash_md5 = hashlib.md5()
    with open(f_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def run_process():
    global root, progress_frame, progress_label, progress_bar, go_button
    go_button.config(state="disabled")
    # Скачиваем бинарные файлы прошивки
    try:
        urllib.request.urlretrieve(repository + "/blob/master/autoboot/lasted.hex/?raw=true",
                                   "bin_file.hex",
                                   reporthook=download_progress)
    except BaseException as e:
        if e == urllib.error.URLError:
            progress(0, "Ошибка загрузки, нет соединения")
            return
        else:
            progress(0, "Ошибка загрузки, неизвестная ошибка [" + str(e) + "]")
            return
    else:
        progress(100, "Завершение...")
    progress(0, "Распаковка...")
    shutil.move('bin_file.hex', 'firmware.hex')
    try:
        urllib.request.urlretrieve(config_link,
                                   "bin_file.hex",
                                   reporthook=download_progress)
    except BaseException as e:
        if e == urllib.error.URLError:
            progress(0, "Ошибка загрузки, нет соединения")
            return
        else:
            progress(0, "Ошибка загрузки, неизвестная ошибка [" + str(e) + "]")
            return
    else:
        progress(100, "Завершение...")
    progress(0, "Распаковка...")
    shutil.move('bin_file.hex', 'config.conf')
    progress(0, "Подкачка компонентов...")
    # Скачиваем бинарные файлы avrdude
    try:
        urllib.request.urlretrieve(avrdude_link,
                                   "bin_file.hex",
                                   reporthook=download_dude_progress)
    except BaseException as e:
        if e == urllib.error.URLError:
            progress(0, "Ошибка загрузки, нет соединения")
            return
        else:
            progress(0, "Ошибка загрузки, неизвестная ошибка [" + str(e) + "]")
    else:
        progress(100, "Завершение...")
    progress(0, "Распаковка...")
    shutil.move('bin_file.hex', 'avrdude.exe')
    progress(0, "Поиск устройства...")
    print(serial_ports())
    ports = serial_ports()
    port = ""
    for i in range(len(ports)):
        if "CH340" in ports[i]:
            port = ports[i]
    if port == "":
        progress(100, "Устройство\nНе обнаружено")
        return
    progress(100, "Устройство\nОбнаружено [" + port.split()[0] + "]")
    port = port.split()[0]
    progress(0, "Загрузка...")
    os.system('avrdude.exe  -C"' + os.getcwd() + '\\config.conf" -v -patmega328p -carduino -P' + port + ' -b115200 -D '
                                                 '-Uflash:w:"' + os.getcwd() + '\\firmware.hex":i')
    progress(50, "Очистка")
    os.remove("config.conf")
    progress(70, "Очистка")
    os.remove("avrdude.exe")
    progress(90, "Очистка")
    os.remove("firmware.hex")
    progress(100, "Загружено")


def progress(value: int, label: str):
    global root, progress_frame, progress_label, progress_bar
    progress_bar.config(value=value)
    progress_label.config(text=label)
    root.update()


def download_progress(count, block_size, total_size):
    progress(count / (total_size / block_size) * 100, "Загрузка файлов...")


def download_dude_progress(count, block_size, total_size):
    progress(count / (total_size / block_size) * 100, "Подкачка компонентов...")


if __name__ == '__main__':
    # Обьявление глобальный переменных
    global root, progress_frame, progress_label, progress_bar, go_button
    root = tk.Tk()
    # root.geometry("150x100")
    # Создаем фреймы и графику
    # Фрейм прогресбара
    progress_frame = tk.Frame(root)
    progress_frame.grid(row=0, column=0, padx=10, pady=10)
    progress_label = tk.Label(progress_frame, text="Подготовка...")
    progress_label.grid(row=0, column=0)
    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", maximum=100, value=0)
    progress_bar.grid(row=1, column=0)
    # Кнопки
    go_button = tk.Button(root, text="Начать обновление")
    go_button.config(command=run_process)
    go_button.grid(row=1, column=0)
    root.mainloop()
