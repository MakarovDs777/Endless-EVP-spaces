import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

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
        low = random.randint(0, 130)
        high = random.randint(low+1, 255)
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
    max_same = max(len(set(frag)) for frag in fragments)
    ratio = max_same / total if total > 0 else 0
    return ratio

def process_file():
    file_path = filedialog.askopenfilename(title="Выберите текстовый файл с RGB данными", filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return
    
    try:
        rgb_data = load_rgb_data(file_path)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
        return
    
    # 1. Диапазоны генерации
    ranges = generate_random_ranges()
    
    # 2. Перегенерировать массив
    new_rgb = re_generate_array(rgb_data, ranges)
    
    # 3. Расчет повторяемости
    repetition = calc_repetition(new_rgb)
    
    # 4. Разделение на мозаики, расчет дисперсии
    fragments = split_into_fragments(new_rgb)
    dispersity = calc_dispertion(fragments)
    
    # 5. Расчет репрезентативности
    rep = calc_representativity(fragments)
    
    # Выводим в окно
    display_results(ranges, new_rgb, repetition, dispersity, rep)

def display_results(ranges, rgb_array, repetition, dispersity, rep_ratio):
    result_win = tk.Toplevel()
    result_win.title("Статистика RGB")
    txt = tk.Text(result_win, width=80, height=30)
    txt.pack()

    txt.insert(tk.END, f"Диапазоны для генерации:\n")
    for i, (low, high) in enumerate(ranges):
        txt.insert(tk.END, f"  Компонент {i+1} (R/G/B): {low} - {high}\n")

    txt.insert(tk.END, "\nПерегенерированный RGB (первые 10):\n")
    for pixel in rgb_array[:10]:
        txt.insert(tk.END, f"{pixel}\n")

    txt.insert(tk.END, "\nПовторяемость чисел:\n")
    for val, ratio in repetition:
        txt.insert(tk.END, f"{val}: {ratio:.2%}\n")

    txt.insert(tk.END, f"\nДисперсность фрагментов: {dispersity}\n")
    txt.insert(tk.END, f"Репрезентативность: {rep_ratio:.2%}\n")

# Главное окно
root = tk.Tk()
root.title("Статистика RGB данных")
btn = tk.Button(root, text="Выбрать файл и получить статистику", command=process_file)
btn.pack(padx=20, pady=20)
root.mainloop()