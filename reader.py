import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from mfrc522 import SimpleMFRC522
import pygame
import pyperclip
import RPi.GPIO as GPIO
import pandas as pd
import threading

class RFIDApp(ctk.CTk):
    def _init_(self):
        super()._init_()
        GPIO.setwarnings(False)  # Disable GPIO warnings
        self.reader = SimpleMFRC522()
        self.title("iibiye RFID Reader")
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))  # Maximize window on startup

        self.cart_items = []
        
        self.display_cart()

        pygame.mixer.init()
        self.sound = pygame.mixer.Sound('beep.wav')
        print("Starting to read tags...")

        # Start reading tags in a separate thread
        threading.Thread(target=self.read_tag, daemon=True).start()

    def read_tag(self):
        while True:
            try:
                id, text = self.reader.read()
                if id:
                    if id in self.cart_items:
                        serial_number = self.cart_items.index(id) + 1
                        self.show_message(f"Tag ID {id} is already in the list at serial number {serial_number}.")
                    else:
                        self.cart_items.append(id)
                        self.update_cart_display()
                        self.sound.play()
                        print(f"Tag read: {id}")
            except Exception as e:
                print("Error reading tag:", e)
            self.after(1000)  # Continue reading after 1 second

    def display_cart(self):
        self.clear_window()

        container_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        container_frame.pack(expand=True, fill='both', padx=20, pady=20)

        total_frame = ctk.CTkFrame(container_frame, fg_color="#F6F7FB", corner_radius=10)
        total_frame.pack(side='left', fill='y', padx=20, pady=20)

        restart_button = ctk.CTkButton(total_frame, text="Restart", command=self.restart, corner_radius=20, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
        restart_button.pack(pady=10)

        download_button = ctk.CTkButton(total_frame, text="Download", command=self.download, corner_radius=20, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
        download_button.pack(pady=10)

        cart_frame = ctk.CTkFrame(container_frame, fg_color="#F6F7FB", corner_radius=0)
        cart_frame.pack(side='right', expand=True, fill='both', padx=20, pady=20)

        self.cart_display = tk.Canvas(cart_frame, bg="#F6F7FB")
        self.cart_display.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_display.yview)
        scrollbar.pack(side='right', fill='y')
        self.cart_display.configure(yscrollcommand=scrollbar.set)
        self.cart_window = ttk.Frame(self.cart_display)
        self.cart_display.create_window((0, 0), window=self.cart_window, anchor='nw')
        self.cart_window.bind("<Configure>", lambda e: self.cart_display.configure(scrollregion=self.cart_display.bbox("all")))

        self.update_cart_display()
        print("Cart displayed")

    def update_cart_display(self):
        for widget in self.cart_window.winfo_children():
            widget.destroy()
        for index, item in enumerate(self.cart_items, start=1):
            row_frame = ctk.CTkFrame(self.cart_window, fg_color="white", corner_radius=10)
            row_frame.pack(fill='x', pady=5, padx=10)

            serial_label = ctk.CTkLabel(row_frame, text=f"{index}.", font=("Arial", 16), fg_color="white")
            serial_label.pack(side='left', padx=5, pady=5)

            tag_label = ctk.CTkLabel(row_frame, text=f"{item}", font=("Arial", 16), fg_color="white")
            tag_label.pack(side='left', padx=5, pady=5)

            copy_button = ctk.CTkButton(row_frame, text="Copy", command=lambda id=item: self.copy_id(id), corner_radius=10, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
            copy_button.pack(side='right', padx=5, pady=5)

            delete_button = ctk.CTkButton(row_frame, text="Delete", command=lambda id=item: self.delete_id(id), corner_radius=10, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
            delete_button.pack(side='right', padx=5, pady=5)

        print("Cart updated")

    def copy_id(self, id):
        pyperclip.copy(str(id))
        print("ID copied to clipboard")

    def delete_id(self, id):
        if id in self.cart_items:
            self.cart_items.remove(id)
            self.update_cart_display()
            print(f"Tag ID {id} removed from the cart")

    def restart(self):
        self.cart_items = []
        self.update_cart_display()
        print("Cart restarted")

    def download(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", ".xlsx"), ("All files", ".*")])
        if file_path:
            data = {"Tag_Serial_Number": list(range(1, len(self.cart_items) + 1)), "uid": [str(item) for item in self.cart_items]}
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            print(f"File downloaded: {file_path}")

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_message(self, message):
        messagebox.showinfo("Duplicate Tag", message)

    def on_close(self):
        GPIO.cleanup()
        self.destroy()

if _name_ == "_main_":
    app = RFIDApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    print("Application started")
    app.mainloop()