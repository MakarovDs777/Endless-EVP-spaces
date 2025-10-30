import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFilter
from itertools import permutations
import time
import math

# Простой Tkinter-приложение реализует метрики из трёх столпов
# Требования: Python 3.7+, Pillow, numpy

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Параметры мозаики — Волномер/Самопространственность")

        # Параметры мозаики (по умолчанию)
        self.range_ranges = {
            'Диапазон 1': (0, 255),
            'Диапазон 2': (0, 255),
            'Диапазон 3': (0, 255)
        }
        self.repeatability_percent = 50.0
        self.fragment_count = 5
        self.range_repetition = [30, 60]
        self.dispersion_type = 'Маленькие'
        self.representativity = 0.5

        # Для генерации кадров
        self.h, self.w = 360, 480
        self.current_index = 0
        self.update_wave_flag = False

        # Метрики и история
        self.history_len = 40
        self.metric_history = {
            'global_mean': [],
            'emergence_score': [],
            'coherence': []
        }
        self.known_mosaic_signatures = set()

        # Интерфейс
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(main_frame)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        right = tk.Frame(main_frame)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.setup_mosaic_params(left)

        # Область предпросмотра + индикаторы
        preview_frame = tk.Frame(right)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        self.wave_canvas = tk.Canvas(preview_frame, width=self.w, height=self.h, bg='black')
        self.wave_canvas.pack(side=tk.TOP)

        # Панель метрик
        metrics_frame = tk.Frame(preview_frame)
        metrics_frame.pack(side=tk.TOP, fill=tk.X, pady=(8,0))

        self.metrics_labels = {}
        labels = [
            'W: Диапазоны', 'W: Повторяемость %', 'W: Фрагментарность', 'W: Диапазон повт.', 'W: Дисперсия', 'W: Репрезентативность',
            'V: Коэрентность', 'V: Самоподобие', 'V: Предсказуемость', 'V: Сила аттрактора', 'V: Внутренняя размерность',
            'S: Каталитическое замыкание', 'S: Устойчивость', 'S: Модулярность', 'S: Новизна', 'S: Поток энергии', 'Emergence'
        ]
        grid_cols = 2
        for i, name in enumerate(labels):
            lbl = tk.Label(metrics_frame, text=f"{name}: ", anchor='w')
            val = tk.Label(metrics_frame, text='—', width=12, anchor='w')
            lbl.grid(row=i//grid_cols, column=(i%grid_cols)*2, sticky='w')
            val.grid(row=i//grid_cols, column=(i%grid_cols)*2+1, sticky='w')
            self.metrics_labels[name] = val

        ctrl_frame = tk.Frame(preview_frame)
        ctrl_frame.pack(side=tk.TOP, pady=6)
        btn_start = tk.Button(ctrl_frame, text='Старт', command=self.start_wave)
        btn_start.pack(side=tk.LEFT, padx=6)
        btn_stop = tk.Button(ctrl_frame, text='Стоп', command=self.stop_wave)
        btn_stop.pack(side=tk.LEFT, padx=6)
        btn_perturb = tk.Button(ctrl_frame, text='Импульс (шум)', command=self.inject_perturbation)
        btn_perturb.pack(side=tk.LEFT, padx=6)

        # Локальное окно волнометрии не требуется — всё в одном окне

    def setup_mosaic_params(self, parent):
        lbl_ranges = tk.Label(parent, text='Диапазоны случайной генерации:')
        lbl_ranges.pack(pady=(10, 2), anchor='w')

        self.range_entries = []
        for key in ['Диапазон 1', 'Диапазон 2', 'Диапазон 3']:
            frame = tk.Frame(parent)
            frame.pack(pady=2, anchor='w')
            lbl = tk.Label(frame, text=key)
            lbl.pack(side=tk.LEFT, padx=(0,6))
            entry_min = tk.Entry(frame, width=6)
            entry_min.pack(side=tk.LEFT, padx=(0,4))
            entry_max = tk.Entry(frame, width=6)
            entry_max.pack(side=tk.LEFT)
            entry_min.insert(0, str(self.range_ranges[key][0]))
            entry_max.insert(0, str(self.range_ranges[key][1]))
            self.range_entries.append((entry_min, entry_max))

        lbl_repeat = tk.Label(parent, text='Общая повторяемость (%)')
        lbl_repeat.pack(pady=(8,2), anchor='w')
        self.entry_repeat = tk.Entry(parent, width=6)
        self.entry_repeat.pack(anchor='w')
        self.entry_repeat.insert(0, str(self.repeatability_percent))

        lbl_fragments = tk.Label(parent, text='Количество мозаик')
        lbl_fragments.pack(pady=(8,2), anchor='w')
        self.entry_fragments = tk.Entry(parent, width=6)
        self.entry_fragments.pack(anchor='w')
        self.entry_fragments.insert(0, str(self.fragment_count))

        lbl_repetition_range = tk.Label(parent, text='Диапазон повторяемости (min/max)')
        lbl_repetition_range.pack(pady=(8,2), anchor='w')
        frame_rep = tk.Frame(parent)
        frame_rep.pack(anchor='w')
        self.entry_repetition_min = tk.Entry(frame_rep, width=6)
        self.entry_repetition_min.pack(side=tk.LEFT, padx=(0,4))
        self.entry_repetition_max = tk.Entry(frame_rep, width=6)
        self.entry_repetition_max.pack(side=tk.LEFT)
        self.entry_repetition_min.insert(0, str(self.range_repetition[0]))
        self.entry_repetition_max.insert(0, str(self.range_repetition[1]))

        lbl_dispersion = tk.Label(parent, text='Дисперсия')
        lbl_dispersion.pack(pady=(8,2), anchor='w')
        self.dispersion_var = tk.StringVar(value='Маленькие')
        options = ['Маленькие', 'Средние', 'Большие']
        ttk.OptionMenu(parent, self.dispersion_var, options[0], *options).pack(anchor='w')

        lbl_repre = tk.Label(parent, text='Репрезентативность (0..1)')
        lbl_repre.pack(pady=(8,2), anchor='w')
        self.entry_representativity = tk.Entry(parent, width=6)
        self.entry_representativity.pack(anchor='w')
        self.entry_representativity.insert(0, str(self.representativity))

        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=12)
        btn_save = tk.Button(btn_frame, text='Сохранить параметры', command=self.save_mosaic_params)
        btn_save.pack(side=tk.LEFT, padx=6)

    def save_mosaic_params(self):
        try:
            for i, (entry_min, entry_max) in enumerate(self.range_entries):
                min_val = int(entry_min.get())
                max_val = int(entry_max.get())
                key = f'Диапазон {i+1}'
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                self.range_ranges[key] = (min_val, max_val)
            self.repeatability_percent = float(self.entry_repeat.get())
            self.fragment_count = max(1, int(self.entry_fragments.get()))
            range_min = int(self.entry_repetition_min.get())
            range_max = int(self.entry_repetition_max.get())
            if range_min > range_max:
                range_min, range_max = range_max, range_min
            self.range_repetition = [range_min, range_max]
            self.dispersion_type = self.dispersion_var.get()
            self.representativity = float(self.entry_representativity.get())
            print("Параметры сохранены:", self.range_ranges, self.repeatability_percent,
                  self.fragment_count, self.range_repetition, self.dispersion_type, self.representativity)
        except Exception as e:
            print("Ошибка при сохранении:", e)

    def start_wave(self):
        if not self.update_wave_flag:
            self.update_wave_flag = True
            self.schedule_next_frame()

    def stop_wave(self):
        self.update_wave_flag = False

    def inject_perturbation(self):
        # добавим запись в истории, чтобы система увидела "шок"
        self.metric_history['global_mean'].append((time.time(), 'perturb'))
        print("Импульс введён")

    def schedule_next_frame(self):
        self.root.after(80, self.update_video_frame)

    # --- разделение на мозаики ---
    def tile_mosaics(self, frame):
        n = max(1, self.fragment_count)
        # выбираем сетку, близкую к квадрату
        cols = int(math.ceil(math.sqrt(n)))
        rows = int(math.ceil(n / cols))
        h, w = frame.shape[:2]
        tile_h = h // rows
        tile_w = w // cols
        mosaics = []
        coords = []
        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= n:
                    break
                y0 = r * tile_h
                x0 = c * tile_w
                y1 = (r + 1) * tile_h if r < rows - 1 else h
                x1 = (c + 1) * tile_w if c < cols - 1 else w
                mosaics.append(frame[y0:y1, x0:x1].copy())
                coords.append((y0, x0, y1, x1))
                idx += 1
        return mosaics, coords

    # --- метрики волнопатернализации ---
    def calc_w_patternalization(self, frame, mosaics):
        # 1) диапазоны для каждого мозаика
        ranges = []
        for m in mosaics:
            r = tuple((int(m[..., ch].min()), int(m[..., ch].max())) for ch in range(3))
            ranges.append(r)
        # 2) общая повторяемость: находим самый частый RGB триплет в кадре
        flat = frame.reshape(-1, 3)
        # делаем кодировку RGB->int
        keys = flat[:,0].astype(np.uint32) << 16 | flat[:,1].astype(np.uint32) << 8 | flat[:,2].astype(np.uint32)
        vals, counts = np.unique(keys, return_counts=True)
        top_freq = 0
        top_percent = 0.0
        if len(counts)>0:
            top_freq = int(vals[np.argmax(counts)])
            top_percent = float(counts.max()) / keys.size * 100.0
        # 3) фрагментарность
        frag_sizes = [m.shape[0]*m.shape[1] for m in mosaics]
        # 4) диапазонность повторяемости: среднее расстояние между повторами самого частого цвета
        spread_list = []
        if len(counts)>0:
            most_key = vals[np.argmax(counts)]
            positions = np.where(keys==most_key)[0]
            if len(positions)>1:
                gaps = np.diff(np.sort(positions))
                spread_list = [int(gaps.mean()), int(gaps.std())]
            else:
                spread_list = [keys.size, 0]
        else:
            spread_list = [keys.size, 0]
        # 5) дисперсность фрагментов: категориальное распределение
        bins = {'Маленькие':(1,30), 'Средние':(30,60), 'Большие':(60,90)}
        chosen = bins.get(self.dispersion_type, (1,30))
        dispersion_counts = sum(1 for s in frag_sizes if chosen[0] <= s <= chosen[1])
        # 6) репрезентативность: KL divergence между выборкой (мозаики) и полным кадром
        # считаем гистограммы для каждого канала
        hist_full, _ = np.histogramdd(flat, bins=(8,8,8), range=((0,256),(0,256),(0,256)))
        hist_full = hist_full.astype(float).ravel() + 1e-9
        # берем случайную часть мозаик (по репрезентативности)
        sample = []
        n_sample = max(1, int(len(mosaics) * self.representativity))
        inds = np.random.choice(len(mosaics), n_sample, replace=False)
        for i in inds:
            sample.append(mosaics[i].reshape(-1,3))
        samp_flat = np.vstack(sample) if len(sample)>0 else flat
        hist_s, _ = np.histogramdd(samp_flat, bins=(8,8,8), range=((0,256),(0,256),(0,256)))
        hist_s = hist_s.astype(float).ravel() + 1e-9
        # KL(divergence)
        kl = float(np.sum(hist_s * np.log(hist_s / hist_full)))

        results = {
            'ranges': ranges,
            'top_percent': top_percent,
            'frag_sizes': frag_sizes,
            'spread': spread_list,
            'dispersion_count': dispersion_counts,
            'kl': kl
        }
        return results

    # --- волнометризация ---
    def calc_volumetrization(self, frame, mosaics, prev_frame=None):
        # 1) коэрентность: корреляция средних цветов соседних мозаик
        means = [m.reshape(-1,3).mean(axis=0) for m in mosaics]
        means = np.array(means)
        if len(means) > 1:
            # pairwise корреляции (на векторах RGB)
            corrs = []
            for i in range(len(means)):
                for j in range(i+1, len(means)):
                    a = means[i] - means[i].mean()
                    b = means[j] - means[j].mean()
                    denom = (np.linalg.norm(a)*np.linalg.norm(b)+1e-9)
                    corrs.append(float(np.dot(a,b)/denom))
            coherence = float(np.mean(corrs))
        else:
            coherence = 1.0

        # 2) самоподобие: downscale и сравнение гистограмм
        def hist3d(img, bins=8):
            f = img.reshape(-1,3)
            h, _ = np.histogramdd(f, bins=(bins,bins,bins), range=((0,256),(0,256),(0,256)))
            h = h.ravel().astype(float)
            h /= (h.sum()+1e-9)
            return h
        h_full = hist3d(frame, bins=6)
        small = frame[::2, ::2]
        h_small = hist3d(small, bins=6)
        self_similarity = float(np.corrcoef(h_full, h_small)[0,1]) if np.isfinite(np.corrcoef(h_full, h_small)[0,1]) else 0.0

        # 3) предсказуемость: если есть prev_frame, предсказуемость = 1 - MSE/Var
        predictability = 0.0
        if prev_frame is not None:
            mse = float(np.mean((frame.astype(float)-prev_frame.astype(float))**2))
            var = float(np.var(prev_frame.astype(float))) + 1e-9
            predictability = max(0.0, 1.0 - mse/var)
        # 4) сила аттрактора: топ-variance по мозаикам
        var_m = [float(m.reshape(-1,3).var()) for m in mosaics]
        attractor_strength = float(max(var_m)) if len(var_m)>0 else 0.0
        # 5) внутренняя размерность: PCA (SVD) на векторах мозаик
        X = np.vstack([m.reshape(-1,3).mean(axis=0) for m in mosaics]) if len(mosaics)>0 else np.zeros((1,3))
        Xc = X - X.mean(axis=0)
        try:
            u, s, vh = np.linalg.svd(Xc, full_matrices=False)
            total = (s**2).sum()
            cum = np.cumsum(s**2) / (total+1e-9)
            intrinsic = int(np.searchsorted(cum, 0.95) + 1)
        except Exception:
            intrinsic = 1

        results = {
            'coherence': coherence,
            'self_similarity': self_similarity,
            'predictability': predictability,
            'attractor_strength': attractor_strength,
            'intrinsic_dim': intrinsic
        }
        return results

    # --- самопространственность ---
    def calc_selfspatiality(self, frame, mosaics):
        n = len(mosaics)
        # build adjacency by correlation between mosaic mean vectors
        means = [m.reshape(-1,3).mean(axis=0) for m in mosaics]
        means = np.array(means)
        adj = np.zeros((n,n), dtype=int)
        for i in range(n):
            for j in range(i+1, n):
                a = means[i] - means[i].mean()
                b = means[j] - means[j].mean()
                denom = (np.linalg.norm(a)*np.linalg.norm(b)+1e-9)
                corr = float(np.dot(a,b)/denom)
                if corr > 0.6:
                    adj[i,j]=1
                    adj[j,i]=1
        # Catalytic closure: count nodes in triangles
        tri = np.linalg.matrix_power(adj, 3)
        triangle_count = int(np.trace(tri) // 6) if n>2 else 0
        nodes_in_triangles = set()
        if triangle_count>0:
            # brute force find triangles
            for i in range(n):
                for j in range(i+1,n):
                    if adj[i,j]:
                        for k in range(j+1,n):
                            if adj[j,k] and adj[k,i]:
                                nodes_in_triangles.update([i,j,k])
        cat_closure_frac = float(len(nodes_in_triangles))/n if n>0 else 0.0

        # Robustness: оценка стабильности (используем историю global_mean)
        gm_hist = [v for (t,v) in self.metric_history['global_mean'] if isinstance(v,float)]
        rob = 1.0
        if len(gm_hist) > 3:
            rob = 1.0 / (1.0 + np.std(gm_hist))

        # Modularity: count connected components
        components = self.count_components(adj)
        modularity_like = 1.0 / components if components>0 else 1.0

        # Novelty: сколько новых сигнатур у мозаик
        new = 0
        sigs = []
        for m in mosaics:
            h = tuple(np.round(m.reshape(-1,3).mean(axis=0)).astype(int).tolist())
            sigs.append(h)
            if h not in self.known_mosaic_signatures:
                new += 1
                self.known_mosaic_signatures.add(h)

        novelty_rate = float(new)/max(1,len(mosaics))

        # Energy flux: локальная энергия и её градиент
        energies = np.array([float((m.astype(float)**2).sum()) for m in mosaics])
        if len(energies)>1:
            flux = float(np.mean(np.abs(np.diff(energies))))
        else:
            flux = 0.0

        results = {
            'catalytic_frac': cat_closure_frac,
            'robustness': rob,
            'modularity': modularity_like,
            'novelty': novelty_rate,
            'flux': flux
        }
        return results

    def count_components(self, adj):
        n = adj.shape[0]
        visited = [False]*n
        def dfs(u):
            stack = [u]
            comp = []
            while stack:
                v = stack.pop()
                if not visited[v]:
                    visited[v]=True
                    comp.append(v)
                    neigh = np.where(adj[v]>0)[0].tolist()
                    for x in neigh:
                        if not visited[x]:
                            stack.append(x)
            return comp
        comps = 0
        for i in range(n):
            if not visited[i]:
                dfs(i)
                comps += 1
        return comps

    # Основной цикл генерации кадров + расчёт метрик
    def update_video_frame(self):
        if not self.update_wave_flag:
            return

        # увеличиваем счётчик кадров — используется для детерминированной генерации декоративных элементов
        self.current_index += 1

        # Генерируем кадр, используя диапазоны и фрагменты
        frame = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        # tile layout чтобы применять диапазоны по мозаикам
        n = max(1, self.fragment_count)
        cols = int(math.ceil(math.sqrt(n)))
        rows = int(math.ceil(n / cols))
        tile_h = self.h // rows
        tile_w = self.w // cols

        # prepare ranges per mosaic cycling through user ranges
        range_keys = list(self.range_ranges.keys())

        for r in range(rows):
            for c in range(cols):
                idx = r*cols + c
                y0 = r*tile_h
                x0 = c*tile_w
                y1 = (r+1)*tile_h if r<rows-1 else self.h
                x1 = (c+1)*tile_w if c<cols-1 else self.w

                # Если индекс меньше n — используем пользовательскую логику, иначе заполняем «вспомогательную» плитку
                if idx < n:
                    rng = self.range_ranges[range_keys[idx % len(range_keys)]]
                else:
                    # Для лишних ячеек: используем смешение диапазонов, чтобы не оставлять черных полей
                    rng_a = self.range_ranges[range_keys[(idx - n) % len(range_keys)]]
                    rng_b = self.range_ranges[range_keys[(idx - n + 1) % len(range_keys)]]
                    # усредним диапазоны
                    rng = (min(rng_a[0], rng_b[0]), max(rng_a[1], rng_b[1]))

                # создаём мозаичное заполнение с учётом repeatability: часть пикселей будет повторяться
                h_chunk = y1-y0
                w_chunk = x1-x0
                total = h_chunk*w_chunk
                # базовый шум
                local = np.random.randint(rng[0], rng[1]+1, size=(h_chunk, w_chunk, 3), dtype=np.uint8)

                # воспроизводимость: выбираем некоторый шаблон и копируем его в random positions
                p = max(0.0, min(1.0, self.repeatability_percent/100.0))
                if p>0.01:
                    # увеличил размер шаблона, чтобы было более заметно
                    pat_h = max(1, int(h_chunk * np.clip(p, 0.02, 0.6)))
                    pat_w = max(1, int(w_chunk * np.clip(p, 0.02, 0.6)))
                    pat = local[:pat_h, :pat_w].copy()
                    # вставляем копии в несколько положений
                    for _ in range(1 + int(p*8)):
                        yy = np.random.randint(0, max(1, h_chunk-pat_h))
                        xx = np.random.randint(0, max(1, w_chunk-pat_w))
                        local[yy:yy+pat_h, xx:xx+pat_w] = pat

                # Добавим видимые декоративные элементы (только штриховка/сетка/размытие) в каждой плитке
                try:
                    rs = np.random.RandomState(self.current_index * 1009 + idx * 97)
                    img_tile = Image.fromarray(local, mode='RGB')
                    draw = ImageDraw.Draw(img_tile, 'RGBA')

                    # лёгкая штриховка/сетка (оставлена по запросу; эллипсы и линии удалены)
                    if rs.randint(0,1)==0:
                        step = max(6, min(w_chunk, h_chunk)//10)
                        for xx in range(0, w_chunk, step):
                            draw.line((xx, 0, xx, h_chunk), fill=(0,0,0,12))
                        for yy in range(0, h_chunk, step):
                            draw.line((0, yy, w_chunk, yy), fill=(0,0,0,12))

                    # немного размытия
                    blur_r = rs.uniform(0.0, 1.0)
                    if blur_r > 0.001:
                        img_tile = img_tile.filter(ImageFilter.GaussianBlur(radius=blur_r))

                    local = np.array(img_tile, dtype=np.uint8)
                except Exception:
                    # если что-то пошло не так — оставим чистый шум
                    pass

                frame[y0:y1, x0:x1] = local

        # Иногда добавляем структурный шум, чтобы наблюдать фазовые переходы
        if np.random.rand() < 0.02:
            noise = np.random.randint(0, 256, size=(self.h, self.w, 3), dtype=np.uint8)
            alpha = np.random.rand()*0.5
            frame = (frame.astype(float)*(1-alpha) + noise.astype(float)*alpha).astype(np.uint8)

        # Получаем предыдущий кадр из истории если есть
        prev_frame = None
        if hasattr(self, 'last_frame'):
            prev_frame = self.last_frame
        self.last_frame = frame.copy()

        # разбиваем
        mosaics, coords = self.tile_mosaics(frame)

        # расчёт метрик
        w_metrics = self.calc_w_patternalization(frame, mosaics)
        v_metrics = self.calc_volumetrization(frame, mosaics, prev_frame)
        s_metrics = self.calc_selfspatiality(frame, mosaics)

        # emergent score (комбинированная метрика)
        emergence = (s_metrics['novelty']*0.6 + s_metrics['catalytic_frac']*0.9 + v_metrics['self_similarity']*0.4) * (1.0/(1.0+v_metrics['predictability']))

        # сохраняем исторические величины
        gm = float(frame.astype(float).mean())
        self.metric_history['global_mean'].append((time.time(), gm))
        if len(self.metric_history['global_mean'])>self.history_len:
            self.metric_history['global_mean'].pop(0)
        self.metric_history['emergence_score'].append(emergence)
        if len(self.metric_history['emergence_score'])>self.history_len:
            self.metric_history['emergence_score'].pop(0)

        # Обновляем UI
        # изображение
        image = Image.fromarray(frame)
        image_tk = ImageTk.PhotoImage(image.resize((self.w, self.h)))
        self.wave_canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.wave_canvas.image = image_tk

        # метрики текста
        self.metrics_labels['W: Диапазоны'].config(text=f"{len(w_metrics['ranges'])} зон")
        self.metrics_labels['W: Повторяемость %'].config(text=f"{w_metrics['top_percent']:.1f}%")
        self.metrics_labels['W: Фрагментарность'].config(text=f"{len(w_metrics['frag_sizes'])} ({np.mean(w_metrics['frag_sizes']):.0f}px)")
        self.metrics_labels['W: Диапазон повт.'].config(text=f"avg_gap={w_metrics['spread'][0]}")
        self.metrics_labels['W: Дисперсия'].config(text=f"count={w_metrics['dispersion_count']}")
        self.metrics_labels['W: Репрезентативность'].config(text=f"KL={w_metrics['kl']:.3f}")

        self.metrics_labels['V: Коэрентность'].config(text=f"{v_metrics['coherence']:.3f}")
        self.metrics_labels['V: Самоподобие'].config(text=f"{v_metrics['self_similarity']:.3f}")
        self.metrics_labels['V: Предсказуемость'].config(text=f"{v_metrics['predictability']:.3f}")
        self.metrics_labels['V: Сила аттрактора'].config(text=f"{v_metrics['attractor_strength']:.1f}")
        self.metrics_labels['V: Внутренняя размерность'].config(text=f"{v_metrics['intrinsic_dim']}")

        self.metrics_labels['S: Каталитическое замыкание'].config(text=f"{s_metrics['catalytic_frac']:.2f}")
        self.metrics_labels['S: Устойчивость'].config(text=f"{s_metrics['robustness']:.3f}")
        self.metrics_labels['S: Модулярность'].config(text=f"{s_metrics['modularity']:.3f}")
        self.metrics_labels['S: Новизна'].config(text=f"{s_metrics['novelty']:.2f}")
        self.metrics_labels['S: Поток энергии'].config(text=f"{s_metrics['flux']:.3e}")

        self.metrics_labels['Emergence'].config(text=f"{emergence:.3f}")

        # Запланировать следующий кадр
        if self.update_wave_flag:
            self.root.after(80, self.update_video_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
