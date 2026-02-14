import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk
from itertools import permutations

# pygame импорт оставлен, но он не обязателен для данной демонстрации
try:
    import pygame
    pygame.mixer.init()
except Exception:
    pass

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Параметры мозаики")
        
        # Параметры мозаики (по умолчанию)
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
        
        # Параметры размеров окна (новые параметры)
        self.window_width = 640
        self.window_height = 480
        
        # Для генерации кадров волнометрии
        self.rgb_permutations = list(permutations(list(range(10)), 3))
        self.current_index = 0
        self.update_wave_flag = False
        
        # Ссылка на окно волнометрии и его виджеты
        self.wave_window = None
        self.wave_canvas = None
        self.btn_stop_wave = None
        
        # Устанавливаем начальный размер главного окна
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # Собираем интерфейс параметров
        self.setup_mosaic_params(self.root)
    
    def setup_mosaic_params(self, parent):
        # Секция параметров размеров окна
        lbl_window_size = tk.Label(parent, text='Размеры окна:', font=('Arial', 10, 'bold'))
        lbl_window_size.pack(pady=(10, 5))
        
        frame_width = tk.Frame(parent)
        frame_width.pack(pady=2, anchor='w')
        lbl_width = tk.Label(frame_width, text='Ширина окна:')
        lbl_width.pack(side=tk.LEFT, padx=(0, 6))
        self.entry_width = tk.Entry(frame_width, width=8)
        self.entry_width.pack(side=tk.LEFT, padx=(0, 4))
        self.entry_width.insert(0, str(self.window_width))
        
        frame_height = tk.Frame(parent)
        frame_height.pack(pady=2, anchor='w')
        lbl_height = tk.Label(frame_height, text='Высота окна:')
        lbl_height.pack(side=tk.LEFT, padx=(0, 6))
        self.entry_height = tk.Entry(frame_height, width=8)
        self.entry_height.pack(side=tk.LEFT, padx=(0, 4))
        self.entry_height.insert(0, str(self.window_height))
        
        btn_apply_size = tk.Button(parent, text='Применить размер', command=self.apply_window_size)
        btn_apply_size.pack(pady=(5, 15), anchor='w')
        
        # Разделитель
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
        # Секция параметров мозаики
        lbl_mosaic_params = tk.Label(parent, text='Параметры мозаики:', font=('Arial', 10, 'bold'))
        lbl_mosaic_params.pack(pady=(5, 2))
        
        lbl_ranges = tk.Label(parent, text='Диапазоны случайной генерации:')
        lbl_ranges.pack(pady=(10, 2))
        
        self.range_entries = []
        for key in ['Диапазон 1', 'Диапазон 2', 'Диапазон 3']:
            frame = tk.Frame(parent)
            frame.pack(pady=2, anchor='w')
            lbl = tk.Label(frame, text=key)
            lbl.pack(side=tk.LEFT, padx=(0, 6))
            entry_min = tk.Entry(frame, width=6)
            entry_min.pack(side=tk.LEFT, padx=(0, 4))
            entry_max = tk.Entry(frame, width=6)
            entry_max.pack(side=tk.LEFT)
            entry_min.insert(0, str(self.range_ranges[key][0]))
            entry_max.insert(0, str(self.range_ranges[key][1]))
            self.range_entries.append((entry_min, entry_max))
        
        lbl_repeat = tk.Label(parent, text='Общая повторяемость (%)')
        lbl_repeat.pack(pady=(8, 2), anchor='w')
        self.entry_repeat = tk.Entry(parent, width=6)
        self.entry_repeat.pack(anchor='w')
        self.entry_repeat.insert(0, str(self.repeatability_percent))
        
        lbl_fragments = tk.Label(parent, text='Количество мозаик')
        lbl_fragments.pack(pady=(8, 2), anchor='w')
        self.entry_fragments = tk.Entry(parent, width=6)
        self.entry_fragments.pack(anchor='w')
        self.entry_fragments.insert(0, str(self.fragment_count))
        
        lbl_repetition_range = tk.Label(parent, text='Диапазон повторяемости (min/max)')
        lbl_repetition_range.pack(pady=(8, 2), anchor='w')
        frame_rep = tk.Frame(parent)
        frame_rep.pack(anchor='w')
        self.entry_repetition_min = tk.Entry(frame_rep, width=6)
        self.entry_repetition_min.pack(side=tk.LEFT, padx=(0, 4))
        self.entry_repetition_max = tk.Entry(frame_rep, width=6)
        self.entry_repetition_max.pack(side=tk.LEFT)
        self.entry_repetition_min.insert(0, str(self.range_repetition[0]))
        self.entry_repetition_max.insert(0, str(self.range_repetition[1]))
        
        lbl_dispersion = tk.Label(parent, text='Дисперсия')
        lbl_dispersion.pack(pady=(8, 2), anchor='w')
        self.dispersion_var = tk.StringVar(value='Маленькие')
        options = ['Маленькие', 'Средние', 'Большие']
        ttk.OptionMenu(parent, self.dispersion_var, options[0], *options).pack(anchor='w')
        
        lbl_repre = tk.Label(parent, text='Репрезентативность')
        lbl_repre.pack(pady=(8, 2), anchor='w')
        self.entry_representativity = tk.Entry(parent, width=6)
        self.entry_representativity.pack(anchor='w')
        self.entry_representativity.insert(0, str(self.representativity))
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=12)
        btn_save = tk.Button(btn_frame, text='Сохранить параметры', command=self.save_mosaic_params)
        btn_save.pack(side=tk.LEFT, padx=6)
        btn_open_wave = tk.Button(btn_frame, text='Открыть Волномер', command=self.open_wave_window)
        btn_open_wave.pack(side=tk.LEFT, padx=6)
    
    def apply_window_size(self):
        """Применяет новые размеры окна"""
        try:
            new_width = int(self.entry_width.get())
            new_height = int(self.entry_height.get())
            
            # Проверка на минимальные размеры
            if new_width < 300:
                new_width = 300
                self.entry_width.delete(0, tk.END)
                self.entry_width.insert(0, str(new_width))
            
            if new_height < 200:
                new_height = 200
                self.entry_height.delete(0, tk.END)
                self.entry_height.insert(0, str(new_height))
            
            # Проверка на максимальные размеры (опционально)
            if new_width > 1920:
                new_width = 1920
                self.entry_width.delete(0, tk.END)
                self.entry_width.insert(0, str(new_width))
            
            if new_height > 1080:
                new_height = 1080
                self.entry_height.delete(0, tk.END)
                self.entry_height.insert(0, str(new_height))
            
            # Применяем новые размеры
            self.window_width = new_width
            self.window_height = new_height
            self.root.geometry(f"{new_width}x{new_height}")
            
            print(f"Размер окна изменен: {new_width}x{new_height}")
            
        except ValueError:
            print("Ошибка: введите корректные числовые значения для ширины и высоты")
            # Восстанавливаем предыдущие значения
            self.entry_width.delete(0, tk.END)
            self.entry_width.insert(0, str(self.window_width))
            self.entry_height.delete(0, tk.END)
            self.entry_height.insert(0, str(self.window_height))
    
    def save_mosaic_params(self):
        """Сохраняет все параметры, включая размеры окна"""
        try:
            # Сохраняем параметры размеров окна
            self.apply_window_size()  # Это также обновит self.window_width и self.window_height
            
            # Сохраняем параметры мозаики
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
            
            print("Параметры сохранены:")
            print(f"  Размер окна: {self.window_width}x{self.window_height}")
            print(f"  Диапазоны: {self.range_ranges}")
            print(f"  Повторяемость: {self.repeatability_percent}%")
            print(f"  Количество мозаик: {self.fragment_count}")
            print(f"  Диапазон повторяемости: {self.range_repetition}")
            print(f"  Дисперсия: {self.dispersion_type}")
            print(f"  Репрезентативность: {self.representativity}")
            
        except Exception as e:
            print("Ошибка при сохранении:", e)
    
    def open_wave_window(self):
        # Если окно уже открыто — просто вывести на передний план
        if self.wave_window and tk.Toplevel.winfo_exists(self.wave_window):
            self.wave_window.deiconify()
            self.wave_window.lift()
            return
        
        # Создаём Toplevel окно для волнометрии
        self.wave_window = tk.Toplevel(self.root)
        self.wave_window.title("Волномеризация")
        self.wave_window.protocol("WM_DELETE_WINDOW", self.on_wave_close)
        
        # Используем текущие размеры окна для волнометра
        wave_width = self.window_width
        wave_height = self.window_height
        
        # Канвас для видео
        self.wave_canvas = tk.Canvas(self.wave_window, width=wave_width, height=wave_height, bg='black')
        self.wave_canvas.pack(padx=8, pady=8)
        
        # Кнопки управления внутри окна волнометрии
        ctrl_frame = tk.Frame(self.wave_window)
        ctrl_frame.pack(pady=(0, 8))
        btn_start = tk.Button(ctrl_frame, text='Старт', command=self.start_wave)
        btn_start.pack(side=tk.LEFT, padx=6)
        self.btn_stop_wave = tk.Button(ctrl_frame, text='Стоп', command=self.stop_wave)
        self.btn_stop_wave.pack(side=tk.LEFT, padx=6)
        
        # Сразу запускаем обновление кадров
        self.start_wave()
    
    def start_wave(self):
        if not self.wave_window or not tk.Toplevel.winfo_exists(self.wave_window):
            return
        if not self.update_wave_flag:
            self.update_wave_flag = True
            self.schedule_next_frame()
    
    def stop_wave(self):
        self.update_wave_flag = False
    
    def on_wave_close(self):
        # Останавливаем обновление и закрываем окно
        self.stop_wave()
        if self.wave_window:
            try:
                self.wave_window.destroy()
            except Exception:
                pass
        self.wave_window = None
        self.wave_canvas = None
        self.btn_stop_wave = None
    
    def schedule_next_frame(self):
        # Используем after от окна волнометрии если оно существует, иначе от root
        if self.wave_window and tk.Toplevel.winfo_exists(self.wave_window):
            self.wave_window.after(30, self.update_video_frame)
        else:
            # Если окно закрыто — выключаем флаг
            self.update_wave_flag = False
    
    def update_video_frame(self):
        if not self.update_wave_flag:
            return
        if not (self.wave_window and tk.Toplevel.winfo_exists(self.wave_window) and self.wave_canvas):
            # окно было закрыто извне
            self.update_wave_flag = False
            return
        
        # Получаем текущие размеры канваса
        canvas_width = self.wave_canvas.winfo_width()
        canvas_height = self.wave_canvas.winfo_height()
        
        # Если размеры не определены, используем значения по умолчанию
        if canvas_width <= 1:
            canvas_width = self.window_width
        if canvas_height <= 1:
            canvas_height = self.window_height
        
        # Генерация простого кадра
        h, w = canvas_height, canvas_width
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        total_perm = len(self.rgb_permutations)
        
        for y in range(h):
            for x in range(w):
                rgb_idx = (y * w + x + self.current_index) % total_perm
                # permutations дают значения 0..9, оставляем так же как в исходнике
                frame[y, x] = np.array(self.rgb_permutations[rgb_idx], dtype=np.uint8)
        
        image = Image.fromarray(frame)
        image_tk = ImageTk.PhotoImage(image)
        self.wave_canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        # сохранить ссылку чтобы изображение не собиралось сборщиком мусора
        self.wave_canvas.image = image_tk
        self.current_index += 1
        
        # Запланировать следующий кадр
        self.schedule_next_frame()

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
