import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import easyocr
import threading

from modules.cardDetection import detect_and_crop_national_card
from modules.picDetection import detect_and_crop_image
from modules.areaCrup import crop_image
from modules.boxCrup import detect_data_box
from modules.OCR import ocr
from modules.saveData import save_data
import matplotlib.pyplot as plt

def show_boxes(boxes):
    n = len(boxes)
    rows, cols = 2, 3

    fig, axes = plt.subplots(rows, cols, figsize=(12, 6))
    axes = axes.ravel()

    for i in range(rows * cols):
        axes[i].axis("off")
        if i < n:
            axes[i].imshow(boxes[i], cmap="gray")
            axes[i].set_title(f"Box {i+1}")

    plt.tight_layout()
    plt.show()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("پردازش کارت ملی")
        self.root.geometry("800x650+200+20")
        
        self.status_lbl = ttk.Label(root, text="")
        self.status_lbl.pack(pady=6)

        self.spinner = ttk.Progressbar(root, mode="indeterminate", length=220)
        self.spinner.pack(pady=6)
        self.spinner.pack_forget()

        # لایه بالا
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(fill="x", padx=10, pady=10)
        
        self.image_label = tk.Label(self.top_frame)
        self.image_label.pack(side="left")
        
        btn_frame = tk.Frame(self.top_frame)
        btn_frame.pack(side="right")
        
        self.upload_btn = tk.Button(btn_frame, text="بارگذاری", command=self.upload_image, width=15)
        self.upload_btn.pack(pady=5)
        
        self.process_btn = tk.Button(btn_frame, text="پردازش", command=self.start_processing, width=15, state="disabled")
        self.process_btn.pack(pady=5)
        
        # لایه پایین
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # سمت چپ - تصویر
        self.left_frame = tk.Frame(self.bottom_frame)
        self.left_frame.pack(side="left", fill="both", expand=True)
        self.result_image_label = tk.Label(self.left_frame)
        
        # سمت راست - داده‌ها
        self.right_frame = tk.Frame(self.bottom_frame)
        self.right_frame.pack(side="right")
        
        self.fields = ['شماره ملی', 'نام', 'نام خانوادگی', 'تاریخ تولد', 'نام پدر', 'پایان اعتبار']
        self.labels = []
        
        for i, field in enumerate(self.fields):
            frame = tk.Frame(self.right_frame, width=250, height=30)
            frame.pack_propagate(False)
            frame.pack(pady=5, anchor="e")
            
            value_label = tk.Label(frame, text=" ", width=15, anchor="w", bg="#f0f0f0", relief="solid")
            value_label.pack(side="left", padx=(5,0))
            
            name_label = tk.Label(frame, text=field, anchor="e", font=("Arial", 10, "bold"))
            name_label.pack(side="left")
            
            self.labels.append(value_label)
        
        self.reader = easyocr.Reader(["fa", "en"])

    def _on_ocr_done(self, result, error):
        self.spinner.stop()
        self.spinner.pack_forget()
        self.process_btn.config(state="normal")

        processed_img = cv2.resize(self.personal_pic, (210, 270))
        
        self.show_image(processed_img, self.result_image_label)
        self.result_image_label.pack(padx=10, pady=10, anchor="nw")

        if error:
            self.status_lbl.config(text=f"خطا: {error}")
            return
        
        for i, d in enumerate(self.result):
            self.labels[i].config(text=d)
        
        self.status_lbl.config(text="پردازش انجام شد ✅")
        messagebox.showinfo("انجام شد", "پردازش کامل شد")

    def _run_ocr_worker(self):
        try:
            boxes = detect_data_box(self.area)
            show_boxes(boxes)

            self.result = ocr(self.reader, boxes)
            error = None
        except Exception as e:
            self.result = None
            error = str(e)
        
        # step ?
        self.personal_pic = detect_and_crop_image(self.image)

        row = save_data("results.xlsx", self.fields, self.result, image=self.personal_pic)
        print("Saved to row:", row)

        # برگشت به Thread اصلی برای آپدیت UI
        self.root.after(0, lambda: self._on_ocr_done(self.result, error))
    
    def upload_image(self):
        self.result_image_label.config(image="")
        for i in range(6):
            self.labels[i].config(text="")
            
        self.path = filedialog.askopenfilename(filetypes=[("تصاویر", "*.jpg;*.png")])
        if self.path:
            # CARD DETECTION
            self.image = detect_and_crop_national_card(self.path)

            height, width, _ = self.image.shape
            print(height, width)

            display_img = cv2.resize(self.image, (375, 250))
            if height>1055 and width>1665:
                resized_width = int((width / height) * 1055)
                self.image = cv2.resize(self.image, (resized_width, 1055))
                height, width, _ = self.image.shape
                print(height, width)
            
            self.show_image(display_img, self.image_label)
            self.process_btn.config(state="normal")

    def start_processing(self):
        
        # step 1
        self.area = crop_image(self.image)

        # UI: دکمه غیرفعال + نمایش لودر
        self.process_btn.config(state="disabled")
        self.status_lbl.config(text="در حال پردازش... لطفا صبر کنید")
        self.spinner.pack()
        self.spinner.start(10)  # سرعت چرخش

        # اجرای کار سنگین در ترد جدا
        t = threading.Thread(target=self._run_ocr_worker, daemon=True)
        t.start()

    def show_image(self, cv_img, label):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk
