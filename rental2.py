import psycopg2
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import bcrypt
import collections
from datetime import datetime

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="rental",
            user="postgres",
            password="erpeelenem",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None

class RentalSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Rental Mobil")
        self.conn = connect_db()
        self.create_widgets()
        self.customer_id = None

        # Inisialisasi struktur data
        self.car_data_temp = {}  # HashMap untuk menyimpan data mobil
        self.rental_requests = collections.deque() # Queue untuk menyimpan pengajuan peminjaman
        self.customer_data = {}  # Dictionary untuk menyimpan data customer

        self.load_rental_requests()
        self.load_customer_data()
        
    def create_widgets(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(padx=10, pady=10)

        self.admin_btn = tk.Button(self.menu_frame, text="Login Admin", command=self.admin_login)
        self.admin_btn.grid(row=0, column=0, padx=5, pady=5)

        self.customer_btn = tk.Button(self.menu_frame, text="Login Customer", command=self.customer_login)
        self.customer_btn.grid(row=0, column=1, padx=5, pady=5)

        self.register_btn = tk.Button(self.menu_frame, text="Register", command=self.open_register_window)
        self.register_btn.grid(row=0, column=2, padx=5, pady=5)

    def admin_login(self):
        username = simpledialog.askstring("Username", "Masukkan username admin:")
        password = simpledialog.askstring("Password", "Masukkan password admin:", show="*")
        if self.validate_admin(username, password):
            self.open_admin_dashboard()
        else:
            messagebox.showerror("Error", "Username atau password salah!")

    def validate_admin(self, username, password):
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM admins WHERE username=%s AND password=%s"
            cursor.execute(query, (username, password))
            admin = cursor.fetchone()
            cursor.close()
            return admin is not None
        except Exception as e:
            print(f"Error: {e}")
            return False

    def customer_login(self):
        self.customer_login_window()

    def customer_login_window(self):
        self.current_customer = None
        global customer_login_window
        customer_login_window = tk.Toplevel(self.root)
        customer_login_window.title("Login Customer")
        customer_login_window.geometry("800x700")
        customer_login_window.configure(bg="#f8f9fa")
        
        frame = tk.Frame(customer_login_window, bg="#f8f9fa")
        frame.pack(expand=True)

        global entry_email, entry_password
        
        label_login = tk.Label(frame, text="Login Customer", bg="#f8f9fa", fg="#000814", font=("Montserrat", 30))
        label_login.grid(row=0, column=0, columnspan=2, sticky="news", pady=40)
        
        label_email = tk.Label(frame, text="Email", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16))
        label_email.grid(row=1, column=0, sticky="w", padx=20, pady=10)
        entry_email = tk.Entry(frame, font=("Montserrat", 16))
        entry_email.grid(row=1, column=1, pady=10)
        
        label_password = tk.Label(frame, text="Password", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16))
        label_password.grid(row=2, column=0, sticky="w", padx=20, pady=10)
        entry_password = tk.Entry(frame, show="*", font=("Montserrat", 16))
        entry_password.grid(row=2, column=1, pady=10)
        
        login_btn = tk.Button(frame, text="Login", bg="#001d3d", fg="#ffffff", font=("Montserrat", 16), command=self.handle_login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        label_havent_account = tk.Label(frame, text="Belum punya akun?", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16))
        label_havent_account.grid(row=4, column=0, columnspan=2, pady=10)
        
        register_btn = tk.Button(frame, text="Register", bg="#001d3d", fg="#ffffff", font=("Montserrat", 16), command=self.open_register_window)
        register_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
    def handle_login(self):
        email = entry_email.get()
        password = entry_password.get()
        if self.validate_customer(email, password):
            self.open_customer_dashboard()
        else:
            messagebox.showerror("Error", "Email atau password salah!")
    
    def validate_customer(self, email, password):
        try:
            cursor = self.conn.cursor()
            query = "SELECT customer_id, full_name, password FROM customers WHERE email=%s"
            cursor.execute(query, (email,))
            customer = cursor.fetchone()
            cursor.close()
            if customer and bcrypt.checkpw(password.encode(), customer[2].encode()):
                self.current_customer = customer  # menyimpan data customer yang sedang login
                self.customer_id = customer[0]  # menyimpan customer_id
                return True
            else:
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def open_register_window(self):
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Register Customer")
        self.register_window.geometry("800x700")
        self.register_window.configure(bg="#f8f9fa")
        
        frame = tk.Frame(self.register_window, bg="#f8f9fa")
        frame.pack(expand=True)
        
        label_register = tk.Label(frame, text="Register Customer", bg="#f8f9fa", fg="#000814", font=("Montserrat", 30))
        label_register.grid(row=0, column=0, columnspan=2, sticky="news", pady=40)

        tk.Label(frame, text="Nama Lengkap", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16)).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.entry_full_name = tk.Entry(frame, font=("Montserrat", 16))
        self.entry_full_name.grid(row=1, column=1, pady=10)

        tk.Label(frame, text="Email", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16)).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        self.entry_email = tk.Entry(frame, font=("Montserrat", 16))
        self.entry_email.grid(row=2, column=1, pady=10)

        tk.Label(frame, text="Password", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16)).grid(row=3, column=0, sticky="w", padx=20, pady=10)
        self.entry_password = tk.Entry(frame, show="*", font=("Montserrat", 16))
        self.entry_password.grid(row=3, column=1, pady=10)
        
        tk.Label(frame, text="No. Telepon", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16)).grid(row=4, column=0, sticky="w", padx=20, pady=10)
        self.entry_phone = tk.Entry(frame, font=("Montserrat", 16))
        self.entry_phone.grid(row=4, column=1, pady=10)
        
        tk.Label(frame, text="Alamat", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16)).grid(row=5, column=0, sticky="w", padx=20, pady=10)
        self.entry_address = tk.Entry(frame, font=("Montserrat", 16))
        self.entry_address.grid(row=5, column=1, pady=10)

        register_btn = tk.Button(frame, text="Register", bg="#001d3d", fg="#ffffff", font=("Montserrat", 16), command=self.register_user)
        register_btn.grid(row=6, column=0, columnspan=2, pady=20)
        
        label_have_account = tk.Label(frame, text="Sudah punya akun?", bg="#f8f9fa", fg="#001d3d", font=("Montserrat", 16))
        label_have_account.grid(row=7, column=0, columnspan=2, pady=10)
        
        login_btn = tk.Button(frame, text="Login", bg="#001d3d", fg="#ffffff", font=("Montserrat", 16), command=self.customer_login_window)
        login_btn.grid(row=8, column=0, columnspan=2, pady=10)

    def register_user(self):
        full_name = self.entry_full_name.get()
        email = self.entry_email.get()
        password = self.entry_password.get()
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        phone = self.entry_phone.get()
        address = self.entry_address.get()

        try:
            cursor = self.conn.cursor()
            query = "INSERT INTO customers (full_name, email, password, phone, address) VALUES (%s, %s, %s, %s, %s) RETURNING customer_id"
            cursor.execute(query, (full_name, email, hashed_password, phone, address))
            customer_id = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            
            # Tambahkan customer baru ke dictionary
            self.customer_data[customer_id] = {
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'address': address
            }

            messagebox.showinfo("Success", "Registrasi berhasil")
            self.register_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal melakukan registrasi: {e}")
            self.conn.rollback()

    def load_customer_data(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT customer_id, full_name, email, phone, address FROM customers"
            cursor.execute(query)
            customers = cursor.fetchall()
            cursor.close()

            # Memasukkan data customer ke dalam dictionary
            for customer in customers:
                customer_id, full_name, email, phone, address = customer
                self.customer_data[customer_id] = {
                    'full_name': full_name,
                    'email': email,
                    'phone': phone,
                    'address': address
                }
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data customer: {e}")

    def open_admin_dashboard(self):
        self.menu_frame.pack_forget()

        self.admin_dashboard = tk.Frame(self.root)
        self.admin_dashboard.pack(fill=tk.BOTH, expand=True)

        self.add_car_btn = tk.Button(self.admin_dashboard, text="Tambah Mobil", command=self.open_add_car_window)
        self.add_car_btn.pack(pady=10)

        self.view_car_btn = tk.Button(self.admin_dashboard, text="Lihat Daftar Mobil", command=self.view_cars)
        self.view_car_btn.pack(pady=10)

        self.view_requests_btn = tk.Button(self.admin_dashboard, text="Pengajuan Peminjaman", command=self.view_rental_requests)
        self.view_requests_btn.pack(pady=10)

        self.view_customers_btn = tk.Button(self.admin_dashboard, text="Data Customer", command=self.view_customers)
        self.view_customers_btn.pack(pady=10)

        self.view_history_btn = tk.Button(self.admin_dashboard, text="Riwayat Peminjaman", command=self.view_rental_history)
        self.view_history_btn.pack(pady=10)

    def open_add_car_window(self):
        self.add_car_window = tk.Toplevel(self.root)
        self.add_car_window.title("Tambah Mobil")
        self.add_car_window.geometry("400x300")

        tk.Label(self.add_car_window, text="Brand").grid(row=0, column=0, padx=10, pady=10)
        self.entry_brand = tk.Entry(self.add_car_window)
        self.entry_brand.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.add_car_window, text="Model").grid(row=1, column=0, padx=10, pady=10)
        self.entry_model = tk.Entry(self.add_car_window)
        self.entry_model.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.add_car_window, text="Capacity").grid(row=2, column=0, padx=10, pady=10)
        self.entry_capacity = tk.Entry(self.add_car_window)
        self.entry_capacity.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.add_car_window, text="Price per Day").grid(row=3, column=0, padx=10, pady=10)
        self.entry_price_per_day = tk.Entry(self.add_car_window)
        self.entry_price_per_day.grid(row=3, column=1, padx=10, pady=10)

        self.add_car_btn = tk.Button(self.add_car_window, text="Tambah Mobil", command=self.add_car)
        self.add_car_btn.grid(row=4, column=0, columnspan=2, pady=20)

    def add_car(self):
        brand = self.entry_brand.get()
        model = self.entry_model.get()
        capacity = self.entry_capacity.get()
        price_per_day = self.entry_price_per_day.get()

        try:
            cursor = self.conn.cursor()
            query = "INSERT INTO cars (brand, model, capacity, price_per_day, status) VALUES (%s, %s, %s, %s, 'available')"
            cursor.execute(query, (brand, model, capacity, price_per_day))
            self.conn.commit()
            cursor.close()
            messagebox.showinfo("Success", "Mobil berhasil ditambahkan")
            self.add_car_window.destroy()
            self.view_cars()  # Refresh list mobil
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambahkan mobil: {e}")
            self.conn.rollback()

    def view_cars(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT car_id, brand, model, capacity, price_per_day, status FROM cars"
            cursor.execute(query)
            cars = cursor.fetchall()
            cursor.close()

            car_list_frame = tk.Frame(self.admin_dashboard)
            car_list_frame.pack(fill=tk.BOTH, expand=True)

            self.tree = ttk.Treeview(car_list_frame, columns=("ID", "Brand", "Model", "Capacity", "Price per Day", "Status"), show="headings")
            self.tree.heading("ID", text="ID")
            self.tree.heading("Brand", text="Brand")
            self.tree.heading("Model", text="Model")
            self.tree.heading("Capacity", text="Capacity")
            self.tree.heading("Price per Day", text="Price per Day")
            self.tree.heading("Status", text="Status")

            self.tree.column("ID", width=30)
            self.tree.column("Brand", width=100)
            self.tree.column("Model", width=100)
            self.tree.column("Capacity", width=80)
            self.tree.column("Price per Day", width=100)
            self.tree.column("Status", width=100)

            for car in cars:
                self.tree.insert("", "end", values=car)

            self.tree.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data mobil: {e}")


    def edit_car_window(self, event):
        selected_item = self.tree.selection()
        car_id = self.tree.item(selected_item, "values")[0]
        car_details = self.car_data_temp[int(car_id)]

        self.edit_car_win = tk.Toplevel(self.root)
        self.edit_car_win.title("Edit Mobil")
        self.edit_car_win.geometry("400x300")

        tk.Label(self.edit_car_win, text="Brand").grid(row=0, column=0, padx=10, pady=10)
        self.edit_entry_brand = tk.Entry(self.edit_car_win)
        self.edit_entry_brand.insert(0, car_details[1])
        self.edit_entry_brand.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.edit_car_win, text="Model").grid(row=1, column=0, padx=10, pady=10)
        self.edit_entry_model = tk.Entry(self.edit_car_win)
        self.edit_entry_model.insert(0, car_details[2])
        self.edit_entry_model.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.edit_car_win, text="Capacity").grid(row=2, column=0, padx=10, pady=10)
        self.edit_entry_capacity = tk.Entry(self.edit_car_win)
        self.edit_entry_capacity.insert(0, car_details[3])
        self.edit_entry_capacity.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.edit_car_win, text="Price per Day").grid(row=3, column=0, padx=10, pady=10)
        self.edit_entry_price_per_day = tk.Entry(self.edit_car_win)
        self.edit_entry_price_per_day.insert(0, car_details[4])
        self.edit_entry_price_per_day.grid(row=3, column=1, padx=10, pady=10)

        self.edit_car_btn = tk.Button(self.edit_car_win, text="Update Mobil", command=lambda: self.update_car(car_id))
        self.edit_car_btn.grid(row=4, column=0, columnspan=2, pady=20)

    def update_car(self, car_id):
        brand = self.edit_entry_brand.get()
        model = self.edit_entry_model.get()
        capacity = self.edit_entry_capacity.get()
        price_per_day = self.edit_entry_price_per_day.get()

        try:
            cursor = self.conn.cursor()
            query = "UPDATE cars SET brand=%s, model=%s, capacity=%s, price_per_day=%s WHERE car_id=%s"
            cursor.execute(query, (brand, model, capacity, price_per_day, car_id))
            self.conn.commit()
            cursor.close()
            messagebox.showinfo("Success", "Data mobil berhasil diupdate")
            self.edit_car_win.destroy()
            self.view_cars()  # Refresh list mobil
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengupdate data mobil: {e}")
            self.conn.rollback()

    def load_rental_requests(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT transaction_id, customer_id, car_id, start_date, end_date, total_price FROM transactions WHERE status='pending'"
            cursor.execute(query)
            requests = cursor.fetchall()
            cursor.close()

            for request in requests:
                self.rental_requests.append(request)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data pengajuan: {e}")

    def approve_request_window(self):
        if not self.rental_requests:
            messagebox.showinfo("Info", "Tidak ada pengajuan peminjaman yang pending")
            return

        self.deque_rental_request()

    def deque_rental_request(self):
        if not self.rental_requests:
            messagebox.showinfo("Info", "Tidak ada pengajuan peminjaman yang pending")
            return

        rental_request = self.rental_requests.popleft()
        transaction_id, customer_id, car_id, start_date, end_date, total_price = rental_request

        approve_window = tk.Toplevel(self.root)
        approve_window.title("Approve Peminjaman")
        approve_window.geometry("300x200")

        tk.Label(approve_window, text=f"Transaction ID: {transaction_id}").pack(pady=10)
        tk.Label(approve_window, text=f"Car ID: {car_id}").pack(pady=10)

        approve_btn = tk.Button(approve_window, text="Approve", command=lambda: self.approve_request(transaction_id, car_id, approve_window))
        approve_btn.pack(pady=20)
        
        reject_btn = tk.Button(approve_window, text="Reject", command=lambda: self.reject_request(transaction_id, car_id, approve_window))
        reject_btn.pack(pady=10)

    def approve_request(self, transaction_id, car_id, window):
        try:
            cursor = self.conn.cursor()
            update_transaction_query = "UPDATE transactions SET status='approved' WHERE transaction_id=%s"
            update_car_query = "UPDATE cars SET status='rented' WHERE car_id=%s"
            cursor.execute(update_transaction_query, (transaction_id,))
            cursor.execute(update_car_query, (car_id,))
            self.conn.commit()
            cursor.close()
            messagebox.showinfo("Success", "Peminjaman berhasil di-approve")
            window.destroy()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Gagal mengapprove peminjaman: {e}")

    def reject_request(self, transaction_id, car_id, window):
        try:
            cursor = self.conn.cursor()
            update_transaction_query = "UPDATE transactions SET status='rejected' WHERE transaction_id=%s"
            cursor.execute(update_transaction_query, (transaction_id,))
            self.conn.commit()
            cursor.close()
            messagebox.showinfo("Success", "Peminjaman berhasil di-reject")
            window.destroy()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Gagal mereject peminjaman: {e}")

    def view_customers(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT customer_id, full_name, email, phone, address FROM customers"
            cursor.execute(query)
            customers = cursor.fetchall()
            cursor.close()

            customer_list_frame = tk.Frame(self.admin_dashboard)
            customer_list_frame.pack(fill=tk.BOTH, expand=True)

            self.tree = ttk.Treeview(customer_list_frame, columns=("ID", "Full Name", "Email", "Phone", "Address"), show="headings")
            self.tree.heading("ID", text="ID")
            self.tree.heading("Full Name", text="Full Name")
            self.tree.heading("Email", text="Email")
            self.tree.heading("Phone", text="Phone")
            self.tree.heading("Address", text="Address")

            self.tree.column("ID", width=30)
            self.tree.column("Full Name", width=100)
            self.tree.column("Email", width=100)
            self.tree.column("Phone", width=80)
            self.tree.column("Address", width=100)

            for customer in customers:
                self.tree.insert("", "end", values=customer)

            self.tree.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data customer: {e}")

    def view_rental_history(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT customer_id, car_id, start_date, end_date, total_price, status FROM transactions WHERE status = 'ended'"
            cursor.execute(query)
            transactions = cursor.fetchall()
            cursor.close()

            history_list_frame = tk.Frame(self.admin_dashboard)
            history_list_frame.pack(fill=tk.BOTH, expand=True)

            self.tree = ttk.Treeview(history_list_frame, columns=("Customer ID", "Car ID", "Start Date", "End Date", "Total Price", "Status"), show="headings")
            self.tree.heading("Customer ID", text="Customer ID")
            self.tree.heading("Car ID", text="Car ID")
            self.tree.heading("Start Date", text="Start Date")
            self.tree.heading("End Date", text="End Date")
            self.tree.heading("Total Price", text="Total Price")
            self.tree.heading("Status", text="Status")

            self.tree.column("Customer ID", width=100)
            self.tree.column("Car ID", width=100)
            self.tree.column("Start Date", width=100)
            self.tree.column("End Date", width=100)
            self.tree.column("Total Price", width=100)
            self.tree.column("Status", width=100)

            for transaction in transactions:
                self.tree.insert("", "end", values=transaction)

            self.tree.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data riwayat peminjaman: {e}")
    
    def view_rental_requests(self):
        request_window = tk.Toplevel(self.root)
        request_window.title("Pengajuan Peminjaman")
        request_window.geometry("800x400")

        tree = ttk.Treeview(request_window, columns=("Transaction ID", "Customer ID", "Car ID", "Start Date", "End Date", "Status"), show="headings")
        tree.heading("Transaction ID", text="Transaction ID")
        tree.heading("Customer ID", text="Customer ID")
        tree.heading("Car ID", text="Car ID")
        tree.heading("Start Date", text="Start Date")
        tree.heading("End Date", text="End Date")
        tree.heading("Status", text="Status")

        tree.column("Transaction ID", width=100)
        tree.column("Customer ID", width=100)
        tree.column("Car ID", width=100)
        tree.column("Start Date", width=100)
        tree.column("End Date", width=100)
        tree.column("Status", width=100)

        try:
            cursor = self.conn.cursor()
            query = "SELECT transaction_id, customer_id, car_id, start_date, end_date, status FROM transactions WHERE status='pending'"
            cursor.execute(query)
            requests = cursor.fetchall()
            cursor.close()

            for request in requests:
                tree.insert("", "end", values=request)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data pengajuan: {e}")

        tree.pack(fill=tk.BOTH, expand=True)
        tree.bind("<Double-1>", lambda event: self.approve_request_window())

    
    def open_customer_dashboard(self):
        self.menu_frame.pack_forget()

        self.customer_dashboard = tk.Frame(self.root)
        self.customer_dashboard.pack(fill=tk.BOTH, expand=True)

        self.display_available_btn = tk.Button(self.customer_dashboard, text="Daftar Mobil Tersedia", command=self.display_available_cars)
        self.display_available_btn.pack(pady=10)
        
        self.search_car_btn = tk.Button(self.customer_dashboard, text="Cari Mobil", command=self.search_car)
        self.search_car_btn.pack(pady=10)
        
        self.sort_by_brand_btn = tk.Button(self.customer_dashboard, text="Sort by Brand", command=self.sort_by_brand)
        self.sort_by_brand_btn.pack(pady=10)

        self.request_rental_btn = tk.Button(self.customer_dashboard, text="Ajukan Peminjaman", command=self.open_request_rental_window)
        self.request_rental_btn.pack(pady=10)

        self.view_rental_status_btn = tk.Button(self.customer_dashboard, text="Lihat Status Peminjaman", command=self.view_rental_status)
        self.view_rental_status_btn.pack(pady=10)
        
        self.view_rented_cars_btn = tk.Button(self.customer_dashboard, text="Lihat Mobil yang Disewa", command=self.view_rented_cars)
        self.view_rented_cars_btn.pack(pady=10)

        self.return_car_btn = tk.Button(self.customer_dashboard, text="Kembalikan Mobil", command=self.return_car)
        self.return_car_btn.pack(pady=10)
        
        self.history_cars_btn = tk.Button(self.customer_dashboard, text="Riwayat Peminjaman", command=self.history_cars)
        self.history_cars_btn.pack(pady=10)

        self.display_available_cars()

    def display_available_cars(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT car_id, brand, model, capacity, price_per_day, status FROM cars WHERE status = 'available'"
            cursor.execute(query)
            cars = cursor.fetchall()
            cursor.close()

            car_list_frame = tk.Frame(self.customer_dashboard)
            car_list_frame.pack(fill=tk.BOTH, expand=True)

            self.tree = ttk.Treeview(car_list_frame, columns=("ID", "Brand", "Model", "Capacity", "Price per Day", "Status"), show="headings")
            self.tree.heading("ID", text="ID")
            self.tree.heading("Brand", text="Brand")
            self.tree.heading("Model", text="Model")
            self.tree.heading("Capacity", text="Capacity")
            self.tree.heading("Price per Day", text="Price per Day")
            self.tree.heading("Status", text="Status")

            self.tree.column("ID", width=30)
            self.tree.column("Brand", width=100)
            self.tree.column("Model", width=100)
            self.tree.column("Capacity", width=80)
            self.tree.column("Price per Day", width=100)
            self.tree.column("Status", width=100)

            for car in cars:
                self.tree.insert("", "end", values=car)

            self.tree.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data mobil: {e}")

    def sort_by_brand(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT car_id, brand, model, capacity, price_per_day, status FROM cars WHERE status = 'available'"
            cursor.execute(query)
            cars = cursor.fetchall()
            cursor.close()

            self.quicksort(cars, 0, len(cars) - 1)

            for i in self.tree.get_children():
                self.tree.delete(i)

            for car in cars:
                self.tree.insert("", "end", values=car)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengurutkan data mobil: {e}")

    def quicksort(self, cars, low, high):
        if low < high:
            pi = self.partition(cars, low, high)
            self.quicksort(cars, low, pi - 1)
            self.quicksort(cars, pi + 1, high)

    def partition(self, cars, low, high):
        pivot = cars[high][1]  # Pivot berdasarkan brand
        i = low - 1
        for j in range(low, high):
            if cars[j][1].lower() <= pivot.lower():
                i += 1
                cars[i], cars[j] = cars[j], cars[i]
        cars[i + 1], cars[high] = cars[high], cars[i + 1]
        return i + 1
    
    def open_request_rental_window(self):
        self.request_rental_window = tk.Toplevel(self.root)
        self.request_rental_window.title("Ajukan Peminjaman")
        self.request_rental_window.geometry("400x300")

        tk.Label(self.request_rental_window, text="ID Mobil").grid(row=0, column=0, padx=10, pady=10)
        self.entry_car_id = tk.Entry(self.request_rental_window)
        self.entry_car_id.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.request_rental_window, text="Tanggal Mulai (YYYY-MM-DD)").grid(row=1, column=0, padx=10, pady=10)
        self.entry_start_date = tk.Entry(self.request_rental_window)
        self.entry_start_date.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.request_rental_window, text="Tanggal Selesai (YYYY-MM-DD)").grid(row=2, column=0, padx=10, pady=10)
        self.entry_end_date = tk.Entry(self.request_rental_window)
        self.entry_end_date.grid(row=2, column=1, padx=10, pady=10)

        self.request_rental_btn = tk.Button(self.request_rental_window, text="Ajukan Peminjaman", command=self.request_rental)
        self.request_rental_btn.grid(row=3, column=0, columnspan=2, pady=20)

    def request_rental(self):
        car_id = self.entry_car_id.get()
        start_date = self.entry_start_date.get()
        end_date = self.entry_end_date.get()

        try:
            cursor = self.conn.cursor()

            # Ambil harga per hari mobil dari database
            cursor.execute("SELECT price_per_day FROM cars WHERE car_id = %s", (car_id,))
            price_per_day = cursor.fetchone()[0]

            # Hitung jumlah hari
            days = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days

            # Hitung total harga
            total_price = days * price_per_day

            # Masukkan data transaksi ke dalam database
            query = "INSERT INTO transactions (customer_id, car_id, start_date, end_date, status, total_price) VALUES (%s, %s, %s, %s, 'pending', %s) RETURNING transaction_id"
            cursor.execute(query, (self.customer_id, car_id, start_date, end_date, total_price))
            transaction_id = cursor.fetchone()[0]
            
            self.conn.commit()
            cursor.close()

            # Tambahkan pengajuan baru ke queue
            self.rental_requests.append((transaction_id, self.customer_id, car_id, start_date, end_date, total_price))

            messagebox.showinfo("Success", "Pengajuan peminjaman berhasil")
            self.request_rental_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengajukan peminjaman: {e}")
            self.conn.rollback()

    def view_rented_cars(self):
        if self.tree is None:
            messagebox.showerror("Error", "Tidak ada data mobil yang tersedia")
            return
        
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT c.car_id, c.brand, c.model, c.capacity, c.price_per_day, t.status
                FROM cars c
                JOIN transactions t ON c.car_id = t.car_id
                WHERE t.customer_id = %s AND t.status = 'approved'
            """
            cursor.execute(query, (self.customer_id,))
            cars = cursor.fetchall()
            cursor.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for car in cars:
                self.tree.insert("", "end", values=car)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data mobil yang disewa: {e}")

    def return_car(self):
        if self.tree is None:
            messagebox.showerror("Error", "Tidak ada data mobil yang tersedia")
            return

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Pilih mobil yang ingin dikembalikan!")
            return

        car_id = self.tree.item(selected_item, "values")[0]

        try:
            cursor = self.conn.cursor()
            update_transaction_query = "UPDATE transactions SET status='ended' WHERE car_id=%s AND customer_id=%s AND status='approved'"
            update_car_query = "UPDATE cars SET status='available' WHERE car_id=%s"
            cursor.execute(update_transaction_query, (car_id, self.customer_id))
            cursor.execute(update_car_query, (car_id,))
            self.conn.commit()
            cursor.close()
            messagebox.showinfo("Success", "Mobil berhasil dikembalikan")
            self.view_rented_cars()  # Refresh list mobil yang disewa
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Gagal mengembalikan mobil: {e}")
    
    def view_rental_status(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT customer_id, car_id, start_date, end_date, total_price, status FROM transactions WHERE status = 'pending' AND customer_id = %s"
            cursor.execute(query, (self.customer_id,))
            transactions = cursor.fetchall()
            cursor.close()

            transaction_list_frame = tk.Frame(self.customer_dashboard)
            transaction_list_frame.pack(fill=tk.BOTH, expand=True)

            self.tree = ttk.Treeview(transaction_list_frame, columns=("Customer ID", "Car ID", "Start Date", "End Date", "Total Price", "Status"), show="headings")
            self.tree.heading("Customer ID", text="Customer ID")
            self.tree.heading("Car ID", text="Car ID")
            self.tree.heading("Start Date", text="Start Date")
            self.tree.heading("End Date", text="End Date")
            self.tree.heading("Total Price", text="Total Price")
            self.tree.heading("Status", text="Status")

            self.tree.column("Customer ID", width=100)
            self.tree.column("Car ID", width=100)
            self.tree.column("Start Date", width=100)
            self.tree.column("End Date", width=100)
            self.tree.column("Total Price", width=100)
            self.tree.column("Status", width=100)

            for transaction in transactions:
                self.tree.insert("", "end", values=transaction)

            self.tree.pack(fill=tk.BOTH, expand=True)
            
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data transaksi: {e}")

    def history_cars(self):
        try:
            cursor = self.conn.cursor()
            query = "SELECT customer_id, car_id, start_date, end_date, total_price, status FROM transactions WHERE customer_id = %s"
            cursor.execute(query, (self.customer_id,))
            transactions = cursor.fetchall()
            cursor.close()

            history_list_frame = tk.Frame(self.customer_dashboard)
            history_list_frame.pack(fill=tk.BOTH, expand=True)

            self.tree = ttk.Treeview(history_list_frame, columns=("Customer ID", "Car ID", "Start Date", "End Date", "Total Price", "Status"), show="headings")
            self.tree.heading("Customer ID", text="Customer ID")
            self.tree.heading("Car ID", text="Car ID")
            self.tree.heading("Start Date", text="Start Date")
            self.tree.heading("End Date", text="End Date")
            self.tree.heading("Total Price", text="Total Price")
            self.tree.heading("Status", text="Status")

            self.tree.column("Customer ID", width=100)
            self.tree.column("Car ID", width=100)
            self.tree.column("Start Date", width=100)
            self.tree.column("End Date", width=100)
            self.tree.column("Total Price", width=100)
            self.tree.column("Status", width=100)

            for transaction in transactions:
                self.tree.insert("", "end", values=transaction)

            self.tree.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data riwayat peminjaman: {e}")
    
    def search_car(self):
        search_query = simpledialog.askstring("Cari Mobil", "Masukkan merk atau model mobil yang ingin dicari:")

        try:
            cursor = self.conn.cursor()
            query = "SELECT car_id, brand, model, capacity, price_per_day, status FROM cars WHERE brand ILIKE %s OR model ILIKE %s"
            search_keyword = f"%{search_query}%"
            cursor.execute(query, (search_keyword, search_keyword))
            cars = cursor.fetchall()
            cursor.close()

            search_result_window = tk.Toplevel(self.root)
            search_result_window.title("Hasil Pencarian Mobil")
            search_result_window.geometry("600x400")

            tree = ttk.Treeview(search_result_window, columns=("ID", "Brand", "Model", "Capacity", "Price per Day", "Status"), show="headings")
            tree.heading("ID", text="ID")
            tree.heading("Brand", text="Brand")
            tree.heading("Model", text="Model")
            tree.heading("Capacity", text="Capacity")
            tree.heading("Price per Day", text="Price per Day")
            tree.heading("Status", text="Status")

            tree.column("ID", width=30)
            tree.column("Brand", width=100)
            tree.column("Model", width=100)
            tree.column("Capacity", width=80)
            tree.column("Price per Day", width=100)
            tree.column("Status", width=100)

            for car in cars:
                tree.insert("", "end", values=car)

            tree.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal melakukan pencarian: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RentalSystem(root)
    root.mainloop()
