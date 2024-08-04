import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from PIL import Image, ImageTk

from customtkinter import CTkImage
import qrcode
import json
import requests
import threading
import urllib.request

# Configure CustomTkinter appearance and color theme
ctk.set_appearance_mode("Light")  # Set appearance mode to "Light"
ctk.set_default_color_theme("blue")  # Default is "blue"

class SelfCheckoutSystem(ctk.CTk):
    def __init__(self):
       super().__init__()
       self.title("Retail Flash")
       self.iconbitmap("logo.ico")
     
       
       # Manually set the window size to the screen size for a maximized effect
       screen_width = self.winfo_screenwidth()
       screen_height = self.winfo_screenheight()
       self.geometry(f"{screen_width}x{screen_height}+0+0")
       # Set background color for areas not covered by CTk widgets
       self.configure(bg_color="#F6F7FB")

    #    self.products = [
    #         {"Uid": "001", "Name": "Milk", "Price": 1.99, "Image": "milk.jpeg"},
    #         {"Uid": "002", "Name": "Bread", "Price": 2.49, "Image": "Bread.jpeg"},
    #         {"Uid": "003", "Name": "Chips", "Price": 3.49, "Image": "Chips.jpeg"},
    #         {"Uid": "004", "Name": "Cooco coolo", "Price": 9.49, "Image": "coco.jpeg"},
    #         {"Uid": "005", "Name": "Cheese", "Price": 3.49, "Image": "Cheese.jpeg"},
    #         {"Uid": "006", "Name": "Orange Juice", "Price": 9.49, "Image": "OrangeJuice.jpeg"},
    #         {"Uid": "007", "Name": "Apple Juice", "Price": 1.99, "Image": "AppleJuice.jpeg"},
    #         {"Uid": "008", "Name": "Cereal", "Price": 2.49, "Image": "Cereal.jpeg"},
    #         {"Uid": "009", "Name": "Rice", "Price": 3.49, "Image": "Rice.jpeg"},
    #         {"Uid": "0010", "Name": "Pasta", "Price": 9.49, "Image": "Pasta.jpeg"},
    #         {"Uid": "0011", "Name": "Water", "Price": 3.49, "Image": "Water.jpeg"},
    #         {"Uid": "0012", "Name": "Soda", "Price": 9.49, "Image": "Soda.jpeg"},
    #         {"Uid": "0013", "Name": "Cookies", "Price": 3.49, "Image": "Cookies.png"},
    #         {"Uid": "0014", "Name": "Chocolate", "Price": 9.49, "Image": "Chocolate.jpg"},
    #         {"Uid": "0015", "Name": "Yogurt", "Price": 1.99, "Image": "Yogurt.png"},
    #         {"Uid": "0016", "Name": "Ice Cream", "Price": 2.49, "Image": "IceCream.jpeg"},
    #         {"Uid": "0017", "Name": "Frozen Pizza", "Price": 3.49, "Image": "FrozenPizza.jpeg"},
    #         {"Uid": "0018", "Name": "Snack Bars", "Price": 9.49, "Image": "SnackBars.jpeg"},
    #         {"Uid": "0019", "Name": "Coffee", "Price": 3.49, "Image": "Coffee.jpeg"},
    #         {"Uid": "0020", "Name": "Tea", "Price": 9.49, "Image": "Tea.jpeg"},
    #     ]
       self.products = []
       self.scanned_products = []
       self.uid_products = [
           '1046189185985'
       ]

       self.start_screen()
    
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
    def display_loading(self):
        # loading_label = ctk.CTkLabel(self, text="Loading...", font=("Arial", 20), fg_color="#F6F7FB", text_color="black")
        # loading_label.pack(expand=True)

        gif_label = tk.Label(self)
        gif_label.pack(expand=True)
        self.animate_gif(gif_label, "circular_loading1.gif")

    def fetch_product_info(self, uids):
        self.clear_window()
        self.display_loading()

        def fetch_data():
            try:
                url = 'https://retailflash.up.railway.app/api/products/info/uids'
                response = requests.get(url, params={'uids': uids})
                if response.status_code == 200:
                    self.products = response.json()
                    self.display_cart()
                else:
                    self.clear_window()
                    messagebox.showerror("Error", f"Failed to fetch product info. Server returned: {response.status_code}")
            except Exception as e:
                self.clear_window()
                messagebox.showerror("Error", f"An error occurred while fetching product info: {e}")

        threading.Thread(target=fetch_data).start()
    
    def animate_gif(self, label, gif_file):
        gif = Image.open(gif_file)
        self.gif_frames = []  # Initialize the list to hold the frames
        try:
            for frame_num in range(gif.n_frames):
                gif.seek(frame_num)
                # Resize the current frame. Adjust (width, height) as needed.
                # Use Image.Resampling.LANCZOS for high-quality downsampling
                resized_frame = gif.copy().resize((850, 850), Image.Resampling.LANCZOS)  # Resize to 150x150
                frame_image = ImageTk.PhotoImage(resized_frame)  # Create a PhotoImage from the resized frame
                self.gif_frames.append(frame_image)
        except EOFError:
            pass  # The end of the GIF file has been reached

        self.gif_index = 0  # Starting index
        self.update_gif(label)


    def update_gif(self, label):
        frame = self.gif_frames[self.gif_index]
        label.config(image=frame)
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)  # Loop the index
        label.after(20, self.update_gif, label)  # Update every 20ms

    def start_screen(self):
        self.clear_window()
        full_screen_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        full_screen_frame.pack(expand=True, fill='both')

        # Adjust padding to ensure all elements are visible
        center_frame = ctk.CTkFrame(full_screen_frame, fg_color="#F6F7FB", corner_radius=10)
        center_frame.pack(expand=True, padx=20, pady=20)

        prompt_label = ctk.CTkLabel(center_frame, text="Place Items & Click Start Button To Start Checkout",
                                    font=("Arial", 30,"bold"), fg_color="#F6F7FB", text_color="black")
        prompt_label.pack(pady=10)

        # Add GIF animation
        gif_label = tk.Label(center_frame, bg="#F6F7FB")
        gif_label.pack(pady=10)
        self.animate_gif(gif_label, "check_start.gif")

        # Button for starting the scan
        scan_button = ctk.CTkButton(center_frame, text="Start", command=lambda: self.fetch_product_info(self.uid_products),
                                     corner_radius=20, fg_color="#F40000",font=("Arial", 20), hover_color="#C10000")
        
        scan_button.pack(pady=10)




    

    def delete_item(self, uid):
        # Find and remove the product from the list
        self.products = [product for product in self.products if product['uid'] != uid]
        # Refresh the display
        self.display_cart()


    def display_cart(self):
        self.clear_window()
        cart_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        cart_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Scrollable Canvas
        canvas = tk.Canvas(cart_frame)
        scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Function to handle mouse wheel scroll
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # Function to handle touch scrolling
        def on_touch_scroll(event):
            canvas.yview_scroll(int(-1*(event.y - on_touch_scroll.last_y)), "units")
            on_touch_scroll.last_y = event.y

        # Store the starting point of scrolling
        def start_touch_scroll(event):
            on_touch_scroll.last_y = event.y

        # Bind the events
        canvas.bind("<Button-1>", start_touch_scroll)
        canvas.bind("<B1-Motion>", on_touch_scroll)
        self.bind_all("<MouseWheel>", on_mouse_wheel)  # For Windows and MacOS
        self.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))  # For Linux
        self.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))  # For Linux

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for product in self.products:
            row_frame = ctk.CTkFrame(scrollable_frame, fg_color="#F6F7FB", corner_radius=0)
            row_frame.pack(fill='both', expand=True, pady=10, padx=10 )

            # # Image label
            img_path = product['image']
            img_url = "https://retailflash.up.railway.app/" + img_path.replace('\\', '/')
            pil_image = Image.open(urllib.request.urlopen(img_url)).resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_image)
            image_label = tk.Label(row_frame, image=photo)
            image_label.image = photo  # Keep a reference.
            image_label.pack(side='left', padx=10, pady=30)
            # Delete button
            delete_button = ctk.CTkButton(row_frame, text="Delete", command=lambda uid=product['uid']: self.delete_item(uid), fg_color="#F40000", hover_color="#C10000", text_color="white")
            delete_button.pack(side='right', padx=30)
            # Price label
            price_label = ctk.CTkLabel(row_frame, text=f"${product['sellingPrice']:0.3f}", font=("Arial", 16), fg_color="#F6F7FB", text_color="black")
            price_label.pack(side='right', padx=30)

            # Name label
            name_label = ctk.CTkLabel(row_frame, text=product['name'], font=("Arial", 16), fg_color="#F6F7FB", text_color="black")
            name_label.pack(side='left', padx=30)


            

            

        # Configure canvas and scrollbar packing
        canvas.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Total price label
        total_price = sum(p['sellingPrice'] for p in self.products)
        total_label = ctk.CTkLabel(cart_frame, text=f"Total Price: ${total_price:.3f}", font=("Arial", 20), fg_color="#F6F7FB", text_color="black")
        total_label.pack(padx=20, pady=200)

        # Buy button
        buy_button = ctk.CTkButton(cart_frame, text="Buy", command=self.confirm_purchase, corner_radius=20, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
        buy_button.pack(padx=20)

    def confirm_purchase(self):
        response = messagebox.askyesno("Confirm Purchase", "Are you sure you want to buy these items?")
        if response:
            self.generate_qr_code()
            self.display_qr_code()




    def generate_qr_code(self):
        # Gather UIDs and total price
        product_data = {
            'products': self.products,
            'total': f"${sum(product['sellingPrice'] for product in self.products):.2f}"
        }
        # Convert dictionary to JSON string
        qr_info = json.dumps(product_data)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_info)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the QR code as an image file
        img.save("payment_qr.png")


    
    def animate_scan(self, label, gif_file):
        gif = Image.open(gif_file)
        self.gif_frames = []  # Initialize the list to hold the frames
        try:
            for frame_num in range(gif.n_frames):
                gif.seek(frame_num)
                # Resize the current frame. Adjust (width, height) as needed.
                # Use Image.Resampling.LANCZOS for high-quality downsampling
                resized_frame = gif.copy().resize((850, 850), Image.Resampling.LANCZOS)  # Resize to 150x150
                frame_image = ImageTk.PhotoImage(resized_frame)  # Create a PhotoImage from the resized frame
                self.gif_frames.append(frame_image)
        except EOFError:
            pass  # The end of the GIF file has been reached

        self.gif_index = 0  # Starting index
        self.update_scan(label)


    def update_scan(self, label):
        frame = self.gif_frames[self.gif_index]
        label.config(image=frame)
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)  # Loop the index
        label.after(20, self.update_scan, label)  # Update every 20ms

    def display_qr_code(self):
        self.clear_window()
        qr_frame = ctk.CTkFrame(self, fg_color="#F6F7FB", corner_radius=0)
        qr_frame.pack(expand=True, fill='both')

        # Create a frame to hold both QR and GIF side by side, centered
        row_frame = ctk.CTkFrame(qr_frame, fg_color="#F6F7FB")
        row_frame.pack(pady=130)

        # Display the additional image to the left using tk.Label
        scan_image_pil = Image.open("scan.png")  # Make sure this image file exists
        scan_photo = ImageTk.PhotoImage(scan_image_pil.resize((550, 450), Image.Resampling.LANCZOS))
        scan_label = tk.Label(row_frame, image=scan_photo, bg="#F6F7FB")  # Using tk.Label here
        scan_label.image = scan_photo  # Keep a reference
        scan_label.pack(side='left', padx=10)

        # Display the QR code to the right using tk.Label
        qr_image_pil = Image.open("payment_qr.png")
        qr_photo = ImageTk.PhotoImage(qr_image_pil.resize((550, 550), Image.Resampling.LANCZOS))
        qr_label = tk.Label(row_frame, image=qr_photo, bg="#F6F7FB")  # Using tk.Label here
        qr_label.image = qr_photo  # Keep a reference
        qr_label.pack(side='right', padx=10)



       

        # Instruction label below the row frame
        instruction_label = ctk.CTkLabel(qr_frame, text="Open Retail Flash App Payment from Your Mobile then Click Camera Icon In The Center Menu Bottom, and scan the QR code.", font=("Arial", 16), fg_color="#F6F7FB", text_color="black")
        instruction_label.pack(pady=10)

        # "Back" button to return to the cart, placed below the instruction label
        back_button = ctk.CTkButton(qr_frame, text="Back", command=self.display_cart, corner_radius=10, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
        back_button.pack(pady=10)
        back_button = ctk.CTkButton(qr_frame, text="Complete", command=self.start_screen, corner_radius=10, fg_color="#F40000", hover_color="#C10000", font=("Arial", 16))
        back_button.pack(pady=10)

if __name__ == "__main__":
    app = SelfCheckoutSystem()
    app.mainloop()