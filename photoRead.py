from PyQt5.QtGui import QPixmap, qRgb, qRed, qGreen, qBlue, qGray
import photo2
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAction
import sys
import numpy as np



class MyFotoRead(QtWidgets.QMainWindow, photo2.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Фиксируем размер виджета
        self.setFixedSize(self.size())

        # создание строки меню
        mainMenu = self.menuBar()

        # создаем меню "файл" для сохранения, очистки и открытия изображения
        self.fileMenu = mainMenu.addMenu("Файл")

        # создание действия "Открыть"
        openAction = QAction("Открыть", self)
        # добавляем "открыть" в меню "файл"
        self.fileMenu.addAction(openAction)
        # добавление действия к "Открыть"
        openAction.triggered.connect(self.openImage)

        # создаем действие "Сохранить"
        saveAction = QAction("Сохранить", self)
        # добавление "Сохранить" в меню "файл"
        self.fileMenu.addAction(saveAction)
        # добавление действия к "Сохранить"
        saveAction.triggered.connect(self.saveImage)

        # создание действия "Очистить"
        clearAction = QAction("Очистить", self)
        # добавляем "очистить" в меню "файл"
        self.fileMenu.addAction(clearAction)
        # добавление действия к "Очистить"
        clearAction.triggered.connect(self.clearImage)

        self.Original.clicked.connect(self.reset_image)
        self.Edge.clicked.connect(self.apply_edge)
        self.Gray.clicked.connect(self.apply_grayscale)
        self.Blur.clicked.connect(self.apply_smooth)
        self.Inversion.clicked.connect(self.apply_invert)
        self.Sepia.clicked.connect(self.apply_sepia)
        self.Red.clicked.connect(self.apply_red)

    #метод, который открывает изображение
    def openImage(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "",
                                                  "Images (*.png *.jpg *.jpeg *.bmp)")
        if filePath:
            self.original_image = QPixmap(filePath)
            self.image.setPixmap(self.original_image)
            self.modified_image = self.original_image  # Храним измененное изображение

    #Метод, который сохраняет изображение
    def saveImage(self):
        if self.modified_image:
            filePath, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "",
                                                      "Images (*.png *.jpg *.jpeg *.bmp)")
            if filePath:
                self.modified_image.save(filePath)

   #Метод, который убирает фотографию
    def clearImage(self):
        self.image.clear()

    #Метод, который возвращает исходное изображение
    def reset_image(self):
        if hasattr(self, 'original_image'):  # Проверка, есть ли сохраненное исходное изображение
            self.image.setPixmap(self.original_image)
        else:
            # Вывод сообщения об ошибке, если исходное изображение не найдено
            QMessageBox.warning(self, "Ошибка", "Исходное изображение не найдено.")

    # Метод, который применяет фильтр края
    def apply_edge(self):
        if self.image.pixmap():
            pixmap = self.image.pixmap()
            image = pixmap.toImage()
            kernel_x = np.array([[-1, 0, 1],
                                 [-2, 0, 2],
                                 [-1, 0, 1]])

            kernel_y = np.array([[-1, -2, -1],
                                 [0, 0, 0],
                                 [1, 2, 1]])

            for x in range(1, image.width() - 1):
                for y in range(1, image.height() - 1):
                    intensity_x = 0
                    intensity_y = 0
                    for i in range(3):
                        for j in range(3):
                            pixel = image.pixel(x + i - 1, y + j - 1)
                            intensity_x += qGray(pixel) * kernel_x[i, j]
                            intensity_y += qGray(pixel) * kernel_y[i, j]

                    magnitude = min(255, int(np.sqrt(intensity_x ** 2 + intensity_y ** 2)))
                    new_pixel = qRgb(magnitude, magnitude, magnitude)
                    image.setPixel(x, y, new_pixel)
            self.modified_image = QPixmap.fromImage(image)
            self.image.setPixmap(self.modified_image)

    # Функция для применения сепии
    def apply_sepia(self):
        if self.image.pixmap():
            pixmap = self.image.pixmap()
            image = pixmap.toImage()
            for x in range(image.width()):
                for y in range(image.height()):
                    pixel = image.pixel(x, y)
                    red = (pixel >> 16) & 0xFF
                    green = (pixel >> 8) & 0xFF
                    blue = pixel & 0xFF

                    sepia_red = int(0.393 * red + 0.769 * green + 0.189 * blue)
                    sepia_green = int(0.349 * red + 0.686 * green + 0.168 * blue)
                    sepia_blue = int(0.272 * red + 0.534 * green + 0.131 * blue)

                    # Ограничение значений от 0 до 255
                    sepia_red = min(sepia_red, 255)
                    sepia_green = min(sepia_green, 255)
                    sepia_blue = min(sepia_blue, 255)

                    image.setPixel(x, y, qRgb(sepia_red, sepia_green, sepia_blue))

            self.modified_image = QPixmap.fromImage(image)
            self.image.setPixmap(self.modified_image)

    # Функция для применения блюра
    def apply_smooth(self):
        if self.image.pixmap():
            pixmap = self.image.pixmap()
            image = pixmap.toImage()
            width = image.width()
            height = image.height()
            for x in range(1, width - 1):
                for y in range(1, height - 1):
                    sum_r = sum_g = sum_b = 0
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            near_pixel = image.pixel(x + dx, y + dy)
                            sum_r += qRed(near_pixel)
                            sum_g += qGreen(near_pixel)
                            sum_b += qBlue(near_pixel)
                    avg_r = sum_r // 9
                    avg_g = sum_g // 9
                    avg_b = sum_b // 9
                    smoothed_color = qRgb(avg_r, avg_g, avg_b)
                    image.setPixel(x, y, smoothed_color)
            self.modified_image = QPixmap.fromImage(image)
            self.image.setPixmap(self.modified_image)

    # Функция для применения инверсии
    def apply_invert(self):
        if self.image.pixmap():
            pixmap = self.image.pixmap()
            image = pixmap.toImage()
            for x in range(image.width()):
                for y in range(image.height()):
                    pixel = image.pixel(x, y)
                    red = 255 - qRed(pixel)
                    green = 255 - qGreen(pixel)
                    blue = 255 - qBlue(pixel)
                    image.setPixel(x, y, qRgb(red, green, blue))
            self.modified_image = QPixmap.fromImage(image)
            self.image.setPixmap(self.modified_image)

    # Функция для применения красного фильтра
    def apply_red(self):
        if self.image.pixmap():
            pixmap = self.image.pixmap()
            image = pixmap.toImage()
            for x in range(image.width()):
                for y in range(image.height()):
                    pixel = image.pixel(x, y)
                    red = (pixel >> 16) & 0xFF
                    red_pixel = qRgb(red, 0, 0)
                    image.setPixel(x, y, red_pixel)
            self.modified_image = QPixmap.fromImage(image)
            self.image.setPixmap(self.modified_image)

    # Функция для применения серого фильтра
    def apply_grayscale(self):

        if self.image.pixmap():
            pixmap = self.image.pixmap()
            image = pixmap.toImage()
            for x in range(image.width()):
                for y in range(image.height()):
                    pixel = image.pixel(x, y)
                    gray = (pixel >> 16) & 0xFF
                    image.setPixel(x, y, qRgb(gray, gray, gray))
            self.modified_image = QPixmap.fromImage(image)
            self.image.setPixmap(self.modified_image)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    Editor = MyFotoRead()
    Editor.show()
    sys.exit(app.exec_())