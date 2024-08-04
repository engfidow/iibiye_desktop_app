import threading
import os
import sys
import customtkinter as ctk
from tkinter import messagebox, StringVar
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
import qrcode
import json
import requests
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import pygame

# Configure CustomTkinter appearance and color theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class SelfCheckoutSystem(ctk.CTk):
    def _init_(self):
        super()._init_()
        self.title("Iibiye")

        # Set the window to full screen
        self.attributes('-fullscreen', True)

        # If you want an option to exit full screen, you can bind a key (e.g., 'Esc')
        self.bind("<Escape>", self.exit_fullscreen)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.configure(bg="#F6F7FB")
        self.products = self.load_active_products()
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Pygame audio initialization failed")

        self.sound = pygame.mixer.Sound("beep.wav")
        self.INSTRUCsound = pygame.mixer.Sound("instructor.wav")
        self.confirmsound = pygame.mixer.Sound("confirm.wav")
        self.scanqrcode = pygame.mixer.Sound("scanqrcode.wav")
        self.warning_sound = pygame.mixer.Sound("timerend.wav")

        self.reader = SimpleMFRC522()
        GPIO.setwarnings(False)  # Disable GPIO warnings
        self.cart = []  # Initialize the cart
        self.cart_items = []  # To store cart item widgets
        self.total_price = StringVar()  # State management for total price
        self.widgets_to_clear = []
        self.rfid_thread_running = True  # Flag to control RFID reading
        self.timer_running = False
        self.start_screen()

    def exit_fullscreen(self, event=None):
        self.attributes('-fullscreen', False)

    def load_active_products(self):
        # Load all active products from the API
        try:
            url = "https://iibiye.up.railway.app/api/products/data/getwithstatus"
            response = requests.get(url)
            if response.status_code == 200:
                products = response.json()
                active_products = {
                    product["uid"]: product
                    for product in products
                    if product["status"] == "active"
                }
                return active_products
            else:
                messagebox.showerror(
                    "Error",
                    f"Failed to load products. Server returned: {response.status_code}",
                )
                return {}
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred while loading products: {e}"
            )
            return {}

    def clear_window(self):
        for widget in self.widgets_to_clear:
            try:
                if widget.winfo_exists():
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
        full_screen_frame.pack(expand=True, fill="both")
        self.widgets_to_clear.append(full_screen_frame)

        center_frame = ctk.CTkFrame(
            full_screen_frame, fg_color="#F6F7FB", corner_radius=10
        )
        center_frame.pack(expand=True, padx=20, pady=20)
        self.widgets_to_clear.append(center_frame)

        prompt_label = ctk.CTkLabel(
            center_frame,
            text="Place The RFID Tag Of Product near the reader...",
            font=("Arial", 30, "bold"),
            fg_color="#F6F7FB",
            text_color="black",
        )
        prompt_label.pack(pady=10)
        self.widgets_to_clear.append(prompt_label)

        gif_label = tk.Label(center_frame, bg="#F6F7FB")
        gif_label.pack(pady=10)
        self.widgets_to_clear.append(gif_label)
        self.animate_gif(gif_label, "start.gif")

        scan_button = ctk.CTkButton(
            center_frame,
            text="Start",
            command=self.display_rfid_instructions,
            corner_radius=20,
            fg_color="#F40000",
            font=("Arial", 20),
            hover_color="#C10000",
        )
        scan_button.pack(pady=10)
        self.widgets_to_clear.append(scan_button)

    def display_rfid_instructions(self):
        self.clear_window()
        self.INSTRUCsound.play()
        self.display_cart()
        instruction_label = ctk.CTkLabel(
            self,
            text="Place the RFID tag of the product in the RFID reader",
            font=("Arial", 14, "bold"),
            fg_color="#F6F7FB",
            text_color="black",
        )
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
                time.sleep(1)  # Small delay to avoid multiple reads of the same tag
        finally:
            GPIO.cleanup()

    def stop_rfid_reader(self):
        self.rfid_thread_running = False

    def add_product_to_cart(self, product):
        if any(p["uid"] == product["uid"] for p in self.cart):
            self.display_duplicate_message()
        else:
            self.cart.append(product)
            self.update_cart_display()

    def display_duplicate_message(self):
        duplicate_label = ctk.CTkLabel(
            self,
            text="Product already in cart.",
            font=("Arial", 20),
            fg_color="#F6F7FB",
            text_color="red",
        )
        duplicate_label.pack(pady=10)
        self.widgets_to_clear.append(duplicate_label)
        self.after(3000, duplicate_label.destroy)  # Remove the label after 3 seconds

    def delete_item(self, uid):
        if messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this item?"
        ):
            self.cart = [product for product in self.cart if product["uid"] != uid]
            self.update_cart_display()

    def display_cart(self):
        self.clear_window()

        container_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        container_frame.pack(expand=True, fill="both", padx=20, pady=20)
        self.widgets_to_clear.append(container_frame)

        total_frame = ctk.CTkFrame(
            container_frame, fg_color="#F6F7FB", corner_radius=10
        )
        total_frame.pack(side="left", fill="y", padx=20, pady=20)
        self.widgets_to_clear.append(total_frame)

        total_label = ctk.CTkLabel(
            total_frame,
            textvariable=self.total_price,
            font=("Arial", 20),
            fg_color="#F6F7FB",
            text_color="black",
        )
        total_label.pack(pady=10)
        self.widgets_to_clear.append(total_label)

        buy_button = ctk.CTkButton(
            total_frame,
            text="Buy",
            command=self.confirm_purchase,
            corner_radius=20,
            fg_color="#F40000",
            hover_color="#C10000",
            font=("Arial", 16),
        )
        buy_button.pack(pady=10)
        self.widgets_to_clear.append(buy_button)

        cart_frame = ctk.CTkFrame(container_frame, fg_color="#F6F7FB", corner_radius=0)
        cart_frame.pack(side="right", expand=True, fill="both", padx=20, pady=20)
        self.widgets_to_clear.append(cart_frame)

        self.cart_display = tk.Canvas(cart_frame, bg="#F6F7FB")
        self.cart_display.pack(side="left", fill="both", expand=True)
        self.widgets_to_clear.append(self.cart_display)

        scrollbar = ttk.Scrollbar(
            cart_frame, orient="vertical", command=self.cart_display.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.cart_display.configure(yscrollcommand=scrollbar.set)
        self.cart_window = ttk.Frame(self.cart_display)
        self.cart_display.create_window((0, 0), window=self.cart_window, anchor="nw")
        self.cart_window.bind(
            "<Configure>",
            lambda e: self.cart_display.configure(
                scrollregion=self.cart_display.bbox("all")
            ),
        )

        self.update_cart_display()

    def update_cart_display(self):
        for widget in self.cart_items:
            try:
                if widget.winfo_exists():
                    widget.destroy()
            except tk.TclError:
                pass
        self.cart_items.clear()

        for product in self.cart:
            row_frame = ctk.CTkFrame(
                self.cart_window, fg_color="#F6F7FB", corner_radius=0
            )
            row_frame.pack(fill="both", expand=True, pady=10, padx=10)
            self.cart_items.append(row_frame)

            name_label = ctk.CTkLabel(
                row_frame,
                text=product["name"],
                font=("Arial", 16),
                fg_color="#F6F7FB",
                text_color="black",
            )
            name_label.pack(side="left", padx=30)
            self.cart_items.append(name_label)

            delete_button = ctk.CTkButton(
                row_frame,
                text="Delete",
                command=lambda uid=product["uid"]: self.delete_item(uid),
                fg_color="#F40000",
                hover_color="#C10000",
                text_color="white",
            )
            delete_button.pack(side="right", padx=30)
            self.cart_items.append(delete_button)

            price_label = ctk.CTkLabel(
                row_frame,
                text=f"${product['sellingPrice']:0.3f}",
                font=("Arial", 16),
                fg_color="#F6F7FB",
                text_color="black",
            )
            price_label.pack(side="right", padx=30)
            self.cart_items.append(price_label)

        total_price = sum(product["sellingPrice"] for product in self.cart)
        self.total_price.set(f"Total Price: ${total_price:.3f}")

    def confirm_purchase(self):
        if not self.cart:
            messagebox.showinfo("Info", "Your cart is empty.")
            return

        self.confirmsound.play()
        response = messagebox.askyesno(
            "Confirm Purchase", "Are you sure you want to buy these items?"
        )

        if response:
            self.stop_rfid_reader()  # Stop the RFID reader
            self.generate_qr_code()
            self.display_qr_code()

    def generate_qr_code(self):
        product_data = {
            "uid": [product["uid"] for product in self.cart],
            "total": f"${sum(product['sellingPrice'] for product in self.cart):.2f}",
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
        qr_frame.pack(expand=True, fill="both")
        self.widgets_to_clear.append(qr_frame)

        qr_image_pil = Image.open("payment_qr.png")
        qr_photo = ImageTk.PhotoImage(
            qr_image_pil.resize((300, 300), Image.Resampling.LANCZOS)
        )  # Adjust size as needed
        qr_label = tk.Label(qr_frame, image=qr_photo, bg="#F6F7FB")
        qr_label.image = qr_photo
        qr_label.pack(pady=20)
        self.widgets_to_clear.append(qr_label)

        instruction_label = ctk.CTkLabel(
            qr_frame,
            text="Open Iibiye App on your mobile, click the camera icon in the center menu at the bottom, and scan the QR code.",
            font=("Arial", 16),
            fg_color="#F6F7FB",
            text_color="black",
            wraplength=400,
        )
        instruction_label.pack(pady=10)
        self.widgets_to_clear.append(instruction_label)

        self.timer_label = ctk.CTkLabel(
            qr_frame,
            text="",
            font=("Arial", 16),
            fg_color="#F6F7FB",
            text_color="#F40000",
        )
        self.timer_label.pack(pady=10)
        self.widgets_to_clear.append(self.timer_label)

        # Add "I don't have a smartphone" button
        no_smartphone_button = ctk.CTkButton(
            qr_frame,
            text="I don't have a smartphone",
            command=self.payment_method_screen,
            corner_radius=20,
            fg_color="#F40000",
            hover_color="#C10000",
            font=("Arial", 16),
        )
        no_smartphone_button.pack(pady=10)
        self.widgets_to_clear.append(no_smartphone_button)

        # Add "Complete" button with confirmation dialog
        complete_button = ctk.CTkButton(
            qr_frame,
            text="Complete",
            command=self.complete_transaction,
            corner_radius=20,
            fg_color="#F40000",
            hover_color="#C10000",
            font=("Arial", 16),
        )
        complete_button.pack(pady=10)
        self.widgets_to_clear.append(complete_button)

        self.start_timer(90)

    def complete_transaction(self):
        response = messagebox.askyesno(
            "Complete Purchase",
            "Are you sure you want to complete the transaction? All data will be cleared and registered.",
        )
        if response:
            self.restart_application()

    def payment_method_screen(self):
        self.clear_window()
        payment_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        payment_frame.pack(expand=True, fill="both")
        self.widgets_to_clear.append(payment_frame)

        payment_label = ctk.CTkLabel(
            payment_frame,
            text="Fadlan Gali Number Ka Lacakta Aad Ka Direeso",
            font=("Arial", 20),
            fg_color="#F6F7FB",
            text_color="black",
        )
        payment_label.pack(pady=20)
        self.widgets_to_clear.append(payment_label)

        self.phone_number_var = StringVar()
        phone_number_entry = ctk.CTkEntry(
            payment_frame,
            textvariable=self.phone_number_var,
            placeholder_text="Enter your phone number",
            font=("Arial", 16),
            corner_radius=10,
            fg_color="#FFFFFF",  # White background color
            text_color="#000000",  # Black text color
            placeholder_text_color="#A8B3D3",
            border_color="#F40000",  # Light grey border color
            border_width=2,  # Border width
            width=200,
            height=30,
        )
        phone_number_entry.pack(pady=20, padx=30)
        self.widgets_to_clear.append(phone_number_entry)

        make_payment_button = ctk.CTkButton(
            payment_frame,
            text="Make Payment",
            command=self.make_payment,
            corner_radius=20,
            fg_color="#F40000",
            hover_color="#C10000",
            font=("Arial", 16),
        )
        make_payment_button.pack(pady=20)
        self.widgets_to_clear.append(make_payment_button)

    def make_payment(self):
        phone_number = self.phone_number_var.get()
        if len(phone_number) != 9 or not phone_number.isdigit():
            messagebox.showerror("Error", "Please enter a valid 9-digit phone number.")
            return

        self.show_loading_screen()
        threading.Thread(target=self.process_transaction, args=(phone_number,)).start()

    def show_loading_screen(self):
        self.clear_window()

        full_screen_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        full_screen_frame.pack(expand=True, fill="both")
        self.widgets_to_clear.append(full_screen_frame)
        center_frame = ctk.CTkFrame(
            full_screen_frame, fg_color="#F6F7FB", corner_radius=10
        )
        center_frame.pack(expand=True, padx=20, pady=20)
        self.widgets_to_clear.append(center_frame)

        loading_label = ctk.CTkLabel(
            center_frame,
            text="Processing your payment...",
            font=("Arial", 20),
            fg_color="#F6F7FB",
            text_color="black",
        )
        loading_label.pack(pady=20)
        self.widgets_to_clear.append(loading_label)

        gif_label = tk.Label(center_frame, bg="#F6F7FB")
        gif_label.pack(pady=10)
        self.widgets_to_clear.append(gif_label)
        self.animate_gif(gif_label, "circular_loading1.gif")

    def close_loading_screen(self):
        self.clear_window()
        self.payment_method_screen()

    def process_transaction(self, phone_number):
        try:
            # Prepare the product data for the transaction
            products_list = []
            for product in self.cart:
                try:
                    product_uid = product["_id"]  # Ensure productUid is a string
                    products_list.append({"productUid": product_uid})
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid product UID format: {e}")
                    return
             
            product_data = {
                "userCustomerId": "668445e9e4112e093e3eab21",  # Replace with actual user ID
                "productsList": products_list,
                "paymentMethod": "EVC-PLUS",
                "paymentPhone": phone_number,
                "totalPrice": sum(product["sellingPrice"] for product in self.cart),
            }

            # Send the transaction request to the server
            
            response = requests.post(
                "https://iibiye.up.railway.app/api/transactions", json=product_data
            )

            if response.status_code == 201:
                self.close_loading_screen()
                messagebox.showinfo("Success", "Transaction successful.")
                self.restart_application()
            else:
                self.close_loading_screen()
                error_message = response.json().get("message", "Unknown error")
                messagebox.showerror("Error", f"Transaction failed: {error_message}")
                self.payment_method_screen()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Network error occurred: {e}")
            self.payment_method_screen()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.payment_method_screen()

    def start_timer(self, duration):
        self.time_remaining = duration
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            mins, secs = divmod(self.time_remaining, 60)
            time_format = f"{mins:02}:{secs:02}"
            print(f"Updating timer: {time_format}")  # Debugging statement
            self.timer_label.configure(text=f"Time remaining: {time_format}")
            if self.time_remaining == 16:
                print("Playing warning sound")  # Debugging statement
                self.warning_sound.play()  # Play the warning sound when 16 seconds are remaining
            if self.time_remaining > 0:
                self.time_remaining -= 1
                self.after(1000, self.update_timer)
            else:
                print("Restarting application")  # Debugging statement
                self.restart_application()

    def restart_application(self):
        self.timer_running = False
        self.clear_window()
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

if _name_ == "_main_":
    self_checkout_app = SelfCheckoutSystem()
    self_checkout_app.mainloop()