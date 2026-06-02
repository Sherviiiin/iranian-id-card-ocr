import cv2
import numpy as np

def detect_data_box(image):
    # پردازش
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img_height, img_width = image.shape
    margin = img_height // 30

    # پردازش تصویر
    _, binary = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY_INV)
    connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, np.ones((1, 50), np.uint8))

    # تشخیص کانتورها و جمع‌آوری مستطیل‌ها
    contours = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    rects = [cv2.boundingRect(cnt) for cnt in contours if cv2.boundingRect(cnt)[2] > 20 and cv2.boundingRect(cnt)[3] > 5]

    # گروه‌بندی مستطیل‌ها بر اساس موقعیت Y
    rects.sort(key=lambda r: r[1] + r[3] // 2)
    groups = []
    current_group = [rects[0]]

    for rect in rects[1:]:
        if abs(rect[1] + rect[3] // 2 - current_group[-1][1] - current_group[-1][3] // 2) < 20:
            current_group.append(rect)
        else:
            groups.append(current_group)
            current_group = [rect]

    groups.append(current_group)

    # محاسبه موقعیت Y برای هر گروه و انتخاب ۶ بزرگترین‌ها
    y_positions = [(min([r[1] for r in group]) - margin, max([r[1] + r[3] for r in group]) + margin) for group in groups]
    y_positions = sorted(y_positions, key=lambda x: x[1] - x[0], reverse=True)[:6]

    # مرتب‌سازی از بالاترین موقعیت Y به پایین‌ترین
    y_positions.sort(key=lambda x: x[0])

    boxes = []
    # ذخیره تصاویر هر محیط
    for i, (y_min, y_max) in enumerate(y_positions):
        # برش محیط
        cropped = image[int(y_min):int(y_max), 0:img_width]

        boxes.append(cropped)

    return boxes