import cv2
import numpy as np

def detect_and_crop_national_card(image_path, show_steps=False):
    
    # خواندن تصویر
    image = cv2.imread(image_path)
    if image is None:
        print(f"خطا: تصویر در مسیر {image_path} یافت نشد!")
        return None
    
    original = image.copy()
    img_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    
    # تغییر اندازه برای پردازش سریعتر
    height, width = image.shape[:2]
    scale = 500 / height
    new_width = int(width * scale)
    new_height = 500
    resized = cv2.resize(image, (new_width, new_height))
    
    # پردازش تصویر
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # افزایش کنتراست
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    # حذف نویز
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # تشخیص لبه
    edges = cv2.Canny(gray, 30, 150)
    
    # عملیات مورفولوژیک برای بستن فضاهای خالی
    kernel = np.ones((5,5), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # یافتن کانتورها
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # انتخاب کانتورهای بزرگ
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    # جستجوی مستطیل کارت
    card_contour = None
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        # مستطیل یا تقریبا مستطیل
        if len(approx) >= 4:
            # بررسی نسبت ابعاد
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            
            # نسبت ابعاد کارت ملی حدود 1.58
            if 1.3 < aspect_ratio < 1.9 and w > 100 and h > 50:
                card_contour = approx
                break
    
    if card_contour is None:
        print("کارت ملی به وضوح تشخیص داده نشد. از بزرگترین کانتور استفاده می‌شود.")
        if contours:
            largest_contour = contours[0]
            peri = cv2.arcLength(largest_contour, True)
            card_contour = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)
        else:
            print("هیچ کانتوری یافت نشد!")
            return img_rgb
    
    # بزرگ کردن کانتور به اندازه اصلی
    card_contour = card_contour.astype('float32')
    card_contour[:, :, 0] /= scale
    card_contour[:, :, 1] /= scale
    card_contour = card_contour.astype('int32')
    
    # برش تصویر
    x, y, w, h = cv2.boundingRect(card_contour)
    
    # اضافه کردن حاشیه
    x_start = max(0, x)
    y_start = max(0, y)
    x_end = min(original.shape[1], x + w)
    y_end = min(original.shape[0], y + h)
    
    cropped = original[y_start:y_end, x_start:x_end]
    
    return cropped
