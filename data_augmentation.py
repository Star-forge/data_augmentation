# coding: utf8
import argparse
import os
import random
from os.path import basename, splitext
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

EXTENSIONS = ['jpg', 'jpeg', 'JPG', 'JPEG']
IMAGE_NAME = ""
IN_DIR_ROOT = ""
IN_DIR = ""
OUT_DIR_ROOT = ""
OUT_DIR = ""
FILES_COUNT = 0
IMAGE_SIZE = (299, 299)

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
        default="3",
        help="Радиус блюра (по-умолчанию: 3)"
    )
    ap.add_argument(
        "-l",
        "--lines",
        type=int,
        required=False,
        default="3",
        help="Количество линий (по-умолчанию: 3)"
    )
    ap.add_argument(
        "-g",
        "--glare",
        type=int,
        required=False,
        default="1",
        help="Количество бликов (по-умолчанию: 1)"
    )
    return vars(ap.parse_args())

def get_image_from_path(in_dir, image_name):
    # Чтение изображения
    im = Image.open(in_dir + image_name).convert("RGBA")
    return im

# * Сохранение изображения в файл с определенным именем
def save_image_to_path(image, output_directory, image_name, resize=True):
    # Если директории для сохранения нет - создание
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # Получение полного пути к изображению, включающего директорию и имя файла
    image_path = output_directory + image_name
    # Изменение размера
    if resize :
        image = image.resize(IMAGE_SIZE, Image.LANCZOS)
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
def addLines(input_directory, output_directory, im_name, lines_num):
    im = get_image_from_path(input_directory, im_name)
    # новое имя файла в директории для результатов
    draw = ImageDraw.Draw(im)
    img_x, img_y = im.size
    for i in range(0,lines_num):
        line_image_name = im_name[:im_name.rindex('.')] + "_l" + str(i) + splitext(im_name)[1]
        r = lambda: random.randint(0, 255)
        color = ('#%02X%02X%02X' % (r(), r(), r()))
        draw.line((random.randint(0, img_x), random.randint(0, img_y), random.randint(0, img_x), random.randint(0, img_y)), fill=color, width=10)
        save_image_to_path(im, output_directory, line_image_name)

def brightnessUP(im):
    width, height = im.size
    factor = 50
    pix = im.load()
    draw = ImageDraw.Draw(im)
    for i in range(width):
        for j in range(height):
            a = pix[i, j][0] + factor
            b = pix[i, j][1] + factor
            c = pix[i, j][2] + factor
            if (a < 0):
                a = 0
            if (b < 0):
                b = 0
            if (c < 0):
                c = 0
            if (a > 255):
                a = 255
            if (b > 255):
                b = 255
            if (c > 255):
                c = 255
            draw.point((i, j), (a, b, c))
    return im

def drawGlare(im, AX, AY, BX, BY):
    # print("glare", AX, AY, BX, BY)
    center_left = int(AX + (BX - AX) / 2 - (BX - AX) / 10)
    center_top = int(AY + (BY - AY) / 2 - (BY - AY) / 10)
    center_right = int(AX + (BX - AX) / 2 + (BX - AX) / 10)
    center_bottom = int(AY + (BY - AY) / 2 + (BY - AY) / 10)
    step = 15
    for i in range(step, 60, step):
        left = int(AX+(BX-AX)/2-(BX-AX)/100*i)
        top = int(AY+(BY-AY)/100*i-(BY-AY)/100*step)
        right = int(AX+(BX-AX)/2+(BX-AX)/100*i)
        bottom = int(BY-(BY-AY)/100*i+(BY-AY)/100*step)
        cropped_im = im.crop((left, top, right, bottom))
        # save_image_to_path(cropped_im, IN_DIR_ROOT + os.sep + ".." + os.sep, "tmp.jpg", False)
        # cropped_im = get_image_from_path(IN_DIR_ROOT + os.sep + ".." + os.sep, "tmp.jpg")
        # cropped_im = cropped_im.filter(ImageFilter.BLUR)
        brightnessUP(cropped_im)
        # cropped_im.show()
        im.paste(cropped_im, (left, top))
    cropped_im = im.crop((center_left, center_top, center_right, center_bottom))
    # save_image_to_path(cropped_im, IN_DIR_ROOT + os.sep + ".." + os.sep, "tmp.jpg", False)
    # cropped_im = get_image_from_path(IN_DIR_ROOT + os.sep + ".." + os.sep, "tmp.jpg")
    cropped_im = cropped_im.filter(ImageFilter.BLUR)
    im.paste(cropped_im, (center_left, center_top))
    return im

def addGlare(input_directory, output_directory, im_name, glare_num):
    im = get_image_from_path(input_directory, im_name)
    # новое имя файла в директории для результатов
    draw = ImageDraw.Draw(im)
    img_x, img_y = im.size
    for i in range(0, glare_num):
        glare_image_name = im_name[:im_name.rindex('.')] + "_G" + str(i) + splitext(im_name)[1]
        # Координаты точек в которые будет вписан круг (размером не более чем 1/3 всего изображения)
        AX = random.randint(int(img_x/5), img_x-int(img_x / 3))
        AY = random.randint(int(img_x/5), img_y-int(img_y / 3))
        circle_diameter = random.randint(int(img_x / 4), int(img_y / 3))
        BX = AX+circle_diameter
        BY = AY+circle_diameter
        # draw.ellipse((AX, AY, BX, BY), outline='silver')
        im = drawGlare(im, AX, AY, BX, BY)
        save_image_to_path(im, output_directory, glare_image_name)

# * Блюр(дефокус) изображений (Размытие по Гауссу с радиусом (radius))
def blur_image(input_directory, output_directory, im_name, radius):
    im = get_image_from_path(input_directory, im_name)
    # новое имя файла в директории для результатов = изначальное-имя_rotated_угол-вращения.изначальное-расширение
    blurred_image_name = im_name[:im_name.rindex('.')] + "_b" + splitext(im_name)[1]
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
            filled = "f"
        # новое имя файла в директории для результатов = изначальное-имя_rotated_угол-вращения.изначальное-расширение
        rotated_image_name = im_name[:im_name.rindex('.')] + "_r" + k.__str__().zfill(3) + filled + splitext(im_name)[1]
        # Сохранение результата в файл
        save_image_to_path(im_rotated, output_directory, rotated_image_name)

# Функция заполняет список для архивирования
def GetListForAugmentation(ImagePath):
    ImageList = []
    for file in os.listdir(ImagePath):
        path = os.path.join(ImagePath, file)
        if not os.path.isdir(path):
            if (path.endswith(tuple(EXTENSIONS))):
                ImageList.append(path)
            else:
                img = Image.open(path)
                img_new = splitext(path)[0]+".jpg"
                img.save(img_new)
                ImageList.append(img_new)

        else:
            ImageList += GetListForAugmentation(path)
    return ImageList

# входная точка приложения
def ResizeImg(input_directory, output_directory, im_name, new_im_name=""):
    if(new_im_name==""):
        new_im_name = im_name
    im = get_image_from_path(input_directory, im_name)
    im_resized = im.resize(IMAGE_SIZE, Image.LANCZOS)
    # Сохранение результата в файл
    save_image_to_path(im_resized, output_directory, new_im_name)

def print_step_number(step, steps):
    print("\rШаг " +str(step)+ " из " + str(steps), end="")
    if(step == steps):
        print("\nЗавершено")

if __name__ == "__main__":
    print("\n***АНАЛИЗ ПАРАМЕТРОВ***")
    args = init()
    # получение значения параметра "Директория поиска изображений"
    input_directory = args["dir"]
    # получение значения параметра "Угол поворота"
    angle = args["angle"]
    # получение значения параметра "Границы сектора"
    sector = args["sector"]
    # получение значения параметра "Добавление шума"
    noise = args["noise"]
    # получение значения параметра "Радиус размытия"
    radius = args["radius"]
    # получение значения параметра "Количество линий"
    lines_num = args["lines"]
    # получение значения параметра "Количество бликов"
    glare_num = args["glare"]

    if (radius <= 0): radius = 3
    if (lines_num <= 0): lines_num = 3
    if (glare_num <= 0): glare_num = 1

    print("Директория поиска изображений:\t" + str(input_directory) +
          "\nУгол поворота:   \t\t" + str(angle) +
          "\nГраницы сектора: \t\t" + str(sector) +
          "\nГенерация шума:  \t\t" + str(noise) +
          "\nРадиус размытия: \t\t" + str(radius) +
          "\nКоличество линий:\t\t" + str(lines_num) +
          "\nКоличество бликов:\t\t" + str(glare_num))

    print("\n***ПОИСК ФАЙЛОВ***")
    image_list = GetListForAugmentation(input_directory)
    FILES_COUNT = len(image_list)
    print("Обнаружено файлов = " + str(FILES_COUNT))
    if(input_directory.endswith(os.sep)): IN_DIR = input_directory
    else: IN_DIR = input_directory + os.sep
    IN_DIR_ROOT = IN_DIR
    OUT_DIR_ROOT = IN_DIR[:-1]  + "_out"
    os.makedirs(OUT_DIR_ROOT,exist_ok=True)

    print("\n***ИЗМЕНЕНИЕ РАЗМЕРА ИЗОБРАЖЕНИЙ ДО "+str(IMAGE_SIZE)+"***")
    step = 0;
    for image_path in image_list:
        step += 1
        IN_DIR, IMAGE_NAME = os.path.split(image_path)
        IN_DIR += os.sep
        OUT_DIR = OUT_DIR_ROOT + os.sep + IN_DIR[len(IN_DIR_ROOT):]
        # new_image_name = ((str(step).zfill(len(str(len(image_list))))) + splitext(IMAGE_NAME)[1])
        ResizeImg(IN_DIR, OUT_DIR, IMAGE_NAME)
        print_step_number(step, len(image_list))

    print("\n***ПОДГОТОВКА К ОБРАБОТКЕ ИЗОБРАЖЕНИЙ***")
    input_directory = OUT_DIR_ROOT
    image_list = GetListForAugmentation(input_directory)
    print("Всего к обработке = " + str(len(image_list)))
    if (input_directory.endswith(os.sep)):
        IN_DIR = input_directory
    else:
        IN_DIR = input_directory + os.sep
    IN_DIR_ROOT = IN_DIR

    print("\n***ОБРАБОТКА ИЗОБРАЖЕНИЙ***")
    print("Начало обработки в директории: " + IN_DIR + ", генерация шума: " + str(noise))

    step = 0;
    for image_path in image_list:
        step += 1
        IN_DIR, IMAGE_NAME = os.path.split(image_path)
        IN_DIR += os.sep

        # Директория для результатов вращения
        OUT_DIR = OUT_DIR_ROOT + os.sep + "#R" + os.sep + IN_DIR[len(IN_DIR_ROOT):]
        print("[" + str(step).zfill(len(str(len(image_list)))) + "/" + str(
            len(image_list)) + "] Rotate:\t" + IN_DIR + "\t" + IMAGE_NAME + "\t" + OUT_DIR)
        # Вращение изображения
        rotate_image(IN_DIR, OUT_DIR, IMAGE_NAME, angle, sector, noise)

        # Директория для результатов внесения дефокуса
        OUT_DIR = OUT_DIR_ROOT + os.sep + "#B" + os.sep + IN_DIR[len(IN_DIR_ROOT):]
        print("[" + str(step).zfill(len(str(len(image_list)))) + "/" + str(
            len(image_list)) + "] Blur:   \t" + IN_DIR + "\t" + IMAGE_NAME + "\t" + OUT_DIR)
        # Дефокус (размытие)
        blur_image(IN_DIR, OUT_DIR, IMAGE_NAME, radius)

        # Директория для результатов рисования линий
        OUT_DIR = OUT_DIR_ROOT + os.sep + "#L" + os.sep + IN_DIR[len(IN_DIR_ROOT):]
        print("[" + str(step).zfill(len(str(len(image_list)))) + "/" + str(
            len(image_list)) + "] Lines:   \t" + IN_DIR + "\t" + IMAGE_NAME + "\t" + OUT_DIR)
        # Линии
        addLines(IN_DIR, OUT_DIR, IMAGE_NAME, lines_num)

        # Директория для результатов рисования бликов
        OUT_DIR = OUT_DIR_ROOT + os.sep + "#G" + os.sep + IN_DIR[len(IN_DIR_ROOT):]
        print("[" + str(step).zfill(len(str(len(image_list)))) + "/" + str(
            len(image_list)) + "] Glare:   \t" + IN_DIR + "\t" + IMAGE_NAME + "\t" + OUT_DIR)
        # Блики
        addGlare(IN_DIR, OUT_DIR, IMAGE_NAME, glare_num)

        # stretch_image(input_directory, output_directory, basename(image_name), 100)

    print("\n***ОБРАБОТКА ЗАВЕРШЕНА***")
    print("Новый датасет находится по пути = " + OUT_DIR_ROOT + "." +
          "\nВ директории '#R' - повернутые изображения, "+
          "\nв директории '#L' - с линиями, "+
          "\nв директории '#G' - с бликами, "+
          "\nа в директории '#B' - размытые. "+
          "\nВсе изображения приведены к размеру " +str(IMAGE_SIZE)+ " пикселей (с помощью фильтра Ланцоша). "+
          "\nКоличество файлов в первоначальном датасете = " + str(FILES_COUNT) +
          "\nКоличество файлов в итоговом датасете = " + str(len(GetListForAugmentation(OUT_DIR_ROOT))))
    print("\n")
