import os
import subprocess
import rasterio
import numpy as np
import matplotlib.pyplot as plt

# Функція для об'єднання окремих банд у один файл
def merge_bands(input_files: object, output_file: object) -> None:
    # Використовуємо gdal_merge для об'єднання банд
    subprocess.run([r"C:\OSGeo4W\apps\Python312\python.exe", r"C:\OSGeo4W\apps\Python312\Scripts\gdal_merge.py", "-separate", "-o", output_file] + input_files)
# Функція для репроекції зображення в задану проекцію
def reproject_image(input_file, output_file, target_srs="EPSG:4326"):
    # Використовуємо gdalwarp для зміни просторової референції (SRS) на задану
    subprocess.run([r"C:\OSGeo4W\bin\gdalwarp.exe", "-s_srs", "EPSG:32633", "-t_srs", target_srs, input_file, output_file])

# Функція для з'єднання всіх банд в один файл
def concatenate_bands(input_files, output_file):
    # З'єднуємо усі банд у один файл за допомогою gdal_merge
    subprocess.run([r"C:\OSGeo4W\apps\Python312\python.exe", r"C:\OSGeo4W\apps\Python312\Scripts\gdal_merge.py", "-o", output_file] + input_files)

# Функція для обрізки зображення на основі шейп-файлу
def clip_image(input_file, shapefile, output_file):
    # Використовуємо gdalwarp для обрізки зображення згідно з шейп-файлом
    subprocess.run([r"C:\OSGeo4W\bin\gdalwarp.exe", "-cutline", shapefile, "-crop_to_cutline", input_file, output_file])

# Функція для візуалізації зображення
def plot_image(image_file):
    # Читання зображення з файлу за допомогою rasterio
    with rasterio.open(image_file) as src:
        print(f"Кількість каналів: {src.count}")
        
        # Якщо зображення має 3 або більше каналів, беремо перші три
        if src.count >= 3:
            img = src.read([1, 2, 3]).astype(np.float32)
        else:
            img = src.read(1).astype(np.float32)
        
        # Переставляємо канали на останнє місце для візуалізації
        img = np.moveaxis(img, 0, -1)  
        
        # Перевірка на наявність значень, щоб уникнути ділення на 0
        if img.max() != img.min():
            img = (img - img.min()) / (img.max() - img.min())
        else:
            img = np.zeros_like(img)  # Якщо все однакові значення, просто робимо чорне зображення
    
    # Виводимо зображення на екран
    plt.figure(figsize=(10, 10))
    plt.imshow(img)
    plt.title(f"Processed Image: {image_file}")
    plt.axis("off")
    plt.show()

# Функція для паншарпінгу зображення
def pansharpen(band_file, panchromatic_file, output_file, method):
    print(f"Розпочато паншарпінг з методом {method}")
    # Використовуємо gdalwarp для поєднання банд з панхроматичним зображенням
    subprocess.run([r"C:\OSGeo4W\bin\gdalwarp.exe",  "-r", method, band_file, panchromatic_file, output_file])
    print(f"Збережено паншарпінг у {output_file}")

# Визначення вхідних файлів для різних банд Sentinel-2
sentinel_b2 = "data/Sentinel-2_L2A_B02.tiff"
sentinel_b3 = "data/Sentinel-2_L2A_B03.tiff"
sentinel_b4 = "data/Sentinel-2_L2A_B04.tiff"
sentinel_b8 = "data/Sentinel-2_L2A_B08.tiff"

# Об'єднуємо B2, B3, B4 банду в один файл
merged_output = "data/processed/Sentinel-2_RGBNIR.tif"
merge_bands([sentinel_b2, sentinel_b3, sentinel_b4], merged_output)

# Репроекція об'єднаного зображення в проекцію EPSG:4326
reprojected_output = "data/processed/Sentinel-2_RGBNIR_reprojected.tif"
reproject_image(merged_output, reprojected_output)

# Об'єднуємо всі банду в один файл для отримання повного зображення
final_output = "data/processed/Sentinel-2_Full.tif"
concatenate_bands([sentinel_b2, sentinel_b3, sentinel_b4, sentinel_b8], final_output)

# Обрізаємо зображення за шейп-файлом
shapefile = "data/processed/Kyiv_regions.shp"
clipped_output = "data/processed/Sentinel-2_Clipped.tif"
clip_image(final_output, shapefile, clipped_output)

# Візуалізуємо обрізане зображення
plot_image(clipped_output)

print("Обробка Sentinel-2 завершена!")

# Методи для паншарпінгу
methods = ["bilinear", "cubic", "lanczos", "average"]
for method in methods:
    # Паншарпінг для кожного методу
    output_file = f"data/processed/Sentinel-2_Pansharpened_{method}.tif"
    pansharpen(merged_output, sentinel_b8, output_file, method)
    # Візуалізація паншарпінгованого зображення
    plot_image(output_file)

print("Обробка Sentinel-2 завершена!")
