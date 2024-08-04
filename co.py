import threading
import os
import sys
import customtkinter as ctk
from tkinter import messagebox, simpledialog, ttk, StringVar, IntVar
import tkinter as tk
from PIL import Image, ImageTk
import qrcode
import json
import requests
import urllib.request
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import pygame

# Configure CustomTkinter appearance and color theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class SelfCheckoutSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Retail Flash")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.configure(bg_color="#F6F7FB")
        self.products = self.load_active_products()
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound('beep.wav')
        self.INSTRUCsound = pygame.mixer.Sound('instructor.wav')
        self.confirmsound = pygame.mixer.Sound('confirm.wav')
        self.scanqrcode = pygame.mixer.Sound('scanqrcode.wav')
        self.warning_sound = pygame.mixer.Sound('timerend.wav')

        self.reader = SimpleMFRC522()
        GPIO.setwarnings(False)  # Disable GPIO warnings
        self.cart = []  # Initialize the cart
        self.cart_items = []  # To store cart item widgets
        self.total_price = IntVar(value=0)  # State management for total price
        self.widgets_to_clear = []
        self.rfid_thread_running = True  # Flag to control RFID reading
        self.timer_running = False
        self.start_screen()

    def load_active_products(self):
        # Load all active products from the API
        try:
            url = 'https://retailflash.up.railway.app/api/products/data/getwithstatus'
            response = requests.get(url)
            if response.status_code == 200:
                products = response.json()
                active_products = {product['uid']: product for product in products if product['status'] == 'active'}
                return active_products
            else:
                messagebox.showerror("Error", f"Failed to load products. Server returned: {response.status_code}")
                return {}
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading products: {e}")
            return {}

    def clear_window(self):
        for widget in self.widgets_to_clear:
            try:
                widget.destroy()
            except Exception as e:
                print(f"Error while destroying widget: {e}")
        self.widgets_to_clear.clear()

    def fetch_product_info(self, uid):
        uid_str = str(uid)  # Convert UID to string
        print(f"Reading UID: {uid_str}")
        print(f"Available UIDs: {self.products.keys()}")
        if uid_str in self.products:
            product = self.products[uid_str]
            self.add_product_to_cart(product)
        else:
            messagebox.showerror("Error", "Product not found.")

    def start_screen(self):
        self.clear_window()
        full_screen_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        full_screen_frame.pack(expand=True, fill='both')
        self.widgets_to_clear.append(full_screen_frame)
        center_frame = ctk.CTkFrame(full_screen_frame, fg_color="#F6F7FB", corner_radius=10)
        center_frame.pack(expand=True, padx=20, pady=20)
        self.widgets_to_clear.append(center_frame)

        prompt_label = ctk.CTkLabel(center_frame, text="Place The RFID Tag Of Product near the reader...",
                                    font=("Arial", 30, "bold"), fg_color="#F6F7FB", text_color="black")
        prompt_label.pack(pady=10)
        self.widgets_to_clear.append(prompt_label)

        gif_label = tk.Label(center_frame, bg="#F6F7FB")
        gif_label.pack(pady=10)
        self.widgets_to_clear.append(gif_label)
        self.animate_gif(gif_label, "start.gif")

        scan_button = ctk.CTkButton(center_frame, text="Start", command=self.display_rfid_instructions,
                                    corner_radius=20, fg_color="#F40000", font=("Arial", 20), hover_color="#C10000")
        scan_button.pack(pady=10)
        self.widgets_to_clear.append(scan_button)

    def display_rfid_instructions(self):
        self.clear_window()
        self.INSTRUCsound.play()
        self.display_cart()
        instruction_label = ctk.CTkLabel(self, text="Place the RFID tag of the product in the RFID reader",
                                         font=("Arial", 14, "bold"), fg_color="#F6F7FB", text_color="black")
        instruction_label.pack(pady=10)
        self.widgets_to_clear.append(instruction_label)
        self.start_rfid_reader()

    def start_rfid_reader(self):
        self.rfid_thread_running = True
        threading.Thread(target=self.read_rfid).start()

    def read_rfid(self):
        try:
            print("Place your RFID tag near the reader...")
            while self.rfid_thread_running:
                id, text = self.reader.read()
                print(f"ID: {id}")
                print(f"Text: {text}")
                self.sound.play()
                self.fetch_product_info(id)
                time.sleep(2)  # Small delay to avoid multiple reads of the same tag
        finally:
            GPIO.cleanup()

    def stop_rfid_reader(self):
        self.rfid_thread_running = False

    def delete_item(self, uid):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            self.cart = [product for product in self.cart if product['uid'] != uid]
            self.update_cart_display()

    def display_cart(self):
        self.clear_window()

        cart_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        cart_frame.pack(expand=True, fill='both', padx=20, pady=20)
        self.widgets_to_clear.append(cart_frame)

        self.cart_display = tk.Frame(cart_frame, bg="#F6F7FB")
        self.cart_display.pack(expand=True, fill='both')
        self.widgets_to_clear.append(self.cart_display)

        total_label = ctk.CTkLabel(cart_frame, textvariable=self.total_price, font=("Arial", 20), fg_color="#F6F7FB", text_color="black")
        total_label.pack(padx=20, pady=10)
        self.widgets_to_clear.append(total_label)

        buy_button = ctk.CTkButton(cart_frame, text="Buy", command=self.confirm_purchase, corner_radius=20, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
        buy_button.pack(padx=20)
        self.widgets_to_clear.append(buy_button)

        self.update_cart_display()

    def update_cart_display(self):
        for widget in self.cart_items:
            widget.destroy()
        self.cart_items.clear()

        for product in self.cart:
            row_frame = tk.Frame(self.cart_display, bg="#F6F7FB")
            row_frame.pack(fill='x', pady=10, padx=10)
            self.cart_items.append(row_frame)

            img_path = product['image']
            img_url = "https://retailflash.up.railway.app/" + img_path.replace('\\', '/')
            pil_image = Image.open(urllib.request.urlopen(img_url)).resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_image)
            image_label = tk.Label(row_frame, image=photo, bg="#F6F7FB")
            image_label.image = photo
            image_label.pack(side='left', padx=10, pady=10)
            self.cart_items.append(image_label)

            name_label = tk.Label(row_frame, text=product['name'], font=("Arial", 16), bg="#F6F7FB", fg="black")
            name_label.pack(side='left', padx=30)
            self.cart_items.append(name_label)

            price_label = tk.Label(row_frame, text=f"${product['sellingPrice']:0.3f}", font=("Arial", 16), bg="#F6F7FB", fg="black")
            price_label.pack(side='right', padx=30)
            self.cart_items.append(price_label)

            delete_button = ctk.CTkButton(row_frame, text="Delete", command=lambda uid=product['uid']: self.delete_item(uid), fg_color="#F40000", hover_color="#C10000", text_color="white")
            delete_button.pack(side='right', padx=30)
            self.cart_items.append(delete_button)

        total_price = sum(product['sellingPrice'] for product in self.cart)
        self.total_price.set(f"Total Price: ${total_price:.3f}")

    def confirm_purchase(self):
        if not self.cart:
            messagebox.showinfo("Info", "Your cart is empty.")
            return

        self.confirmsound.play()
        response = messagebox.askyesno("Confirm Purchase", "Are you sure you want to buy these items?")

        if response:
            self.stop_rfid_reader()  # Stop the RFID reader
            self.generate_qr_code()
            self.display_qr_code()

    def generate_qr_code(self):
        product_data = {
            'uid': [product['uid'] for product in self.cart],
            'total': f"${sum(product['sellingPrice'] for product in self.cart):.2f}"
        }
        qr_info = json.dumps(product_data)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,
            border=4,
        )
        qr.add_data(qr_info)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("payment_qr.png")  # Save to a known location

    def animate_gif(self, label, gif_file):
        gif = Image.open(gif_file)
        self.gif_frames = []
        try:
            for frame_num in range(gif.n_frames):
                gif.seek(frame_num)
                resized_frame = gif.copy().resize((250, 250), Image.Resampling.LANCZOS)
                frame_image = ImageTk.PhotoImage(resized_frame)
                self.gif_frames.append(frame_image)
        except EOFError:
            pass
        self.gif_index = 0
        self.update_scan(label)

    def update_scan(self, label):
        if self.gif_frames:
            frame = self.gif_frames[self.gif_index]
            label.config(image=frame)
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            label.after(20, self.update_scan, label)

    def display_qr_code(self):
        self.clear_window()
        self.scanqrcode.play()
        qr_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        qr_frame.pack(expand=True, fill='both')
        self.widgets_to_clear.append(qr_frame)

        qr_image_pil = Image.open("payment_qr.png")
        qr_photo = ImageTk.PhotoImage(qr_image_pil.resize((300, 300), Image.Resampling.LANCZOS))  # Adjust size as needed
        qr_label = tk.Label(qr_frame, image=qr_photo, bg="#F6F7FB")
        qr_label.image = qr_photo
        qr_label.pack(pady=20)
        self.widgets_to_clear.append(qr_label)

        instruction_label = ctk.CTkLabel(qr_frame, text="Open Retail Flash App on your mobile, click the camera icon in the center menu at the bottom, and scan the QR code.", font=("Arial", 16), fg_color="#F6F7FB", text_color="black", wraplength=400)
        instruction_label.pack(pady=10)
        self.widgets_to_clear.append(instruction_label)

        self.timer_label = ctk.CTkLabel(qr_frame, text="", font=("Arial", 16), fg_color="#F6F7FB", text_color="#F40000")
        self.timer_label.pack(pady=10)
        self.widgets_to_clear.append(self.timer_label)

        complete_button = ctk.CTkButton(qr_frame, text="Complete", command=self.restart_application, corner_radius=20, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
        complete_button.pack(pady=10)
        self.widgets_to_clear.append(complete_button)

        self.start_timer(90)

    def start_timer(self, duration):
        self.time_remaining = duration
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            mins, secs = divmod(self.time_remaining, 60)
            time_format = f'{mins:02}:{secs:02}'
            self.timer_label.configure(text=f"Time remaining: {time_format}")
            if self.time_remaining == 16:
                self.warning_sound.play()  # Play the warning sound when 16 seconds are remaining
            if self.time_remaining > 0:
                self.time_remaining -= 1
                self.after(1000, self.update_timer)
            else:
                self.restart_application()

    def restart_application(self):
        self.timer_running = False
        self.clear_window()
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def add_product_to_cart(self, product):
        if any(p['uid'] == product['uid'] for p in self.cart):
            self.display_duplicate_message()
        else:
            self.cart.append(product)
            self.update_cart_display()

    def display_duplicate_message(self):
        duplicate_label = ctk.CTkLabel(self, text="Product already in cart.", font=("Arial", 20), fg_color="#F6F7FB", text_color="red")
        duplicate_label.pack(pady=10)
        self.widgets_to_clear.append(duplicate_label)
        self.after(3000, duplicate_label.destroy)  # Remove the label after 3 seconds


if __name__ == "__main__":
    self_checkout_app = SelfCheckoutSystem()
    self_checkout_app.mainloop()
