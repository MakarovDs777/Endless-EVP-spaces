"""
Three Pillars: интегрированный прототип реализации трёх столпов
- Столп 1 (Волнопатернализация): фрагментарная регенерация мозаик с per-channel диапазонами и повторяемостью
- Столп 2 (Волномеризация): спектральный анализ (2D FFT) и вычисление спектральной энергии
- Столп 3 (Самопространственность): реакционно-диффузионная эволюция (Gray-Scott) на основе патернализированного состояния

Интерфейс: главное окно с параметрами, отдельное окно визуализации с тремя изображениями (исходное -> патернализированное -> RD-эволюция) и панелью управления (старт/стоп).

Требует: Python 3, numpy, Pillow, tkinter (стандартная библиотека)
Запуск: python three_pillars.py

Автор: Маша (MashAGPT) — прототип для исследований и экспериментов
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import time
import math
import random

# Если хотите использовать звук — можно добавить pygame
try:
    import pygame
    pygame.mixer.init()
except Exception:
    pygame = None

# --------------------------- УТИЛИТЫ ---------------------------

def pil_from_array(arr):
    """Привести массив uint8 (H,W,3) к PIL.Image"""
    return Image.fromarray(arr.astype(np.uint8))


def normalize01(x):
    xm = x.astype(np.float32)
    xm -= xm.min()
    if xm.max() != 0:
        xm /= xm.max()
    return xm


# --------------------------- СТОЛП 1: ВОЛНОПАТЕРНАЛИЗАЦИЯ ---------------------------

def patternalize_image(img, fragment_count=8, per_channel_ranges=None, repeatability_percent=30, dispersion='Маленькие', representativity=0.5):
    h, w, _ = img.shape
    rng = np.random.RandomState(seed=int(time.time() * 1000) % 2**32)

    if dispersion == 'Маленькие':
        min_size, max_size = 4, 24
    elif dispersion == 'Средние':
        min_size, max_size = 16, 64
    else:
        min_size, max_size = 40, 120

    fragment_count = max(fragment_count, 5)

    if per_channel_ranges is None:
        per_channel_ranges = {0: (0, 255), 1: (0, 255), 2: (0, 255)}

    out = img.copy().astype(np.uint8)
    fragment_map = -np.ones((h, w), dtype=np.int32)
    fragments = []

    attempts = 0
    fid = 0
    while fid < fragment_count and attempts < fragment_count * 30:
        attempts += 1
        # безопасный выбор размеров: учтём, что h или w может быть меньше min_size
        fh_max = max(min(max_size, h), 1)
        fw_max = max(min(max_size, w), 1)
        fh = rng.randint(min(min_size, fh_max), fh_max+1)
        fw = rng.randint(min(min_size, fw_max), fw_max+1)
        y0 = rng.randint(0, max(1, h - fh))
        x0 = rng.randint(0, max(1, w - fw))
        area = fragment_map[y0:y0+fh, x0:x0+fw]
        if np.mean(area == -1) < 0.3:
            continue
        fragment_map[y0:y0+fh, x0:x0+fw] = fid
        fragments.append((fid, x0, y0, fw, fh))
        fid += 1

    if fid < fragment_count:
        empties = np.argwhere(fragment_map == -1)
        rng.shuffle(empties)
        for i in range(min(fragment_count - fid, len(empties))):
            y, x = empties[i]
            fh = rng.randint(1, min(max_size, h - y) + 1)
            fw = rng.randint(1, min(max_size, w - x) + 1)
            fragment_map[y:y+fh, x:x+fw] = fid
            fragments.append((fid, x, y, fw, fh))
            fid += 1

    if np.any(fragment_map == -1):
        empties = np.argwhere(fragment_map == -1)
        for (y, x) in empties:
            best = None
            bestd = 10**9
            for (fid, fx, fy, fw, fh) in fragments:
                cx = fx + fw / 2
                cy = fy + fh / 2
                d = (cx - x)**2 + (cy - y)**2
                if d < bestd:
                    bestd = d
                    best = fid
            fragment_map[y, x] = best if best is not None else 0

    for (fid, fx, fy, fw, fh) in fragments:
        tile = out[fy:fy+fh, fx:fx+fw]
        for ch in range(3):
            lo, hi = per_channel_ranges.get(ch, (0, 255))
            if lo > hi:
                lo, hi = hi, lo
            # Если representativity — работаем с flattened массивом, затем reshpae обратно
            if rng.rand() < representativity:
                base = tile[..., ch].flatten().astype(np.int32)
                samples = rng.randint(lo, hi+1, size=base.shape)
                mix_ratio = 0.5
                newvals = (samples * (1-mix_ratio) + base * mix_ratio).astype(np.uint8)
                # приведение к форме плитки перед присвоением
                newvals = newvals.reshape(tile[..., ch].shape)
            else:
                newvals = rng.randint(lo, hi+1, size=tile[..., ch].shape, dtype=np.uint8)
            tile[..., ch] = newvals

        if repeatability_percent > 0:
            total = tile.shape[0] * tile.shape[1]
            to_repeat = int(total * (repeatability_percent / 100.0))
            # защитимся от нулевого размера
            if to_repeat > 0:
                ys = rng.randint(0, tile.shape[0], size=to_repeat)
                xs = rng.randint(0, tile.shape[1], size=to_repeat)
                for ch in range(3):
                    vals, counts = np.unique(tile[..., ch], return_counts=True)
                    if len(vals) == 0:
                        continue
                    top = vals[np.argmax(counts)]
                    tile[ys, xs, ch] = top

        out[fy:fy+fh, fx:fx+fw] = tile

    return out, fragment_map
# --------------------------- СТОЛП 2: ВОЛНОМЕТРИЗАЦИЯ ---------------------------

def wavemetrize_image(img):
    """
    img: HxWx3 uint8
    Возвращает: спектральное изображение (grayscale HxW uint8), и метрики: total_energy, low_freq_energy_ratio
    """
    h, w, c = img.shape
    gray = np.mean(img.astype(np.float32), axis=2)

    # 2D FFT
    F = np.fft.fftshift(np.fft.fft2(gray))
    mag = np.abs(F)
    # Лог масштаб для визуализации
    mag_log = np.log1p(mag)
    mag_img = 255 * normalize01(mag_log)
    mag_img = mag_img.astype(np.uint8)

    # Энергетические метрики
    total_energy = float(np.sum(mag**2))
    # низкие частоты — центральная область
    cy, cx = h//2, w//2
    r = min(h, w) // 8
    y, x = np.ogrid[:h, :w]
    mask_low = (y - cy)**2 + (x - cx)**2 <= r*r
    low_energy = float(np.sum(mag[mask_low]**2))
    low_ratio = low_energy / total_energy if total_energy != 0 else 0.0

    # Дополнительная простая метрика когерентности: средний градиент
    gx = np.gradient(gray, axis=1)
    gy = np.gradient(gray, axis=0)
    grad_mag = np.sqrt(gx**2 + gy**2)
    grad_mean = float(np.mean(grad_mag))

    metrics = {
        'total_energy': total_energy,
        'low_freq_ratio': low_ratio,
        'grad_mean': grad_mean
    }

    return mag_img, metrics


# --------------------------- СТОЛП 3: САМОПРОСТРАНСТВЕННОСТЬ (Gray-Scott RD) ---------------------------

def gray_scott_step(u, v, Du, Dv, F, k, dt=1.0):
    """One step of Gray-Scott model, vectorized. u,v are float arrays 0..1"""
    lap_u = (np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) + np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1) - 4*u)
    lap_v = (np.roll(v, 1, axis=0) + np.roll(v, -1, axis=0) + np.roll(v, 1, axis=1) + np.roll(v, -1, axis=1) - 4*v)
    uvv = u * v * v
    du = Du * lap_u - uvv + F * (1 - u)
    dv = Dv * lap_v + uvv - (F + k) * v
    u += du * dt
    v += dv * dt
    # clamp
    u = np.clip(u, 0.0, 1.0)
    v = np.clip(v, 0.0, 1.0)
    return u, v


def run_gray_scott_from_image(base_img, steps=200, Du=0.16, Dv=0.08, F=0.035, k=0.065):
    """
    base_img: HxWx3 uint8 — будем использовать для инициализации u,v
    Возвращает последний RGB uint8 image визуализации v (или смесь)
    """
    h, w, _ = base_img.shape
    gray = np.mean(base_img.astype(np.float32), axis=2)
    # инициализация u,v на основе нормализованной яркости
    u = 1.0 - normalize01(gray)
    v = normalize01(gray) * 0.3
    # добавим небольшой шум
    rng = np.random.RandomState(int(time.time() * 1000) % 2**32)
    v += 0.02 * rng.randn(h, w).astype(np.float32)
    v = np.clip(v, 0.0, 1.0)

    for i in range(steps):
        u, v = gray_scott_step(u, v, Du, Dv, F, k, dt=1.0)
    # Конвертация в псевдо-RGB
    out = np.zeros((h, w, 3), dtype=np.uint8)
    out[..., 0] = (255 * normalize01(u)).astype(np.uint8)
    out[..., 1] = (255 * normalize01(v)).astype(np.uint8)
    out[..., 2] = (out[..., 0] // 2 + out[..., 1] // 2)
    return out


# --------------------------- GUI: объединяем столпы ---------------------------

class ThreePillarsApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Three Pillars — Волнопатернализация · Волномеризация · Самопространственность')

        # Параметры
        self.img_size = (256, 256)
        self.base_image = self.generate_base_image(self.img_size)

        # Параметры патернализации
        self.per_channel_ranges = {0:(0,255), 1:(0,255), 2:(0,255)}
        self.repeatability_percent = tk.DoubleVar(value=30.0)
        self.fragment_count = tk.IntVar(value=8)
        self.dispersion_var = tk.StringVar(value='Маленькие')
        self.representativity = tk.DoubleVar(value=0.5)

        # RD params
        self.rd_steps_per_frame = tk.IntVar(value=8)
        self.rd_F = tk.DoubleVar(value=0.035)
        self.rd_k = tk.DoubleVar(value=0.065)

        # Control
        self.is_running = False
        self.visual_window = None
        self.visual_canvases = {}
        self.last_pat_image = None
        self.last_spectrum = None
        self.last_rd = None

        self.build_main_ui()

    def generate_base_image(self, size=(256,256)):
        h,w = size
        # Сделаем плавный градиент + texture
        x = np.linspace(0, 1, w)[None, :]
        y = np.linspace(0, 1, h)[:, None]
        grad = 0.5 * (np.sin(2*math.pi*(x*3 + y*2)) + 1.0)
        texture = 0.2 * np.random.RandomState(0).randn(h,w)
        base = 0.5*grad + 0.5*(1.0 - y)
        base = base + texture
        base = normalize01(base)
        img = np.dstack([base*200 + 20, base*220 + 10, base*255]).astype(np.uint8)
        return img

    def build_main_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(frm)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,8))

        # Параметры патернализации
        ttk.Label(left, text='Параметры Волнопатернализации', font=('Arial', 11, 'bold')).pack(anchor='w')

        ttk.Label(left, text='Фрагментов (>=5)').pack(anchor='w')
        ttk.Entry(left, textvariable=self.fragment_count, width=8).pack(anchor='w')

        ttk.Label(left, text='Повторяемость (%)').pack(anchor='w', pady=(6,0))
        ttk.Scale(left, variable=self.repeatability_percent, from_=0, to=100, orient=tk.HORIZONTAL).pack(anchor='w', fill=tk.X)

        ttk.Label(left, text='Дисперсия').pack(anchor='w', pady=(6,0))
        ttk.OptionMenu(left, self.dispersion_var, 'Маленькие', 'Маленькие', 'Средние', 'Большие').pack(anchor='w')

        ttk.Label(left, text='Репрезентативность').pack(anchor='w', pady=(6,0))
        ttk.Scale(left, variable=self.representativity, from_=0.0, to=1.0, orient=tk.HORIZONTAL).pack(anchor='w', fill=tk.X)

        ttk.Separator(left).pack(fill=tk.X, pady=8)

        ttk.Label(left, text='Параметры волномеризации', font=('Arial', 11, 'bold')).pack(anchor='w')
        ttk.Label(left, text='(спектральный анализ)').pack(anchor='w')

        ttk.Separator(left).pack(fill=tk.X, pady=8)

        ttk.Label(left, text='Параметры самопространственности (RD)', font=('Arial', 11, 'bold')).pack(anchor='w')
        ttk.Label(left, text='Шагов RD за кадр').pack(anchor='w')
        ttk.Entry(left, textvariable=self.rd_steps_per_frame, width=8).pack(anchor='w')
        ttk.Label(left, text='F').pack(anchor='w')
        ttk.Entry(left, textvariable=self.rd_F, width=8).pack(anchor='w')
        ttk.Label(left, text='k').pack(anchor='w')
        ttk.Entry(left, textvariable=self.rd_k, width=8).pack(anchor='w')

        ttk.Separator(left).pack(fill=tk.X, pady=8)

        btn_open = ttk.Button(left, text='Открыть окно визуализации', command=self.open_visual_window)
        btn_open.pack(fill=tk.X, pady=4)

        ttk.Button(left, text='Сгенерировать новый базовый кадр', command=self.regenerate_base).pack(fill=tk.X, pady=2)

        # Правый холст — превью исходного
        right = ttk.Frame(frm)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(right, text='Исходный кадр', font=('Arial', 10, 'bold')).pack()
        self.preview_canvas = tk.Canvas(right, width=256, height=256, bg='black')
        self.preview_canvas.pack(padx=8, pady=8)
        self.show_preview(self.base_image)

    def show_preview(self, arr):
        img = pil_from_array(arr)
        tkimg = ImageTk.PhotoImage(img)
        self.preview_canvas.create_image(0,0,anchor=tk.NW,image=tkimg)
        self.preview_canvas.image = tkimg

    def regenerate_base(self):
        self.base_image = self.generate_base_image(self.img_size)
        self.show_preview(self.base_image)

    def open_visual_window(self):
        if self.visual_window and tk.Toplevel.winfo_exists(self.visual_window):
            self.visual_window.lift()
            return

        self.visual_window = tk.Toplevel(self.root)
        self.visual_window.title('Визуализация столпов')
        self.visual_window.protocol('WM_DELETE_WINDOW', self.close_visual)

        frames = ttk.Frame(self.visual_window)
        frames.pack(fill=tk.BOTH, expand=True)

        # Три холста по горизонтали
        canvas_frame = ttk.Frame(frames)
        canvas_frame.pack()

        # Исходник
        c1f = ttk.Frame(canvas_frame)
        c1f.grid(row=0, column=0, padx=6, pady=6)
        ttk.Label(c1f, text='Исходник').pack()
        c1 = tk.Canvas(c1f, width=256, height=256, bg='black')
        c1.pack()
        self.visual_canvases['orig'] = c1

        # Патернализация
        c2f = ttk.Frame(canvas_frame)
        c2f.grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(c2f, text='Патернализация').pack()
        c2 = tk.Canvas(c2f, width=256, height=256, bg='black')
        c2.pack()
        self.visual_canvases['pat'] = c2

        # Самопространственность (RD)
        c3f = ttk.Frame(canvas_frame)
        c3f.grid(row=0, column=2, padx=6, pady=6)
        ttk.Label(c3f, text='Самопространственность (RD)').pack()
        c3 = tk.Canvas(c3f, width=256, height=256, bg='black')
        c3.pack()
        self.visual_canvases['rd'] = c3

        # Спектр внизу
        spec_frame = ttk.Frame(frames)
        spec_frame.pack()
        ttk.Label(spec_frame, text='Спектр (log-mag) и метрики').pack()
        spec_canvas = tk.Canvas(spec_frame, width=256, height=128, bg='black')
        spec_canvas.pack()
        self.visual_canvases['spec'] = spec_canvas

        # Кнопки управления
        ctrl = ttk.Frame(frames)
        ctrl.pack(pady=6)
        self.btn_start = ttk.Button(ctrl, text='Старт', command=self.start)
        self.btn_start.pack(side=tk.LEFT, padx=4)
        self.btn_stop = ttk.Button(ctrl, text='Стоп', command=self.stop)
        self.btn_stop.pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text='Сделать шаг', command=self.single_step).pack(side=tk.LEFT, padx=4)

        # Метрики
        self.metrics_var = tk.StringVar(value='—')
        ttk.Label(frames, textvariable=self.metrics_var).pack()

        # Инициализация состояний
        self.last_pat_image, _ = patternalize_image(self.base_image,
                                                    fragment_count=self.fragment_count.get(),
                                                    per_channel_ranges=self.per_channel_ranges,
                                                    repeatability_percent=self.repeatability_percent.get(),
                                                    dispersion=self.dispersion_var.get(),
                                                    representativity=self.representativity.get())
        self.last_spectrum, metrics = wavemetrize_image(self.last_pat_image)
        self.last_rd = run_gray_scott_from_image(self.last_pat_image, steps=80, Du=0.16, Dv=0.08, F=self.rd_F.get(), k=self.rd_k.get())

        # показать сразу
        self.update_visuals(force=True)

    def update_visuals(self, force=False):
        if not (self.visual_window and tk.Toplevel.winfo_exists(self.visual_window)):
            return
        # Исходник
        c = self.visual_canvases['orig']
        self._draw_on_canvas(c, self.base_image)
        # Патернализация
        c2 = self.visual_canvases['pat']
        self._draw_on_canvas(c2, self.last_pat_image)
        # RD
        c3 = self.visual_canvases['rd']
        self._draw_on_canvas(c3, self.last_rd)
        # Спектр
        cs = self.visual_canvases['spec']
        spec_rgb = np.dstack([self.last_spectrum]*3)
        self._draw_on_canvas(cs, spec_rgb)

    def _draw_on_canvas(self, canvas, arr):
        img = pil_from_array(arr)
        tkimg = ImageTk.PhotoImage(img.resize((canvas.winfo_width() or arr.shape[1],
                                              canvas.winfo_height() or arr.shape[0])))
        canvas.create_image(0,0,anchor=tk.NW,image=tkimg)
        canvas.image = tkimg

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._run_loop()

    def stop(self):
        self.is_running = False

    def close_visual(self):
        self.stop()
        if self.visual_window:
            try:
                self.visual_window.destroy()
            except Exception:
                pass
            self.visual_window = None

    def single_step(self):
        # Один цикл: патернализация -> спектр -> N шагов RD
        self.last_pat_image, _ = patternalize_image(self.base_image,
                                                    fragment_count=self.fragment_count.get(),
                                                    per_channel_ranges=self.per_channel_ranges,
                                                    repeatability_percent=self.repeatability_percent.get(),
                                                    dispersion=self.dispersion_var.get(),
                                                    representativity=self.representativity.get())
        self.last_spectrum, metrics = wavemetrize_image(self.last_pat_image)
        steps = max(1, self.rd_steps_per_frame.get())
        # применяем RD несколько итераций
        self.last_rd = run_gray_scott_from_image(self.last_pat_image, steps=steps, Du=0.16, Dv=0.08, F=self.rd_F.get(), k=self.rd_k.get())
        # обновляем метрики
        self.metrics_var.set(f"Energy: {metrics['total_energy']:.1f}  LowFreqRatio: {metrics['low_freq_ratio']:.3f}  GradMean: {metrics['grad_mean']:.3f}")
        self.update_visuals()

    def _run_loop(self):
        if not self.is_running:
            return
        # каждая итерация делает патернализацию и несколько RD шагов
        self.last_pat_image, _ = patternalize_image(self.base_image,
                                                    fragment_count=self.fragment_count.get(),
                                                    per_channel_ranges=self.per_channel_ranges,
                                                    repeatability_percent=self.repeatability_percent.get(),
                                                    dispersion=self.dispersion_var.get(),
                                                    representativity=self.representativity.get())
        self.last_spectrum, metrics = wavemetrize_image(self.last_pat_image)
        steps = max(1, self.rd_steps_per_frame.get())
        self.last_rd = run_gray_scott_from_image(self.last_pat_image, steps=steps, Du=0.16, Dv=0.08, F=self.rd_F.get(), k=self.rd_k.get())
        self.metrics_var.set(f"Energy: {metrics['total_energy']:.1f}  LowFreqRatio: {metrics['low_freq_ratio']:.3f}  GradMean: {metrics['grad_mean']:.3f}")
        self.update_visuals()
        # планируем следующий кадр
        if self.visual_window and tk.Toplevel.winfo_exists(self.visual_window):
            self.visual_window.after(200, self._run_loop)
        else:
            self.is_running = False


if __name__ == '__main__':
    root = tk.Tk()
    app = ThreePillarsApp(root)
    root.mainloop()
