# برنامج إدارة صيدلية كامل - مبيعات + تقرير متقدم

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import ttkbootstrap as tb
from datetime import datetime

# إنشاء قاعدة البيانات
conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()

# إنشاء الجداول
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    expire_date TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    name TEXT,
    quantity INTEGER,
    unit_price REAL,
    discount REAL,
    total_price REAL,
    base_price REAL,
    final_price REAL,
    date TEXT
)''')

conn.commit()

# إضافة منتج جديد
def add_product():
    name = name_entry.get()
    company = company_entry.get()
    price = price_entry.get()
    quantity = quantity_entry.get()
    expire = expire_entry.get()

    if name == "" or price == "" or quantity == "":
        messagebox.showerror("خطأ", "من فضلك أدخل اسم المنتج والسعر والكمية")
        return

    try:
        cursor.execute("INSERT INTO products (name, company, price, quantity, expire_date) VALUES (?, ?, ?, ?, ?)",
                       (name, company, float(price), int(quantity), expire))
        conn.commit()
        clear_entries()
        load_products()
    except Exception as e:
        messagebox.showerror("خطأ", str(e))

# تحميل المنتجات
def load_products():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM products")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

# مسح الحقول
def clear_entries():
    name_entry.delete(0, tk.END)
    company_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    expire_entry.delete(0, tk.END)

# حذف منتج
def delete_product():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("خطأ", "اختر منتجًا للحذف")
        return
    item = tree.item(selected[0])
    prod_id = item['values'][0]
    cursor.execute("DELETE FROM products WHERE id=?", (prod_id,))
    conn.commit()
    load_products()

# تنفيذ البيع من الجدول مباشرة

def quick_sale(product_id):
    cursor.execute("SELECT name, price, quantity FROM products WHERE id=?", (product_id,))
    result = cursor.fetchone()
    if not result:
        messagebox.showerror("خطأ", "المنتج غير موجود")
        return

    name, base_price, stock_qty = result

    def open_quick_sale_window():
        win = tb.Toplevel(title="تنفيذ البيع")
        win.geometry("400x300")

        ttk.Label(win, text=f"المنتج: {name}", font=("Arial", 12, "bold")).pack(pady=10)

        qty_frame = ttk.Frame(win)
        qty_frame.pack(pady=5)
        ttk.Label(qty_frame, text="الكمية المطلوبة:").pack(side="left")
        qty_entry = ttk.Entry(qty_frame, width=10)
        qty_entry.pack(side="left", padx=5)
        qty_entry.insert(0, "1")

        disc_frame = ttk.Frame(win)
        disc_frame.pack(pady=5)
        ttk.Label(disc_frame, text="نسبة الخصم ٪:").pack(side="left")
        discount_entry = ttk.Entry(disc_frame, width=10)
        discount_entry.pack(side="left", padx=5)
        discount_entry.insert(0, "0")

        def confirm_sale():
            try:
                qty = int(qty_entry.get())
                discount = float(discount_entry.get())
                if qty > stock_qty:
                    messagebox.showerror("خطأ", "الكمية غير متوفرة")
                    return
                final_unit_price = base_price * (1 - discount / 100)
                total = final_unit_price * qty

                cursor.execute("INSERT INTO sales (product_id, name, quantity, unit_price, discount, total_price, base_price, final_price, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (product_id, name, qty, base_price, discount, total, base_price, final_unit_price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (qty, product_id))
                conn.commit()
                win.destroy()
                load_products()
            except Exception as e:
                messagebox.showerror("خطأ", str(e))

        ttk.Button(win, text="تأكيد البيع", command=confirm_sale).pack(pady=15)

    open_quick_sale_window()

# البحث في المنتجات


#تحديث رقم 1 خاص بكليك يمين


def edit_product(product_id):
    cursor.execute("SELECT name, company, price, quantity, expire_date FROM products WHERE id=?", (product_id,))
    result = cursor.fetchone()
    if not result:
        messagebox.showerror("خطأ", "المنتج غير موجود")
        return

    name_val, company_val, price_val, quantity_val, expire_val = result

    win = tb.Toplevel(title="تعديل المنتج")
    win.geometry("400x400")

    ttk.Label(win, text="اسم المنتج").pack(pady=5)
    name_entry = ttk.Entry(win)
    name_entry.pack()
    name_entry.insert(0, name_val)

    ttk.Label(win, text="الشركة المصنعة").pack(pady=5)
    company_entry = ttk.Entry(win)
    company_entry.pack()
    company_entry.insert(0, company_val)

    ttk.Label(win, text="السعر").pack(pady=5)
    price_entry = ttk.Entry(win)
    price_entry.pack()
    price_entry.insert(0, price_val)

    ttk.Label(win, text="الكمية").pack(pady=5)
    quantity_entry = ttk.Entry(win)
    quantity_entry.pack()
    quantity_entry.insert(0, quantity_val)

    ttk.Label(win, text="تاريخ الانتهاء").pack(pady=5)
    expire_entry = ttk.Entry(win)
    expire_entry.pack()
    expire_entry.insert(0, expire_val)

    def save_changes():
        try:
            cursor.execute("""UPDATE products
                              SET name=?,
                                  company=?,
                                  price=?,
                                  quantity=?,
                                  expire_date=?
                              WHERE id = ?""",
                           (name_entry.get(), company_entry.get(), float(price_entry.get()),
                             int(quantity_entry.get()), expire_entry.get(), product_id))
            conn.commit()
            win.destroy()
            load_products()

        except Exception as e:
            messagebox.showerror("خطأ", str(e))


# نهاية تحديث رقم 1



######


def search_products(event):
    query = search_entry.get().strip()
    for row in tree.get_children():
        tree.delete(row)

    if query == "":
        load_products()
        return

    try:
        if query.isdigit():
            cursor.execute("SELECT * FROM products WHERE id = ?", (int(query),))
        else:
            cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{query}%",))
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("خطأ", str(e))

# نافذة المبيعات المتقدمة

#تحديث 3


#تحديث رقم 3
def open_sales_report_directly():
        report_win = tb.Toplevel(title="تقرير المبيعات")
        report_win.geometry("900x500")

        columns = ("ID", "المنتج", "الكمية", "السعر الأساسي", "السعر بعد الخصم", "الخصم", "الإجمالي", "التاريخ")
        tree_sales = ttk.Treeview(report_win, columns=columns, show="headings")
        for col in columns:
            tree_sales.heading(col, text=col)
        tree_sales.pack(fill="both", expand=True)

        cursor.execute(
            "SELECT id, name, quantity, base_price, final_price, discount, total_price, date FROM sales ORDER BY id DESC LIMIT 50")
        total_sum = 0
        for row in cursor.fetchall():
            tree_sales.insert("", "end", values=row)
            total_sum += row[6]

        ttk.Label(report_win, text=f"إجمالي المبيعات: {total_sum:.2f} جنيه", font=("Arial", 12, "bold")).pack(pady=10)


#نهاية تحديث 3

def open_sales_window():
    sales_win = tb.Toplevel(title="نقطة البيع")
    sales_win.geometry("600x600")

    ttk.Label(sales_win, text="اسم المنتج").pack(pady=5)
    name_entry = ttk.Entry(sales_win)
    name_entry.pack(pady=5)

    ttk.Label(sales_win, text="الكمية").pack(pady=5)
    qty_entry = ttk.Entry(sales_win)
    qty_entry.pack(pady=5)

    ttk.Label(sales_win, text="نسبة الخصم ٪").pack(pady=5)
    discount_entry = ttk.Entry(sales_win)
    discount_entry.insert(0, "0")
    discount_entry.pack(pady=5)

    receipt = tk.Text(sales_win, height=12)
    receipt.pack(pady=10, fill="x")

    #نهاية تحديث رقم3


    def process_sale():
        name = name_entry.get().strip()
        try:
            qty = int(qty_entry.get())
            discount = float(discount_entry.get())
            cursor.execute("SELECT id, price, quantity FROM products WHERE name LIKE ?", (f"%{name}%",))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("خطأ", "المنتج غير موجود")
                return
            prod_id, base_price, stock_qty = result
            if qty > stock_qty:
                messagebox.showerror("خطأ", "الكمية غير متوفرة")
                return

            final_unit_price = base_price * (1 - discount / 100)
            total = final_unit_price * qty

            cursor.execute("INSERT INTO sales (product_id, name, quantity, unit_price, discount, total_price, base_price, final_price, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (prod_id, name, qty, base_price, discount, total, base_price, final_unit_price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (qty, prod_id))
            conn.commit()

            receipt.insert(tk.END, f"{name} x{qty} = {total:.2f} جنيه\n")
            name_entry.delete(0, tk.END)
            qty_entry.delete(0, tk.END)
            discount_entry.delete(0, tk.END)
            discount_entry.insert(0, "0")

        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def show_report():
        report_win = tb.Toplevel(title="تقرير المبيعات")
        report_win.geometry("900x500")

        columns = ("ID", "المنتج", "الكمية", "السعر الأساسي", "السعر بعد الخصم", "الخصم", "الإجمالي", "التاريخ")
        tree_sales = ttk.Treeview(report_win, columns=columns, show="headings")
        for col in columns:
            tree_sales.heading(col, text=col)
        tree_sales.pack(fill="both", expand=True)

        cursor.execute("SELECT id, name, quantity, base_price, final_price, discount, total_price, date FROM sales ORDER BY id DESC LIMIT 50")
        total_sum = 0
        for row in cursor.fetchall():
            tree_sales.insert("", "end", values=row)
            total_sum += row[6]

        ttk.Label(report_win, text=f"إجمالي المبيعات: {total_sum:.2f} جنيه", font=("Arial", 12, "bold")).pack(pady=10)

    ttk.Button(sales_win, text="تنفيذ البيع", command=process_sale).pack(pady=10)
    ttk.Button(sales_win, text="عرض تفاصيل المبيعات", command=show_report).pack()

# واجهة البرنامج الرئيسية
root = tb.Window(themename="cosmo")
root.title("نظام إدارة الصيدلية")
root.geometry("1000x600")

frame = ttk.LabelFrame(root, text="إضافة منتج")
frame.pack(padx=10, pady=10, fill="x")

labels = ["اسم المنتج", "الشركة المصنعة", "السعر", "الكمية", "تاريخ الانتهاء"]
name_entry = ttk.Entry(frame)
company_entry = ttk.Entry(frame)
price_entry = ttk.Entry(frame)
quantity_entry = ttk.Entry(frame)
expire_entry = ttk.Entry(frame)
entry_widgets = [name_entry, company_entry, price_entry, quantity_entry, expire_entry]

for i, label in enumerate(labels):
    ttk.Label(frame, text=label).grid(row=0, column=i, padx=5, pady=5)
    entry_widgets[i].grid(row=1, column=i, padx=5, pady=5)

ttk.Button(frame, text="إضافة المنتج", command=add_product).grid(row=2, column=0, columnspan=2, pady=10)

ttk.Button(frame, text="حذف المنتج", command=delete_product).grid(row=2, column=2, columnspan=2, pady=10)

ttk.Button(frame, text="الذهاب لنقطة البيع", command=open_sales_window).grid(row=2, column=4, pady=10)

#تحديث رقم3
ttk.Button(frame, text="تقارير البيع", command=open_sales_report_directly).grid(row=2, column=5, pady=10)

#نهاية تحديث رقم3

search_frame = ttk.Frame(root)
search_frame.pack(pady=5)

search_label = ttk.Label(search_frame, text="ابحث هنا:")
search_label.pack(side="left", padx=5)
search_entry = ttk.Entry(search_frame, width=40)
search_entry.pack(side="left")
search_entry.bind("<Return>", search_products)

columns = ("ID", "الاسم", "الشركة", "السعر", "الكمية", "ت. الانتهاء")
tree = ttk.Treeview(root, columns=columns, show="headings")

#تحديث رقم 2

# إنشاء القائمة المنبثقة (كليك يمين)
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="تنفيذ عملية بيع", command=lambda: quick_sale(tree.item(tree.selection()[0])['values'][0]))
menu.add_command(label="تعديل المنتج في المخزن", command=lambda: edit_product(tree.item(tree.selection()[0])['values'][0]))

def show_context_menu(event):
    selected = tree.identify_row(event.y)
    if selected:
        tree.selection_set(selected)
        menu.post(event.x_root, event.y_root)

tree.bind("<Button-3>", show_context_menu)



# نهاية تحديث رقم 2

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", stretch=True, width=150)
tree.pack(padx=10, pady=10, fill="both", expand=True)

def on_product_select(event):
    selected = tree.selection()
    if selected:
        item = tree.item(selected[0])
        prod_id = item['values'][0]
        quick_sale(prod_id)

tree.bind("<Double-1>", on_product_select)

load_products()
root.mainloop()

# نهاية البرنامج

