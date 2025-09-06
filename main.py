import cv2
import numpy as np

# Загрузка изображения
image = cv2.imread('1752497179693.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Улучшение контраста
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
gray = clahe.apply(gray)

# Бинаризация
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Удаление шума
binary = cv2.medianBlur(binary, 5)


# Нахождение контуров
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
max_contour = max(contours, key=cv2.contourArea)

# Получение описанного прямоугольника вокруг стопы
x, y, w, h = cv2.boundingRect(max_contour)
cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("Binary image", image)

cv2.waitKey(0)
cv2.destroyAllWindows()

# cv2.imshow('Detected Points', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
