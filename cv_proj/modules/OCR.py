import re

NUMBERS = "۰۰۰٠۱١٢٣٤۵۶٧٨٩"
TRANS = str.maketrans(NUMBERS, "00001123456789")

def norm(s: str) -> str:
    s = s.translate(TRANS).replace("／", "/").replace("\\", "/")
    return re.sub(r"[^0-9/]", "", s)

def fix_date(s: str) -> str:
    chars = list(s)

    if len(chars) >= 3 and chars[1] == "4" and chars[2] == "5":
        chars[2] = "0"

    if len(chars) >= 6 and chars[5] == "5":
        chars[5] = "0"

    if len(chars) >= 9 and chars[8] == "5":
        chars[8] = "0"

    return "".join(chars)

def ocr(reader, boxes):
    results = []

    try:
        # 1
        result1 = reader.readtext(
            boxes[0],
            decoder="greedy",
            detail=1,
            paragraph=False,
            batch_size=8,
            # کیفیت/سایز
            mag_ratio=1.5,
            canvas_size=4000,
            add_margin=0.25,
            # کنترل نویز/اتصال کلمات
            text_threshold=0.5,
            low_text=0.3,
            link_threshold=0.4,
            allowlist="0123456789۰۰۰٠۱١٢٣٤۵۶٧٨٩/\\",
        )
        text = " ".join(t for _, t, _ in result1)
        results.append(norm(" ".join(text)))

        # 2
        res2 = reader.readtext(boxes[1], paragraph=True)
        for detection in res2:
            results.append(detection[1])

        # 3
        res3 = reader.readtext(boxes[2], paragraph=True)
        for detection in res3:
            results.append(detection[1])

        # 4
        result4 = reader.readtext(
            boxes[3],
            decoder="greedy",
            detail=1,
            paragraph=False,
            batch_size=8,
            # کیفیت/سایز
            mag_ratio=1.5,
            canvas_size=4000,
            add_margin=0.25,
            # کنترل نویز/اتصال کلمات
            text_threshold=0.5,
            low_text=0.3,
            link_threshold=0.4,
            allowlist="0123456789۰۰۰٠۱١٢٣٤۵۶٧٨٩/\\",
        )
        text = " ".join(t for _, t, _ in result4)
        fixed_date = fix_date(norm(" ".join(text)))
        results.append(fixed_date)

        # 5
        res5 = reader.readtext(boxes[4], paragraph=True)
        for detection in res5:
            results.append(detection[1])

        # 6
        result6 = reader.readtext(
            boxes[5],
            decoder="greedy",
            detail=1,
            paragraph=False,
            batch_size=8,
            # کیفیت/سایز
            mag_ratio=1.5,
            canvas_size=4000,
            add_margin=0.25,
            # کنترل نویز/اتصال کلمات
            text_threshold=0.5,
            low_text=0.3,
            link_threshold=0.4,
            allowlist="0123456789۰۰۰٠۱١٢٣٤۵۶٧٨٩/\\",
        )
        text = " ".join(t for _, t, _ in result6)
        fixed_date = fix_date(norm(" ".join(text)))
        results.append(fixed_date)
        
        print(results)
        return results
    except Exception as e:
        print("Error:", e)
        return False