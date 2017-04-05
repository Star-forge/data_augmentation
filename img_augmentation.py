# coding: utf8
import argparse
import os
from os.path import basename

import numpy as np
from PIL import Image, ImageFilter
from tensorflow.python.platform import gfile

EXTENSIONS = ['jpg', 'jpeg', 'JPG', 'JPEG']
IMAGE_NAME = ""
IN_DIR_ROOT = ""
IN_DIR = ""
OUT_DIR_ROOT = ""
OUT_DIR = ""

def init():
    # задаются параметры приложения
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-d",
        "--dir",
        type=str,
        required=True,
        help="Директория поиска изображений"
    )
    ap.add_argument(
        "-a",
        "--angle",
        type=int,
        required=False,
        default=2,
        help="Угол поворота изображения (по-умолчанию: 2 градуса)"
    )
    ap.add_argument(
        "-s",
        "--sector",
        type=str,
        required=False,
        default="0-360",
        help="В какой области вращать изображение (по-умолчанию:0-360 = поворот от 0+angle до 360)"
    )
    ap.add_argument(
        "-n",
        "--noise",
        type=bool,
        required=False,
        default="1",
        help="Добавление шума: 1 - добавлять шум к изображению при вращении; пустая строка "" - не добавлять"
    )
    ap.add_argument(
        "-r",
        "--radius",
        type=int,
        required=False,
        default="5",
        help="Радиус блюра (по-умолчанию: 5)"
    )
    return vars(ap.parse_args())

def get_image_from_path(in_dir, image_name):
    # Чтение изображения
    im = Image.open(in_dir + image_name).convert("RGBA")
    return im

# * Сохранение изображения в файл с определенным именем
def save_image_to_path(image, output_directory, image_name):
    # Если директории для сохранения нет - создание
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # Получение полного пути к изображению, включающего директорию и имя файла
    image_path = output_directory + image_name
    # Запись в файл
    image.save(image_path)

def get_noise_image(width, height):
    imarray = np.random.rand(height, width, 3) * 255
    im = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    return im

# * Растягивание на пределенные значения по оси X и Y
def stretch_image(input_directory, output_directory, image_name, X):
    im = get_image_from_path(input_directory, image_name)
    img_x, img_y = im.size
    img_noise = get_noise_image(img_x, img_y)
    X = -100
    if X < 0:
        img_x -=img_x/img_y*(-X)
    elif X > 0:
        img_y -=img_y/img_x*X

    mim = im.resize((int(img_x), int(img_y)), Image.ANTIALIAS)
    mim.show()
    coords = (int((img_noise.width-int(img_x))/2), int((img_noise.height-int(img_y))/2))
    print(coords)
    mim2 = Image.composite(mim, img_noise, mim)
    img_noise = img_noise.paste(mim, coords)
    # im.show()
    img_noise.save("00000.jpg")

# * Сжатие на пределенные значения по оси  X и Y

# * Сдвиг на пределенные значения по оси  X и Y

# * Введение на изображение бликов и линий

# * Блюр(дефокус) изображений (Размытие по Гауссу с радиусом (radius))
def blur_image(input_directory, output_directory, im_name, radius):
    im = get_image_from_path(input_directory, im_name)
    # новое имя файла в директории для результатов = изначальное-имя_rotated_угол-вращения.изначальное-расширение
    blurred_image_name = im_name[:im_name.rindex('.')] + "_blured" + im_name[im_name.rindex('.'):]
    blurred_image = im.filter(ImageFilter.GaussianBlur(radius=int(radius)))
    save_image_to_path(blurred_image, output_directory, blurred_image_name)

# * Вращение изображения на определенный угол (angle) в рамках определенного сектора (sector)
def rotate_image(input_directory, output_directory, im_name, angle, sector, noise):
    filled = ""
    im = get_image_from_path(input_directory, im_name)
    # Границы сектора, в рамках которого происходит вращение с шагом на угол angle
    start_sector = int(sector[:sector.index('-')])+int(angle)
    finish_sector = int(sector[sector.index('-')+1:])
    # Вращение изображения
    for k in range(int(start_sector), int(finish_sector), int(angle)):
        im_rotated = im.rotate(k, expand = True)
        # Если необходимо добавить шум
        if(noise):
            # Генерация фона (шума) под размер изображения
            img_noise = get_noise_image(im_rotated.width, im_rotated.height)
            # Слияние изображений
            im_rotated = Image.composite(im_rotated, img_noise, im_rotated)
            filled = "_filled"
        # новое имя файла в директории для результатов = изначальное-имя_rotated_угол-вращения.изначальное-расширение
        rotated_image_name = im_name[:im_name.rindex('.')] + "_rotated_" + k.__str__().zfill(3) + filled + im_name[im_name.rindex('.'):]
        # Сохранение результата в файл
        save_image_to_path(im_rotated, output_directory, rotated_image_name)

# Функция заполняет список для архивирования
def GetListForAugmentation(ImagePath):
    ImageList = []
    for file in os.listdir(ImagePath):
        path = os.path.join(ImagePath, file)
        if not os.path.isdir(path):
            ImageList.append(path)
        else:
            ImageList += GetListForAugmentation(path)
    return ImageList

# входная точка приложения
def ResizeImg(input_directory, output_directory, im_name):
    im = get_image_from_path(input_directory, im_name)
    im_resized = im.resize((299, 299), Image.LANCZOS)
    # Сохранение результата в файл
    save_image_to_path(im_resized, output_directory, im_name)

def print_step_number(step, steps):
    print("\rStep " +step+ " from " + steps, end="")

if __name__ == "__main__":
    args = init()
    # получение значения параметра "Директория поиска изображений"
    input_directory = args["dir"]
    # получение значения параметра "Угол поворота"
    angle = args["angle"] or 2
    # получение значения параметра "Границы сектора"
    sector = args["sector"] or "0-360"
    # получение значения параметра "Добавление шума"
    noise = args["noise"] or "1"
    # получение значения параметра "Радиус размытия"
    radius = args["radius"] or 5

    image_list = GetListForAugmentation(input_directory)
    print("\nВсего к обработке=" + str(len(image_list)))
    if(input_directory.endswith(os.sep)): IN_DIR = input_directory
    else: IN_DIR = input_directory + os.sep
    IN_DIR_ROOT = IN_DIR
    OUT_DIR_ROOT = IN_DIR[:-1]  + "_out"
    os.makedirs(OUT_DIR_ROOT,exist_ok=True)

    step = 0;
    for image_path in image_list:
        IN_DIR, IMAGE_NAME = os.path.split(image_path)
        IN_DIR += os.sep
        OUT_DIR = OUT_DIR_ROOT + os.sep + IN_DIR[len(IN_DIR_ROOT):]
        ResizeImg(IN_DIR, OUT_DIR, IMAGE_NAME)
        step+=1
        print_step_number(str(step), str(len(image_list)))

    input_directory = OUT_DIR_ROOT
    image_list = GetListForAugmentation(input_directory)
    print("\nВсего к обработке=" + str(len(image_list)))
    if (input_directory.endswith(os.sep)):
        IN_DIR = input_directory
    else:
        IN_DIR = input_directory + os.sep
    IN_DIR_ROOT = IN_DIR

    print("\nНачало обработки в директории: " + IN_DIR + ", генерация шума: " + str(noise))

    step = 0;
    for image_path in image_list:
        step += 1
        IN_DIR, IMAGE_NAME = os.path.split(image_path)
        IN_DIR += os.sep

        # Директория для результатов rotate
        OUT_DIR = OUT_DIR_ROOT + os.sep + "#R" + os.sep + IN_DIR[len(IN_DIR_ROOT):]
        print(str(step).zfill(len(str(len(image_list)))) + " Rotate:\t" + IN_DIR +"\t"+ IMAGE_NAME +"\t"+ OUT_DIR)
        # Вращение изображения
        rotate_image(IN_DIR, OUT_DIR, IMAGE_NAME, angle, sector, noise)

        # Директория для результатов blur
        OUT_DIR = OUT_DIR_ROOT + os.sep + "#B" + os.sep + IN_DIR[len(IN_DIR_ROOT):]
        print(str(step).zfill(len(str(len(image_list)))) + " Blur:\t" + IN_DIR +"\t"+ IMAGE_NAME +"\t"+ OUT_DIR)
        # Дефокус (размытие)
        blur_image(IN_DIR, OUT_DIR, IMAGE_NAME, radius)

        # stretch_image(input_directory, output_directory, basename(image_name), 100)
    '''
    # Директория для результатов
    output_directory2 = input_directory + os.sep + "out" + os.sep + "blured" + os.sep
    input_directory = OUT_DIR[:-1]
    # Получение списка файлов в переменную files
    files = os.listdir(input_directory)
    # Фильтрация списка, по расширениям '.jpg' или '.jpeg'
    image_list = list(filter(lambda x: x.endswith('.jpg'), files))

    print("Начало обработки в директории: " + input_directory + ", генерация шума: " + noise)
    print("Всего к обработке=" + str(len(image_list)))

    for IMAGE_NAME in image_list:
        blur_image(input_directory, output_directory2, basename(IMAGE_NAME), radius)
    '''
