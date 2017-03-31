import argparse
import os
import numpy as np
from PIL import Image, ImageFilter
from tensorflow.python.platform import gfile

EXTENSIONS = ['jpg', 'jpeg', 'JPG', 'JPEG']

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

def get_image_from_path(directory, image_name):
    img_path = directory + os.sep + image_name;
    # Чтение изображения
    im = Image.open(img_path).convert("RGBA")
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
def blur_image(input_directory, output_directory, image_name, radius=5):
    im = get_image_from_path(input_directory, image_name)
    # новое имя файла в директории для результатов = изначальное-имя_rotated_угол-вращения.изначальное-расширение
    blurred_image_name = image_name[:image_name.rindex('.')] + "_blured" + image_name[image_name.rindex('.'):]
    blurred_image = im.filter(ImageFilter.GaussianBlur(radius=int(radius)))
    save_image_to_path(blurred_image, output_directory, blurred_image_name)

# * Вращение изображения на определенный угол (angle) в рамках определенного сектора (sector)
def rotate_image(input_directory, output_directory, im_name, angle=2, sector="0-360", noise=""):
    filled = ""
    im = get_image_from_path(input_directory, image_name)
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

# входная точка приложения
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

    # Получение списка файлов в переменную files
    files = os.listdir(input_directory)
    # Фильтрация списка, по расширениям '.jpg' или '.jpeg'
    image_list = list(filter(lambda x: x.endswith('.jpg'), files))

    print("Начало обработки в директории: " + input_directory + ", генерация шума: " + str(noise))
    print("Всего к обработке=" + str(len(image_list)))

    for image_name in image_list:
        print(image_name)
        # Вращение изображения
        # Директория для результатов
        output_directory = input_directory + os.sep + "out" + os.sep + "rotated" + os.sep
        rotate_image(input_directory, output_directory, image_name, angle, sector, noise)

        # Дефокус (размытие)
        # Директория для результатов
        output_directory2 = input_directory + os.sep + "out" + os.sep + "blured" + os.sep
        # Дефокус (размытие)
        blur_image(input_directory, output_directory2, image_name, radius)

        stretch_image(input_directory, output_directory, image_name, 100)

    # Директория для результатов
    output_directory2 = input_directory + os.sep + "out" + os.sep + "blured" + os.sep
    input_directory = output_directory[:-1]
    # Получение списка файлов в переменную files
    files = os.listdir(input_directory)
    # Фильтрация списка, по расширениям '.jpg' или '.jpeg'
    image_list = list(filter(lambda x: x.endswith('.jpg'), files))

    print("Начало обработки в директории: " + input_directory + ", генерация шума: " + noise)
    print("Всего к обработке=" + str(len(image_list)))

    for image_name in image_list:
        blur_image(input_directory, output_directory2, image_name, radius)