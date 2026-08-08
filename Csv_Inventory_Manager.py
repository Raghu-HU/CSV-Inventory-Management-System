import csv
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class CSVInventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Inventory Management System")
        self.root.geometry("1100x650")

        self.csv_file = None
        self.headers = ["ProductID","ProductName","Category","Quantity","Price","Supplier"]
        self.rows = []

        self.vars = {h: tk.StringVar() for h in self.headers}

        self.create_menu()
        self.create_form()
        self.create_table()
        self.create_status()
        self.refresh_status()

    def create_menu(self):
        m = tk.Menu(self.root)
        fm = tk.Menu(m, tearoff=0)
        fm.add_command(label="New", command=self.new_file)
        fm.add_command(label="Open CSV", command=self.open_csv)
        fm.add_command(label="Save", command=self.save_csv)
        fm.add_command(label="Save As", command=self.save_as)
        fm.add_separator()
        fm.add_command(label="Exit", command=self.root.quit)
        m.add_cascade(label="File", menu=fm)
        self.root.config(menu=m)

    def create_form(self):
        f = ttk.Frame(self.root,padding=10)
        f.pack(fill="x")
        for i,h in enumerate(self.headers):
            ttk.Label(f,text=h).grid(row=i,column=0,sticky="w",pady=3)
            ttk.Entry(f,textvariable=self.vars[h],width=35).grid(row=i,column=1,sticky="w")
        b = ttk.Frame(f)
        b.grid(row=0,column=2,rowspan=6,padx=20)
        for txt,cmd in [("Add",self.add),("Update",self.update),
                        ("Delete",self.delete),("Clear",self.clear)]:
            ttk.Button(b,text=txt,command=cmd,width=15).pack(pady=4)
        s=ttk.Frame(self.root,padding=(10,0))
        s.pack(fill="x")
        self.search_var=tk.StringVar()
        ttk.Entry(s,textvariable=self.search_var,width=40).pack(side="left")
        ttk.Button(s,text="Search",command=self.search).pack(side="left",padx=5)
        ttk.Button(s,text="Show All",command=self.load_tree).pack(side="left")

    def create_table(self):
        cols=self.headers
        self.tree=ttk.Treeview(self.root,columns=cols,show="headings")
        for c in cols:
            self.tree.heading(c,text=c)
            self.tree.column(c,width=150)
        self.tree.pack(fill="both",expand=True,padx=10,pady=10)
        self.tree.bind("<<TreeviewSelect>>",self.select)

    def create_status(self):
        self.status=ttk.Label(self.root)
        self.status.pack(fill="x",padx=10,pady=5)

    def refresh_status(self):
        total=len(self.rows)
        value=0
        low=0
        for r in self.rows:
            try:
                q=float(r[3]); p=float(r[4])
                value += q*p
                if q<5: low+=1
            except: pass
        self.status.config(text=f"Products: {total}   Inventory Value: ${value:,.2f}   Low Stock: {low}   File: {self.csv_file or 'Unsaved'}")

    def new_file(self):
        self.rows=[]; self.csv_file=None
        self.load_tree(); self.clear()

    def open_csv(self):
        path=filedialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if not path: return
        with open(path,newline='',encoding="utf-8") as f:
            data=list(csv.reader(f))
        if not data:
            messagebox.showerror("Error","Empty CSV."); return
        self.headers=data[0]
        self.rows=data[1:]
        self.csv_file=path
        self.load_tree()

    def save_csv(self):
        if not self.csv_file:
            return self.save_as()
        with open(self.csv_file,"w",newline='',encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(self.headers)
            w.writerows(self.rows)
        messagebox.showinfo("Saved","CSV saved successfully.")

    def save_as(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV Files","*.csv")])
        if not path: return
        self.csv_file=path
        self.save_csv()

    def load_tree(self,rows=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in (rows if rows is not None else self.rows):
            self.tree.insert("",tk.END,values=r)
        self.refresh_status()

    def clear(self):
        for v in self.vars.values(): v.set("")

    def get_form(self):
        return [self.vars[h].get() for h in self.headers]

    def add(self):
        self.rows.append(self.get_form())
        self.load_tree()
        self.clear()

    def update(self):
        sel=self.tree.selection()
        if not sel: return
        idx=self.tree.index(sel[0])
        self.rows[idx]=self.get_form()
        self.load_tree()

    def delete(self):
        sel=self.tree.selection()
        if not sel: return
        idx=self.tree.index(sel[0])
        del self.rows[idx]
        self.load_tree()
        self.clear()

    def select(self,e):
        sel=self.tree.selection()
        if not sel: return
        vals=self.tree.item(sel[0])["values"]
        for h,v in zip(self.headers,vals):
            self.vars[h].set(v)

    def search(self):
        term=self.search_var.get().lower()
        filt=[r for r in self.rows if any(term in str(c).lower() for c in r)]
        self.load_tree(filt)

root=tk.Tk()
CSVInventoryManager(root)
root.mainloop()