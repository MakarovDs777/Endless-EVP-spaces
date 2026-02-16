import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from PIL import Image, ImageTk
from itertools import permutations
import json
import os

class EGFTVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЭГФ Телевизор")
        
        # Основные параметры
        self.window_width = 640
        self.window_height = 480
        
        # Параметры для каждого пикселя (матрица параметров)
        self.pixel_params = None  # Будет 3D массив: [height][width][параметры]
        self.current_pixel_params = None  # Параметры для текущего выбранного пикселя
        
        # Для генерации кадров волнометрии
        self.rgb_permutations = list(permutations(list(range(10)), 3))
        self.current_index = 0
        self.update_wave_flag = False
        
        # Ссылка на окно волнометрии
        self.wave_window = None
        self.wave_canvas = None
        self.btn_stop_wave = None
        
        # Флаг для непрерывной генерации изображения
        self.generate_continuous_flag = False
        
        # Параметры FPS (кадров в секунду)
        self.fps = 10  # Значение по умолчанию
        self.frame_delay = 100  # Задержка в миллисекундах (1000/fps)
        
        # Устанавливаем начальный размер главного окна
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # Собираем интерфейс
        self.setup_interface(self.root)
        
        # Инициализируем параметры пикселей по умолчанию
        self.init_default_pixel_params()
    
    def init_default_pixel_params(self):
        """Инициализация параметров пикселей по умолчанию"""
        # Создаем матрицу параметров для всех пикселей
        self.pixel_params = {
            'width': self.window_width,
            'height': self.window_height,
            'pixels': []
        }
        
        # Заполняем параметрами по умолчанию
        for y in range(self.window_height):
            row = []
            for x in range(self.window_width):
                # Параметры по умолчанию для каждого пикселя
                pixel_data = {
                    'x': x,
                    'y': y,
                    'r_range': [0, 255],  # Диапазон для красного канала
                    'g_range': [0, 255],  # Диапазон для зеленого канала
                    'b_range': [0, 255],  # Диапазон для синего канала
                    'r_value': 0,         # Текущее значение R
                    'g_value': 0,         # Текущее значение G
                    'b_value': 0,         # Текущее значение B
                    'frequency': 1.0,     # Частота обновления
                    'phase': 0.0,         # Фаза
                    'amplitude': 1.0      # Амплитуда
                }
                row.append(pixel_data)
            self.pixel_params['pixels'].append(row)
        
        # Устанавливаем текущие параметры для первого пикселя
        self.current_pixel_params = self.pixel_params['pixels'][0][0].copy()
    
    def setup_interface(self, parent):
        # Фрейм для управления размерами
        size_frame = tk.Frame(parent)
        size_frame.pack(pady=5, fill='x')
        
        # Ширина
        width_frame = tk.Frame(size_frame)
        width_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(width_frame, text='Ширина:').pack(side=tk.LEFT)
        self.entry_width = tk.Entry(width_frame, width=6)
        self.entry_width.pack(side=tk.LEFT, padx=2)
        self.entry_width.insert(0, str(self.window_width))
        
        # Высота
        height_frame = tk.Frame(size_frame)
        height_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(height_frame, text='Высота:').pack(side=tk.LEFT)
        self.entry_height = tk.Entry(height_frame, width=6)
        self.entry_height.pack(side=tk.LEFT, padx=2)
        self.entry_height.insert(0, str(self.window_height))
        
        # Кнопка применения размера
        btn_apply_size = tk.Button(size_frame, text='Применить', command=self.apply_window_size)
        btn_apply_size.pack(side=tk.LEFT, padx=10)
        
        # Разделитель
        separator1 = ttk.Separator(parent, orient='horizontal')
        separator1.pack(fill='x', pady=5)
        
        # Фрейм для управления файлами
        file_frame = tk.Frame(parent)
        file_frame.pack(pady=5, fill='x')
        
        # Кнопка загрузки параметров
        btn_load_params = tk.Button(file_frame, text='Загрузить параметры из файла', command=self.load_pixel_params_from_file)
        btn_load_params.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сохранения параметров
        btn_save_params = tk.Button(file_frame, text='Сохранить параметры в файл', command=self.save_pixel_params_to_file)
        btn_save_params.pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        separator2 = ttk.Separator(parent, orient='horizontal')
        separator2.pack(fill='x', pady=5)
        
        # Фрейм для выбора пикселя
        pixel_select_frame = tk.Frame(parent)
        pixel_select_frame.pack(pady=5, fill='x')
        
        tk.Label(pixel_select_frame, text='Пиксель X:').pack(side=tk.LEFT)
        self.entry_pixel_x = tk.Entry(pixel_select_frame, width=4)
        self.entry_pixel_x.pack(side=tk.LEFT, padx=2)
        self.entry_pixel_x.insert(0, '0')
        
        tk.Label(pixel_select_frame, text='Y:').pack(side=tk.LEFT)
        self.entry_pixel_y = tk.Entry(pixel_select_frame, width=4)
        self.entry_pixel_y.pack(side=tk.LEFT, padx=2)
        self.entry_pixel_y.insert(0, '0')
        
        btn_select_pixel = tk.Button(pixel_select_frame, text='Выбрать пиксель', command=self.select_pixel)
        btn_select_pixel.pack(side=tk.LEFT, padx=10)
        
        # Разделитель
        separator3 = ttk.Separator(parent, orient='horizontal')
        separator3.pack(fill='x', pady=5)
        
        # Фрейм для параметров RGB текущего пикселя
        rgb_frame = tk.LabelFrame(parent, text='Параметры RGB для выбранного пикселя')
        rgb_frame.pack(pady=5, fill='x', padx=10)
        
        # Красный канал
        r_frame = tk.Frame(rgb_frame)
        r_frame.pack(pady=2, fill='x')
        tk.Label(r_frame, text='R диапазон:').pack(side=tk.LEFT)
        self.entry_r_min = tk.Entry(r_frame, width=4)
        self.entry_r_min.pack(side=tk.LEFT, padx=2)
        tk.Label(r_frame, text='-').pack(side=tk.LEFT)
        self.entry_r_max = tk.Entry(r_frame, width=4)
        self.entry_r_max.pack(side=tk.LEFT, padx=2)
        
        # Зеленый канал
        g_frame = tk.Frame(rgb_frame)
        g_frame.pack(pady=2, fill='x')
        tk.Label(g_frame, text='G диапазон:').pack(side=tk.LEFT)
        self.entry_g_min = tk.Entry(g_frame, width=4)
        self.entry_g_min.pack(side=tk.LEFT, padx=2)
        tk.Label(g_frame, text='-').pack(side=tk.LEFT)
        self.entry_g_max = tk.Entry(g_frame, width=4)
        self.entry_g_max.pack(side=tk.LEFT, padx=2)
        
        # Синий канал
        b_frame = tk.Frame(rgb_frame)
        b_frame.pack(pady=2, fill='x')
        tk.Label(b_frame, text='B диапазон:').pack(side=tk.LEFT)
        self.entry_b_min = tk.Entry(b_frame, width=4)
        self.entry_b_min.pack(side=tk.LEFT, padx=2)
        tk.Label(b_frame, text='-').pack(side=tk.LEFT)
        self.entry_b_max = tk.Entry(b_frame, width=4)
        self.entry_b_max.pack(side=tk.LEFT, padx=2)
        
        # Текущие значения RGB
        values_frame = tk.Frame(rgb_frame)
        values_frame.pack(pady=5, fill='x')
        tk.Label(values_frame, text='Текущие значения:').pack(side=tk.LEFT)
        self.label_current_rgb = tk.Label(values_frame, text='[0, 0, 0]')
        self.label_current_rgb.pack(side=tk.LEFT, padx=10)
        
        # Кнопка применения параметров пикселя
        btn_apply_pixel = tk.Button(rgb_frame, text='Применить к пикселю', command=self.apply_pixel_params)
        btn_apply_pixel.pack(pady=5)
        
        # Кнопка применения ко всем пикселям
        btn_apply_all = tk.Button(rgb_frame, text='Применить ко всем пикселям', command=self.apply_to_all_pixels)
        btn_apply_all.pack(pady=2)
        
        # Разделитель
        separator4 = ttk.Separator(parent, orient='horizontal')
        separator4.pack(fill='x', pady=5)
        
        # Кнопки управления
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        
        btn_open_wave = tk.Button(btn_frame, text='Открыть ЭГФ дисплей', command=self.open_wave_window)
        btn_open_wave.pack(side=tk.LEFT, padx=5)
        
        btn_generate = tk.Button(btn_frame, text='Сгенерировать тестовое изображение', command=self.generate_test_image)
        btn_generate.pack(side=tk.LEFT, padx=5)
        
        # Обновляем отображение текущих параметров
        self.update_pixel_params_display()
    
    def apply_window_size(self):
        """Применяет новые размеры окна"""
        try:
            new_width = int(self.entry_width.get())
            new_height = int(self.entry_height.get())
            
            # Проверка на минимальные размеры
            if new_width < 100:
                new_width = 100
                self.entry_width.delete(0, tk.END)
                self.entry_width.insert(0, str(new_width))
            
            if new_height < 100:
                new_height = 100
                self.entry_height.delete(0, tk.END)
                self.entry_height.insert(0, str(new_height))
            
            # Проверка на максимальные размеры
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
            
            # Переинициализируем параметры пикселей с новыми размерами
            self.init_default_pixel_params()
            self.update_pixel_params_display()
            
            print(f"Размер окна изменен: {new_width}x{new_height}")
        except ValueError:
            print("Ошибка: введите корректные числовые значения для ширины и высоты")
    
    def load_pixel_params_from_file(self):
        """Загружает параметры пикселей из текстового файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл с параметрами",
            filetypes=[("Текстовые файлы", "*.txt"), ("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Пробуем загрузить как JSON
            try:
                params = json.loads(content)
                self.load_params_from_json(params)
                print(f"Параметры загружены из JSON файла: {file_path}")
                return
            except json.JSONDecodeError:
                pass
            
            # Пробуем загрузить как текстовый формат
            self.load_params_from_text(content)
            print(f"Параметры загружены из текстового файла: {file_path}")
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
    
    def load_params_from_json(self, params):
        """Загружает параметры из JSON структуры"""
        if 'width' in params and 'height' in params and 'pixels' in params:
            self.window_width = params['width']
            self.window_height = params['height']
            self.pixel_params = params
            
            # Обновляем интерфейс
            self.entry_width.delete(0, tk.END)
            self.entry_width.insert(0, str(self.window_width))
            self.entry_height.delete(0, tk.END)
            self.entry_height.insert(0, str(self.window_height))
            
            # Устанавливаем текущие параметры для первого пикселя
            if (self.window_height > 0 and self.window_width > 0 and 
                len(self.pixel_params['pixels']) > 0 and 
                len(self.pixel_params['pixels'][0]) > 0):
                self.current_pixel_params = self.pixel_params['pixels'][0][0].copy()
                self.update_pixel_params_display()
    
    def load_params_from_text(self, text):
        """Загружает параметры из текстового формата"""
        lines = text.strip().split('\n')
        
        # Простой парсинг текстового формата
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Пример формата: "RGB диапазон генерации для пикселя от 0 до 255 R от 0 до 255 G от 0 до 255 B [R,G,B]"
            # Пока реализуем базовый парсинг
            if 'RGB диапазон' in line:
                # Извлекаем значения
                parts = line.split()
                # Здесь можно добавить более сложную логику парсинга
                print(f"Найдена строка с параметрами RGB: {line}")
    
    def save_pixel_params_to_file(self):
        """Сохраняет параметры пикселей в файл"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить параметры",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Сохраняем в JSON формате
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.pixel_params, file, indent=2, ensure_ascii=False)
            print(f"Параметры сохранены в файл: {file_path}")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
    
    def select_pixel(self):
        """Выбирает пиксель для редактирования"""
        try:
            x = int(self.entry_pixel_x.get())
            y = int(self.entry_pixel_y.get())
            
            # Проверяем границы
            if (0 <= x < self.window_width and 0 <= y < self.window_height and 
                y < len(self.pixel_params['pixels']) and 
                x < len(self.pixel_params['pixels'][0])):
                
                self.current_pixel_params = self.pixel_params['pixels'][y][x].copy()
                self.update_pixel_params_display()
                print(f"Выбран пиксель: X={x}, Y={y}")
            else:
                print(f"Ошибка: координаты пикселя вне диапазона (0-{self.window_width-1}, 0-{self.window_height-1})")
        except ValueError:
            print("Ошибка: введите корректные числовые значения для координат пикселя")
    
    def update_pixel_params_display(self):
        """Обновляет отображение параметров текущего пикселя"""
        if not self.current_pixel_params:
            return
        
        # Обновляем поля ввода
        self.entry_r_min.delete(0, tk.END)
        self.entry_r_min.insert(0, str(self.current_pixel_params['r_range'][0]))
        
        self.entry_r_max.delete(0, tk.END)
        self.entry_r_max.insert(0, str(self.current_pixel_params['r_range'][1]))
        
        self.entry_g_min.delete(0, tk.END)
        self.entry_g_min.insert(0, str(self.current_pixel_params['g_range'][0]))
        
        self.entry_g_max.delete(0, tk.END)
        self.entry_g_max.insert(0, str(self.current_pixel_params['g_range'][1]))
        
        self.entry_b_min.delete(0, tk.END)
        self.entry_b_min.insert(0, str(self.current_pixel_params['b_range'][0]))
        
        self.entry_b_max.delete(0, tk.END)
        self.entry_b_max.insert(0, str(self.current_pixel_params['b_range'][1]))
        
        # Обновляем текущие значения
        current_rgb = f"[{self.current_pixel_params['r_value']}, {self.current_pixel_params['g_value']}, {self.current_pixel_params['b_value']}]"
        self.label_current_rgb.config(text=current_rgb)
    
    def apply_pixel_params(self):
        """Применяет параметры к текущему выбранному пикселю"""
        try:
            # Получаем координаты пикселя
            x = int(self.entry_pixel_x.get())
            y = int(self.entry_pixel_y.get())
            
            # Получаем новые значения диапазонов
            r_min = int(self.entry_r_min.get())
            r_max = int(self.entry_r_max.get())
            g_min = int(self.entry_g_min.get())
            g_max = int(self.entry_g_max.get())
            b_min = int(self.entry_b_min.get())
            b_max = int(self.entry_b_max.get())
            
            # Проверяем границы
            if not (0 <= r_min <= 255 and 0 <= r_max <= 255 and r_min <= r_max):
                raise ValueError("Некорректный диапазон для R")
            if not (0 <= g_min <= 255 and 0 <= g_max <= 255 and g_min <= g_max):
                raise ValueError("Некорректный диапазон для G")
            if not (0 <= b_min <= 255 and 0 <= b_max <= 255 and b_min <= b_max):
                raise ValueError("Некорректный диапазон для B")
            
            # Обновляем параметры пикселя
            self.pixel_params['pixels'][y][x]['r_range'] = [r_min, r_max]
            self.pixel_params['pixels'][y][x]['g_range'] = [g_min, g_max]
            self.pixel_params['pixels'][y][x]['b_range'] = [b_min, b_max]
            
            # Обновляем текущие параметры
            self.current_pixel_params = self.pixel_params['pixels'][y][x].copy()
            
            print(f"Параметры применены к пикселю X={x}, Y={y}")
        except (ValueError, IndexError) as e:
            print(f"Ошибка при применении параметров: {e}")
    
    def apply_to_all_pixels(self):
        """Применяет текущие параметры ко всем пикселям"""
        try:
            # Получаем значения из полей ввода
            r_min = int(self.entry_r_min.get())
            r_max = int(self.entry_r_max.get())
            g_min = int(self.entry_g_min.get())
            g_max = int(self.entry_g_max.get())
            b_min = int(self.entry_b_min.get())
            b_max = int(self.entry_b_max.get())
            
            # Проверяем границы
            if not (0 <= r_min <= 255 and 0 <= r_max <= 255 and r_min <= r_max):
                raise ValueError("Некорректный диапазон для R")
            if not (0 <= g_min <= 255 and 0 <= g_max <= 255 and g_min <= g_max):
                raise ValueError("Некорректный диапазон для G")
            if not (0 <= b_min <= 255 and 0 <= b_max <= 255 and b_min <= b_max):
                raise ValueError("Некорректный диапазон для B")
            
            # Применяем ко всем пикселям
            for y in range(self.window_height):
                for x in range(self.window_width):
                    self.pixel_params['pixels'][y][x]['r_range'] = [r_min, r_max]
                    self.pixel_params['pixels'][y][x]['g_range'] = [g_min, g_max]
                    self.pixel_params['pixels'][y][x]['b_range'] = [b_min, b_max]
            
            print(f"Параметры применены ко всем {self.window_width}x{self.window_height} пикселям")
        except ValueError as e:
            print(f"Ошибка при применении параметров: {e}")
    
    def generate_test_image(self):
        """Генерирует тестовое изображение на основе параметров пикселей"""
        try:
            # Создаем изображение
            img_array = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
            
            # Заполняем изображение на основе параметров пикселей
            for y in range(self.window_height):
                for x in range(self.window_width):
                    pixel = self.pixel_params['pixels'][y][x]
                    
                    # Генерируем случайные значения в заданных диапазонах
                    r_val = np.random.randint(pixel['r_range'][0], pixel['r_range'][1] + 1)
                    g_val = np.random.randint(pixel['g_range'][0], pixel['g_range'][1] + 1)
                    b_val = np.random.randint(pixel['b_range'][0], pixel['b_range'][1] + 1)
                    
                    # Обновляем текущие значения
                    self.pixel_params['pixels'][y][x]['r_value'] = r_val
                    self.pixel_params['pixels'][y][x]['g_value'] = g_val
                    self.pixel_params['pixels'][y][x]['b_value'] = b_val
                    
                    img_array[y, x] = [r_val, g_val, b_val]
            
            # Показываем изображение в новом окне
            self.show_image(img_array, "Тестовое изображение")
            print("Тестовое изображение сгенерировано")
        except Exception as e:
            print(f"Ошибка при генерации изображения: {e}")
    
    def show_image(self, img_array, title):
        """Показывает изображение в новом окне"""
        image_window = tk.Toplevel(self.root)
        image_window.title(title)
        
        # Конвертируем массив в изображение
        img = Image.fromarray(img_array)
        img_tk = ImageTk.PhotoImage(img)
        
        # Создаем канвас для отображения
        canvas = tk.Canvas(image_window, width=img.width, height=img.height)
        canvas.pack()
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk  # Сохраняем ссылку
    
    def open_wave_window(self):
        """Открывает окно ЭГФ дисплея с непрерывной генерацией изображения"""
        if self.wave_window and tk.Toplevel.winfo_exists(self.wave_window):
            self.wave_window.deiconify()
            self.wave_window.lift()
            return
        
        # Создаём окно для ЭГФ дисплея
        self.wave_window = tk.Toplevel(self.root)
        self.wave_window.title("ЭГФ Дисплей - Непрерывная генерация")
        self.wave_window.protocol("WM_DELETE_WINDOW", self.on_wave_close)
        
        # Используем текущие размеры
        wave_width = self.window_width
        wave_height = self.window_height
        
        # Канвас для отображения
        self.wave_canvas = tk.Canvas(self.wave_window, width=wave_width, height=wave_height, bg='black')
        self.wave_canvas.pack(padx=8, pady=8)
        
        # Фрейм для управления FPS
        fps_frame = tk.Frame(self.wave_window)
        fps_frame.pack(pady=(0, 8))
        
        # Кнопка FPS с полем ввода
        tk.Label(fps_frame, text='FPS:').pack(side=tk.LEFT, padx=(0, 5))
        self.entry_fps = tk.Entry(fps_frame, width=5)
        self.entry_fps.pack(side=tk.LEFT, padx=2)
        self.entry_fps.insert(0, str(self.fps))
        
        btn_apply_fps = tk.Button(fps_frame, text='Применить FPS', command=self.apply_fps)
        btn_apply_fps.pack(side=tk.LEFT, padx=5)
        
        # Фрейм для кнопок управления
        ctrl_frame = tk.Frame(self.wave_window)
        ctrl_frame.pack(pady=(0, 8))
        
        btn_start = tk.Button(ctrl_frame, text='Старт', command=self.start_continuous_generation)
        btn_start.pack(side=tk.LEFT, padx=6)
        
        self.btn_stop_wave = tk.Button(ctrl_frame, text='Стоп', command=self.stop_continuous_generation)
        self.btn_stop_wave.pack(side=tk.LEFT, padx=6)
        
        # Сразу запускаем непрерывную генерацию
        self.start_continuous_generation()
    
    def apply_fps(self):
        """Применяет настройки FPS"""
        try:
            new_fps = int(self.entry_fps.get())
            
            # Проверка на допустимые значения
            if new_fps < 1:
                new_fps = 1
                self.entry_fps.delete(0, tk.END)
                self.entry_fps.insert(0, str(new_fps))
            elif new_fps > 60:
                new_fps = 60
                self.entry_fps.delete(0, tk.END)
                self.entry_fps.insert(0, str(new_fps))
            
            # Применяем новые настройки
            self.fps = new_fps
            self.frame_delay = int(1000 / new_fps)  # Конвертируем FPS в миллисекунды
            
            print(f"FPS изменен на: {new_fps} (задержка: {self.frame_delay} мс)")
            
            # Если генерация активна, перезапускаем с новыми параметрами
            if self.generate_continuous_flag:
                self.stop_continuous_generation()
                self.start_continuous_generation()
                
        except ValueError:
            print("Ошибка: введите корректное числовое значение для FPS")
    
    def start_continuous_generation(self):
        """Запускает непрерывную генерацию изображения"""
        if not self.wave_window or not tk.Toplevel.winfo_exists(self.wave_window):
            return
        
        if not self.generate_continuous_flag:
            self.generate_continuous_flag = True
            self.schedule_next_generation()
    
    def stop_continuous_generation(self):
        """Останавливает непрерывную генерацию изображения"""
        self.generate_continuous_flag = False
    
    def on_wave_close(self):
        """Обработчик закрытия окна волнометрии"""
        self.stop_continuous_generation()
        if self.wave_window:
            try:
                self.wave_window.destroy()
            except Exception:
                pass
            self.wave_window = None
            self.wave_canvas = None
            self.btn_stop_wave = None
    
    def schedule_next_generation(self):
        """Планирует следующую генерацию изображения"""
        if self.wave_window and tk.Toplevel.winfo_exists(self.wave_window):
            self.wave_window.after(self.frame_delay, self.update_continuous_frame)
        else:
            self.generate_continuous_flag = False
    
    def update_continuous_frame(self):
        """Обновляет кадр непрерывной генерации"""
        if not self.generate_continuous_flag:
            return
        
        if not (self.wave_window and tk.Toplevel.winfo_exists(self.wave_window) and self.wave_canvas):
            self.generate_continuous_flag = False
            return
        
        # Получаем размеры канваса
        canvas_width = self.wave_canvas.winfo_width()
        canvas_height = self.wave_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = self.window_width
        if canvas_height <= 1:
            canvas_height = self.window_height
        
        # Генерируем тестовое изображение (как в generate_test_image)
        h, w = min(canvas_height, self.window_height), min(canvas_width, self.window_width)
        img_array = np.zeros((h, w, 3), dtype=np.uint8)
        
        for y in range(h):
            for x in range(w):
                if y < len(self.pixel_params['pixels']) and x < len(self.pixel_params['pixels'][0]):
                    pixel = self.pixel_params['pixels'][y][x]
                    
                    # Генерируем случайные значения в заданных диапазонах
                    r_val = np.random.randint(pixel['r_range'][0], pixel['r_range'][1] + 1)
                    g_val = np.random.randint(pixel['g_range'][0], pixel['g_range'][1] + 1)
                    b_val = np.random.randint(pixel['b_range'][0], pixel['b_range'][1] + 1)
                    
                    # Обновляем текущие значения
                    self.pixel_params['pixels'][y][x]['r_value'] = r_val
                    self.pixel_params['pixels'][y][x]['g_value'] = g_val
                    self.pixel_params['pixels'][y][x]['b_value'] = b_val
                    
                    img_array[y, x] = [r_val, g_val, b_val]
        
        # Отображаем кадр
        image = Image.fromarray(img_array)
        image_tk = ImageTk.PhotoImage(image)
        self.wave_canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.wave_canvas.image = image_tk
        
        # Запланировать следующий кадр
        self.schedule_next_generation()

if __name__ == "__main__":
    root = tk.Tk()
    app = EGFTVApp(root)
    root.mainloop()
