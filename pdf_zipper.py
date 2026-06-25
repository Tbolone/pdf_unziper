import fitz  # PyMuPDF
import os
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

class PdfMinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF ZIP Bányász")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        self.pdf_paths = []
        self.output_dir = ""

        # GUI Elemek
        tk.Label(root, text="Rejtett ZIP fájlok kinyerése PDF-ből", font=("Arial", 14, "bold")).pack(pady=10)

        # PDF választó
        self.btn_select_pdf = tk.Button(root, text="1. PDF fájl(ok) tallózása", command=self.select_pdfs, width=30)
        self.btn_select_pdf.pack(pady=5)
        
        self.lbl_pdfs = tk.Label(root, text="Nincs fájl kiválasztva.", fg="gray")
        self.lbl_pdfs.pack()

        # Mappa választó
        self.btn_select_dir = tk.Button(root, text="2. Célmappa kiválasztása", command=self.select_output_dir, width=30)
        self.btn_select_dir.pack(pady=10)
        
        self.lbl_dir = tk.Label(root, text="Nincs mappa kiválasztva.", fg="gray")
        self.lbl_dir.pack()

        # Indítás gomb
        self.btn_start = tk.Button(root, text="3. Mélyfúrás Indítása", command=self.start_mining, width=30, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.btn_start.pack(pady=20)

        # Eredmény log
        self.lbl_status = tk.Label(root, text="", font=("Arial", 10))
        self.lbl_status.pack()

    def select_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Válaszd ki a PDF fájlokat",
            filetypes=[("PDF fájlok", "*.pdf")]
        )
        if files:
            self.pdf_paths = list(files)
            self.lbl_pdfs.config(text=f"{len(self.pdf_paths)} db PDF fájl kiválasztva.", fg="black")

    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Válaszd ki a mentés helyét")
        if directory:
            self.output_dir = directory
            self.lbl_dir.config(text=self.output_dir, fg="black")

    def open_directory(self, path):
        """Megnyitja a mappát az operációs rendszer alapértelmezett fájlkezelőjében."""
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])

    def start_mining(self):
        if not self.pdf_paths:
            messagebox.showwarning("Figyelmeztetés", "Kérlek, válassz ki legalább egy PDF fájlt!")
            return
        if not self.output_dir:
            messagebox.showwarning("Figyelmeztetés", "Kérlek, válaszd ki a célmappát!")
            return

        total_found = 0
        self.lbl_status.config(text="Feldolgozás folyamatban...", fg="blue")
        self.root.update()

        for pdf_path in self.pdf_paths:
            pdf_name = os.path.basename(pdf_path)
            try:
                doc = fitz.open(pdf_path)
                hossz = doc.xref_length()
                talalat_pdfben = 0

                for xref in range(1, hossz):
                    try:
                        stream = doc.xref_stream(xref)
                        # Ellenőrizzük a ZIP magic number-t (PK\x03\x04)
                        if stream and stream.startswith(b'\x50\x4b\x03\x04'):
                            talalat_pdfben += 1
                            total_found += 1
                            
                            # Fájlnév generálása a célmappába
                            fajl_nev = f"{os.path.splitext(pdf_name)[0]}_kimentett_{talalat_pdfben}.zip"
                            teljes_utvonal = os.path.join(self.output_dir, fajl_nev)

                            with open(teljes_utvonal, "wb") as f:
                                f.write(stream)
                    except Exception:
                        continue
                doc.close()
            except Exception as e:
                print(f"Hiba a(z) {pdf_name} fájlnál: {e}")

        self.lbl_status.config(text=f"KÉSZ! Összesen {total_found} db ZIP fájl kibányászva.", fg="green")
        
        # Sikeres üzenet és mappa megnyitása
        messagebox.showinfo("Befejezve", f"A művelet befejeződött!\nÖsszesen {total_found} db fájl lett kibányászva.")
        self.open_directory(self.output_dir)

if __name__ == "__main__":
    root = tk.Tk()
    app = PdfMinerApp(root)
    root.mainloop()
