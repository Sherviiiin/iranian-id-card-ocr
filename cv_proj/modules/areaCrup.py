def crop_image(image):
    # ابعاد اصلی تصویر
    original_width = 3200
    original_height = 2050

    # مختصات کراپ بر اساس تصویر اصلی
    x1, x2 = 1100, 2550
    y1, y2 = 450, 1700

    # گرفتن ابعاد جدید تصویر
    height, width, _ = image.shape

    # محاسبه نسبت ابعاد جدید به ابعاد اصلی
    width_ratio = width / original_width
    height_ratio = height / original_height

    # محاسبه مختصات جدید بر اساس مقیاس جدید
    new_x1 = int(x1 * width_ratio)
    new_x2 = int(x2 * width_ratio)
    new_y1 = int(y1 * height_ratio)
    new_y2 = int(y2 * height_ratio)

    # کراپ تصویر با مختصات جدید
    cropped_image = image[new_y1:new_y2, new_x1:new_x2]
    
    return cropped_image
