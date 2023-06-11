import threading
import tkinter as tk

import keyboard
import numpy as np
from PIL import Image, ImageTk
import time

class GUI(tk.Frame):
    def __init__(self, bot,master=None):
        super().__init__(master)
        self.img_size = (800, 800)
        self.bot = bot
        self.master = master
        self.pack()
        self.create_widgets()
        self.update_time()
        self.update_img()
        self.update_stop()


    def create_widgets(self):
        # 创建一个标签，用于展示图片
        self.img_label = tk.Label(self)
        self.img_label.pack()

        # 加载图片
        self.img = Image.fromarray(np.uint8(self.bot.perception))
        self.img = self.img.resize(self.img_size)
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.img_label.config(image=self.img_tk)

        # 创建一个标签，用于展示时间
        self.time_label = tk.Label(self, text=time.strftime("%Y-%m-%d %H:%M:%S"))
        self.time_label.pack()

        # 创建一个开始按钮
        self.start_button = tk.Button(self, text="开始", command=self.start_bot)
        self.start_button.pack()

        # 创建一个结束按钮
        self.stop_button = tk.Button(self, text="结束", command=self.stop_bot)
        self.stop_button.pack()

        # 创建一个标签，用于展示 helloworld
        self.hello_label = tk.Label(self, text="helloworld", font=("Helvetica", 24))
        self.hello_label.pack()

        # robot
        self.robot_thread = None

    def start_bot(self):
        # 检测线程是否已经在运行
        if self.robot_thread is not None and self.robot_thread.is_alive():
            return
        # 创建一个新的线程来运行机器人程序
        time.sleep(3)
        self.robot_thread = threading.Thread(target=self.bot.run)
        self.robot_thread.daemon = True
        self.robot_thread.start()

    def stop_bot(self):
        self.bot.stop()

    def update_stop(self):
        if keyboard.is_pressed("q"):
            self.bot.stop()
        self.after(100, self.update_stop)

    def update_time(self):
        self.time_label.config(text=time.strftime("%Y-%m-%d %H:%M:%S"))
        self.after(100, self.update_time)

    def update_img(self):
        # 加载图片
        self.img = Image.fromarray(np.uint8(self.bot.perception))
        # bgr2rgb
        #self.img = self.img.convert('RGB')
        self.img = self.img.resize(self.img_size)
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.img_label.config(image=self.img_tk)
        self.after(100, self.update_img)

if __name__ == '__main__':
    pass