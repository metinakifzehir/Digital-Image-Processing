import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np


class PhotoEditor:
    def __init__(self, root):
        self.img = None
        self.root = root
        self.root.title("Photo Editor")
        self.file_path1 = None
        self.file_path2 = None
        self.image1 = None
        self.image2 = None
        self.root.geometry("995x495")
        photo_frame = tk.Frame(root)
        photo_frame.grid(row=0, column=1, rowspan=7, sticky="nsew")
        self.photo_label1 = tk.Label(photo_frame)
        self.photo_label2 = tk.Label(photo_frame)
        self.photo_label1.grid(row=0, column=0, padx=5, sticky="s")
        self.photo_label2.grid(row=0, column=1, rowspan=2, padx=5, sticky="nsew")
        select_button = tk.Button(root, text=" Select File ", command=self.load_images)
        select_button.grid(row=0, column=0, pady=20, padx=10)
        child_frame = tk.Frame(root)
        child_frame.grid(row=1, column=0)
        change_button1 = tk.Button(child_frame, text="  Sharpen  ", command=self.sharpen)
        change_button1.grid(row=0, column=0, pady=10, padx=10)
        change_button2 = tk.Button(child_frame, text="His. Equal.", command=self.equalize_histogram)
        change_button2.grid(row=1, column=0, pady=10, padx=10)
        change_button3 = tk.Button(child_frame, text="Max  Filter", command=self.apply_max_filter)
        change_button3.grid(row=2, column=0, pady=10, padx=10)
        change_button4 = tk.Button(child_frame, text="Min  Filter", command=self.apply_min_filter)
        change_button4.grid(row=3, column=0, pady=10, padx=10)
        change_button5 = tk.Button(child_frame, text="Avg. Filter", command=self.apply_average_filter)
        change_button5.grid(row=4, column=0, pady=10, padx=10)
        change_button6 = tk.Button(child_frame, text="Save", command=self.save)
        change_button6.grid(row=5, column=0, pady=30, padx=10)
        self.kernel_size_slider = tk.Scale(photo_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                           command=self.update_kernel_size)
        self.kernel_size_slider.set(4)
        self.kernel_size_slider.grid(row=1, column=0, sticky="n", padx=10)

    def load_images(self):
        self.file_path1 = filedialog.askopenfilename()
        self.file_path2 = self.file_path1
        self.img = cv2.imread(self.file_path1, cv2.IMREAD_GRAYSCALE)
        if not self.file_path1 or not self.file_path2:
            return
        self.image1 = Image.open(self.file_path1)
        self.image2 = Image.open(self.file_path2)
        self.show_images()

    def show_images(self):
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        aspect_ratio1 = self.image1.width / self.image1.height
        if aspect_ratio1 > 16/9:
            new_width1 = int(window_width / 5)
            new_height1 = int(new_width1 / aspect_ratio1)
            aspect_ratio2 = self.image2.width / self.image2.height
            new_width2 = int(window_width / 5 * 3)
            new_height2 = int(new_width2 / aspect_ratio2)
        else:
            new_height1 = int(window_height / 5)
            new_width1 = int(new_height1 * aspect_ratio1)
            aspect_ratio2 = self.image2.width / self.image2.height
            new_height2 = int(window_height / 5 * 4)
            new_width2 = int(new_height2 * aspect_ratio2)
        resized_image1 = self.image1.resize((new_width1, new_height1))
        resized_image2 = self.image2.resize((new_width2, new_height2))
        tk_image1 = ImageTk.PhotoImage(resized_image1)
        tk_image2 = ImageTk.PhotoImage(resized_image2)
        self.photo_label1.config(image=tk_image1)
        self.photo_label1.image = tk_image1
        self.photo_label2.config(image=tk_image2)
        self.photo_label2.image = tk_image2

    def equalize_histogram(self):
        histogram = np.zeros(256, dtype=int)
        for i in range(self.img.shape[0]):
            for j in range(self.img.shape[1]):
                histogram[self.img[i, j]] += 1
        r, c = self.img.shape
        output = np.zeros((r, c), dtype=np.uint8)
        step1 = histogram / (r * c)
        step2 = np.zeros(256)
        for i in range(256):
            step2[i] = np.sum(step1[:i + 1])
        eq_histogram = np.round(255 * step2).astype(int)
        for i in range(r):
            for j in range(c):
                output[i, j] = eq_histogram[self.img[i, j]]
        self.image2 = Image.fromarray(output)
        self.show_images()

    def update_kernel_size(self, value):
        self.kernel_size = int(value)

    def apply_max_filter(self):
        kernel_size = self.kernel_size
        max_filtered_img = cv2.dilate(self.img, kernel=np.ones((kernel_size, kernel_size), np.uint8))
        self.image2 = Image.fromarray(max_filtered_img)
        self.show_images()

    def apply_min_filter(self):
        kernel_size = self.kernel_size
        min_filtered_img = cv2.erode(self.img, kernel=np.ones((kernel_size, kernel_size), np.uint8))
        self.image2 = Image.fromarray(min_filtered_img)
        self.show_images()

    def apply_average_filter(self):
        kernel_size = self.kernel_size
        average_filtered_img = cv2.blur(self.img, (kernel_size, kernel_size))
        self.image2 = Image.fromarray(average_filtered_img)
        self.show_images()

    def sharpen(self):
        Lap = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        a1 = cv2.filter2D(self.img, cv2.CV_64F, Lap)
        a2 = np.uint8(a1)
        output = np.abs(self.img - a2)
        self.image2 = Image.fromarray(output)
        self.show_images()

    def save(self):
        image3 = np.uint8(self.image2)
        cv2.imwrite("savedImage.jpg", image3)
        tk.messagebox.showinfo("Info", "Your image saved successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoEditor(root)
    root.mainloop()
