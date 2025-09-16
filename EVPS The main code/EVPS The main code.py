import tkinter as tk
from tkinter import ttk
import threading
import numpy as np
from PIL import Image, ImageTk
import pygame
import random
import time
from itertools import permutations

pygame.mixer.init()

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Процедурная обработка и волномеризация")
        
        # Инициализация переменных
        self.range_ranges = {
            'Диапазон 1': (0, 255),
            'Диапазон 2': (0, 255),
            'Диапазон 3': (0, 255)
        }
        self.repeatability_percent = 50
        self.fragment_count = 5
        self.range_repetition = [30, 60]
        self.dispersion_type = 'Маленькие'
        self.representativity = 0.5

        # Для волнометрии
        self.init_wave_params()

        # Создаем вкладки интерфейса
        self.setup_ui()

        # Для генерации Permutations
        self.rgb_permutations = list(permutations(list(range(10)), 3))
        self.current_index = 0
        self.update_wave_flag = False  # флаг активности волнометрии

        # Для видеобара
        self.setup_video()

    def init_wave_params(self):
        pass

    def setup_ui(self):
        # Вкладки
        tab_control = ttk.Notebook(self.root)
        self.tab_params = ttk.Frame(tab_control)
        self.tab_wave = ttk.Frame(tab_control)
        tab_control.add(self.tab_params, text='Параметры Мозаики')
        tab_control.add(self.tab_wave, text='Волномеризация')
        tab_control.pack(expand=1, fill='both')

        # Параметры мозаики
        self.setup_mosaic_params(self.tab_params)

        # Вкладка волнометрии
        self.setup_wave_view(self.tab_wave)

    def setup_mosaic_params(self, parent):
        # Диапазоны случайной генерации
        lbl_ranges = tk.Label(parent, text='Диапазоны случайной генерации:')
        lbl_ranges.pack()

        self.range_entries = []
        for key in ['Диапазон 1', 'Диапазон 2', 'Диапазон 3']:
            frame = tk.Frame(parent)
            frame.pack(pady=2)
            lbl = tk.Label(frame, text=key)
            lbl.pack(side=tk.LEFT)
            entry_min = tk.Entry(frame, width=5)
            entry_min.pack(side=tk.LEFT)
            entry_max = tk.Entry(frame, width=5)
            entry_max.pack(side=tk.LEFT)
            # Значения по умолчанию
            entry_min.insert(0, str(self.range_ranges[key][0]))
            entry_max.insert(0, str(self.range_ranges[key][1]))
            self.range_entries.append((entry_min, entry_max))
        
        # Общая повторяемость
        lbl_repeat = tk.Label(parent, text='Общая повторяемость (%)')
        lbl_repeat.pack(pady=2)
        self.entry_repeat = tk.Entry(parent, width=5)
        self.entry_repeat.pack()
        self.entry_repeat.insert(0, str(self.repeatability_percent))

        # Количество мозаик
        lbl_fragments = tk.Label(parent, text='Количество мозаик')
        lbl_fragments.pack(pady=2)
        self.entry_fragments = tk.Entry(parent, width=5)
        self.entry_fragments.pack()
        self.entry_fragments.insert(0, str(self.fragment_count))

        # Диапазон повторяемости
        lbl_repetition_range = tk.Label(parent, text='Диапазон повторяемости')
        lbl_repetition_range.pack(pady=2)
        self.entry_repetition_min = tk.Entry(parent, width=5)
        self.entry_repetition_min.pack()
        self.entry_repetition_max = tk.Entry(parent, width=5)
        self.entry_repetition_max.pack()
        self.entry_repetition_min.insert(0, str(self.range_repetition[0]))
        self.entry_repetition_max.insert(0, str(self.range_repetition[1]))

        # Дисперсия
        lbl_dispersion = tk.Label(parent, text='Дисперсия')
        lbl_dispersion.pack(pady=2)
        self.dispersion_var = tk.StringVar(value='Маленькие')
        options = ['Маленькие', 'Средние', 'Большие']
        ttk.OptionMenu(parent, self.dispersion_var, options[0], *options).pack()

        # Резентативность
        lbl_repre = tk.Label(parent, text='Репрезентативность')
        lbl_repre.pack(pady=2)
        self.entry_representativity = tk.Entry(parent, width=5)
        self.entry_representativity.pack()
        self.entry_representativity.insert(0, str(self.representativity))

        # Кнопка сохранить
        btn_save = tk.Button(parent, text='Сохранить параметры', command=self.save_mosaic_params)
        btn_save.pack(pady=5)

    def save_mosaic_params(self):
        try:
            for i, (entry_min, entry_max) in enumerate(self.range_entries):
                min_val = int(entry_min.get())
                max_val = int(entry_max.get())
                key = f'Диапазон {i+1}'
                self.range_ranges[key] = (min_val, max_val)
            self.repeatability_percent = float(self.entry_repeat.get())
            self.fragment_count = int(self.entry_fragments.get())
            range_min = int(self.entry_repetition_min.get())
            range_max = int(self.entry_repetition_max.get())
            self.range_repetition = [range_min, range_max]
            self.dispersion_type = self.dispersion_var.get()
            self.representativity = float(self.entry_representativity.get())

            print("Параметры сохранены:", self.range_ranges, self.repeatability_percent,
                  self.fragment_count, self.range_repetition, self.dispersion_type, self.representativity)
        except Exception as e:
            print("Ошибка при сохранении:", e)

    def setup_wave_view(self, parent):
        # Область для видео
        self.video_canvas = tk.Canvas(parent, width=640, height=480, bg='black')
        self.video_canvas.pack(pady=5)

        # Начальная кнопка "Запустить волномер."
        self.btn_start_wave = tk.Button(parent, text='Запустить волномер.', command=self.toggle_wave)
        self.btn_start_wave.pack(pady=2)

        # Создаем отдельную кнопку для остановки - справа
        self.btn_stop_wave = tk.Button(parent, text='Остановить', command=self.stop_wave)
        self.btn_stop_wave.pack(pady=2)
        self.btn_stop_wave.pack_forget()  # изначально скрыт

    def setup_video(self):
        self.current_index = 0

    def update_video_frame(self):
        if not self.update_wave_flag:
            return
        # Генерация кадра
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        for y in range(480):
            for x in range(640):
                rgb_idx = (y * 640 + x + self.current_index) % len(self.rgb_permutations)
                frame[y, x] = np.array(self.rgb_permutations[rgb_idx])
        image = Image.fromarray(frame)
        image_tk = ImageTk.PhotoImage(image)
        self.video_canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.video_canvas.image = image_tk
        self.current_index += 1
        self.root.after(30, self.update_video_frame)

    def toggle_wave(self):
        # Запуск или остановка волномерии
        if not self.update_wave_flag:
            self.update_wave_flag = True
            self.btn_start_wave.pack_forget()  # скрыть кнопку запуска
            self.btn_stop_wave.pack()         # показать кнопку остановки
            self.update_video_frame()          # запуск обновления
        else:
            self.stop_wave()

    def stop_wave(self):
        self.update_wave_flag = False
        self.btn_stop_wave.pack_forget()
        self.btn_start_wave.pack()  # возвращение фаршинг кнопки старт

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
