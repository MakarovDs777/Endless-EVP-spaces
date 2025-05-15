import tkinter as tk
from tkinter import filedialog, messagebox
import os
import numpy as np

# --- Объявляем функции анализа ---

def load_rgb_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    rgb_list = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 3:
            r, g, b = map(int, parts)
            rgb_list.append([r, g, b])
    return rgb_list

def generate_random_ranges():
    ranges = []
    for _ in range(3):
        low = np.random.randint(0, 130)
        high = np.random.randint(low+1, 255)
        ranges.append((low, high))
    return ranges

def re_generate_array(array, ranges):
    new_array = []
    for pixel in array:
        new_pixel = []
        for i, val in enumerate(pixel):
            low, high = ranges[i]
            new_val = np.random.randint(low, high+1)
            new_pixel.append(new_val)
        new_array.append(new_pixel)
    return new_array

def calc_repetition(array):
    counts = {}
    for pixel in array:
        for val in pixel:
            counts[val] = counts.get(val, 0) + 1
    total = len(array)*3
    sorted_counts = sorted([(k, v/total) for k, v in counts.items()], key=lambda x: x[1], reverse=True)
    return sorted_counts

def split_into_fragments(array, min_frag=5, max_frag=20):
    total_len = len(array)
    groups_count = np.random.randint(min_frag, max_frag+1)
    indices = sorted(np.random.choice(range(1, total_len), groups_count-1, replace=False))
    indices = [0]+indices+[total_len]
    fragments = []
    for i in range(len(indices)-1):
        frag = array[indices[i]:indices[i+1]]
        fragments.append(frag)
    return fragments

def calc_dispertion(fragments):
    sizes = [len(f) for f in fragments]
    avg_size = np.mean(sizes)
    if avg_size <= 30:
        return 'Маленькая'
    elif avg_size <= 60:
        return 'Средняя'
    elif avg_size <= 90:
        return 'Большая'
    else:
        return 'Очень большая'

def calc_representativity(fragments):
    total = sum(len(frag) for frag in fragments)
    max_unique_colors = max(len(set(map(tuple, frag))) for frag in fragments)
    ratio = max_unique_colors / total if total > 0 else 0
    return ratio

# --- Основная функция обработки одного файла ---

def analyze_file(file_path):
    rgb_data = load_rgb_data(file_path)
    ranges = generate_random_ranges()
    new_rgb = re_generate_array(rgb_data, ranges)
    repetition = calc_repetition(new_rgb)
    fragments = split_into_fragments(new_rgb)
    dispersity = calc_dispertion(fragments)
    rep_ratio = calc_representativity(fragments)
    return {
        'ranges': ranges,
        'sample': new_rgb,
        'repetition': repetition,
        'disperity': dispersity,
        'repr': rep_ratio
    }

# --- Функция обработки всей папки ---

def process_folder(folder_path, output_folder, progress_var):
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    files.sort()  # по алфавиту или по имени
    total_files = len(files)
    if total_files == 0:
        messagebox.showinfo("Информация", "Нет текстовых файлов в папке.")
        return

    # Создать папку для результатов
    os.makedirs(output_folder, exist_ok=True)
    count = 0

    for i, filename in enumerate(files, 1):
        file_full_path = os.path.join(folder_path, filename)
        result = analyze_file(file_full_path)
        # Формируем текст для сохранения
        save_path = os.path.join(output_folder, f'information_{i}.txt')
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(f"Обработка файла: {filename}\n")
            f.write("-" * 40 + "\n")
            f.write("Диапазоны генерации (R,G,B):\n")
            for j, (low, high) in enumerate(result['ranges']):
                f.write(f"  Компонент {j+1}: {low} - {high}\n")
            f.write("\nПерегенерированные RGB (первые 10):\n")
            for pixel in result['sample'][:10]:
                f.write(f"{pixel}\n")
            f.write("\nПовторяемость:\n")
            for val, ratio in result['repetition']:
                f.write(f"{val}: {ratio:.2%}\n")
            f.write(f"\nДисперсность фрагментов: {result['disperity']}\n")
            f.write(f"Репрезентативность: {result['repr']:.2%}\n")
        count += 1
        progress_var.set(f'Обработано {i} из {total_files}')
        # Обновляем интерфейс
        root.update()

    messagebox.showinfo("Готово!", f"Обработано {total_files} файлов. Результаты в: {output_folder}")

# --- Главное окно tkinter ---

def select_folder():
    folder_path = filedialog.askdirectory(title="Выберите папку с файлами")
    if folder_path:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        output_dir = os.path.join(desktop, "information_complete")
        progress_label.config(text="Обработка началась...")
        process_folder(folder_path, output_dir, progress_var)

# Создаём главное окно
root = tk.Tk()
root.title("Анализ папки с файлами RGB")

btn_select_folder = tk.Button(root, text="Выбрать папку для анализа", command=select_folder)
btn_select_folder.pack(padx=20, pady=10)

progress_var = tk.StringVar()
progress_label = tk.Label(root, textvariable=progress_var)
progress_label.pack(pady=10)

root.mainloop()