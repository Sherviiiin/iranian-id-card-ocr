import cv2
import numpy as np

def detect_and_crop_image(image, show_steps=False):
    # تبدیل تصویر به خاکی-سفید (Grayscale)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # استفاده از Threshold برای تبدیل تصویر به باینری (سیاه و سفید)
    _, binary_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)

    # انجام عملیات مورفولوژی برای حذف نویز و بهبود تشخیص
    kernel = np.ones((3, 3), np.uint8)
    binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

    # پیدا کردن کانتورها (مناطق متن)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # متغیر برای ذخیره کانتور با بیشترین مساحت که نسبت ارتفاع به عرض بیشتر است
    max_area = 0
    best_contour = None

    # جستجو برای کانتوری که نسبت ارتفاع به عرض بیشتر از 1 داشته باشد و مساحت بیشتری داشته باشد
    for contour in contours:
        # برای هر کانتور یک مستطیل محاطی (Bounding box) پیدا می‌کنیم
        x, y, w, h = cv2.boundingRect(contour)

        # فقط اگر نسبت ارتفاع به عرض بیشتر از 1 باشد و مساحت بزرگتری داشته باشد
        if h > w:  # ارتفاع بیشتر از عرض
            area = w * h
            if area > max_area:
                max_area = area
                best_contour = contour

    # اگر کانتوری پیدا شد که بهترین باشد
    if best_contour is not None:
        # برای کانتور بهترین، مستطیل محاطی را پیدا می‌کنیم
        x, y, w, h = cv2.boundingRect(best_contour)

        # برش تصویر بر اساس مستطیل محاطی
        cropped_image = image[y:y+h, x:x+w]

        # رسم مستطیل سبز روی تصویر اصلی (فقط برای تصویر اصلی)
        image_with_rect = image.copy()  # یک کپی از تصویر اصلی می‌سازیم تا مستطیل فقط روی آن رسم شود
        cv2.rectangle(image_with_rect, (x, y), (x + w, y + h), (0, 255, 0), 2)
    else:
        print("هیچ کانتوری با ویژگی‌های مورد نظر یافت نشد.")
    
    return cropped_image
