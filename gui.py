import tkinter as tk
import os


root=tk.Tk()
root.geometry("700x100")

filename_var = tk.StringVar()
url_var = tk.StringVar()


def download():
    filename = filename_var.get()
    url = url_var.get()
    os.system(f"python dl_hls.py '{filename}' '{url}'")
    filename_var.set("")
    url_var.set("")


filename_label = tk.Label(root, text = 'Filename', font=('calibre', 10, 'bold'))
filename_entry = tk.Entry(root, textvariable = filename_var, font=('calibre', 10, 'normal'), width=70)

url_label = tk.Label(root, text = 'URL', font=('calibre', 10, 'bold'))
url_entry = tk.Entry(root, textvariable = url_var, font=('calibre', 10, 'normal'), width=70)

dl_btn = tk.Button(root, text = 'Download', command = download)

filename_label.grid(row=0, column=0)
filename_entry.grid(row=0, column=1)
url_label.grid(row=1, column=0)
url_entry.grid(row=1, column=1)
root.grid_columnconfigure(0, weight=1)

dl_btn.place(relx=0.55, rely=1.0, anchor=tk.SE)

root.mainloop()