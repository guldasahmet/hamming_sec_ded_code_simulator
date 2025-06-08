# main.py

import tkinter as tk
from tkinter import messagebox, ttk
from memory import Memory
from hamming import detect_and_correct, inject_error, get_parity_bit_count
from utils import is_valid_binary_string, format_hamming_code

mem = Memory()

# --- Profesyonel Dark Mode Renk Paleti ---
# Inspired by Atom One Dark / VS Code Dark themes
DARK_MODE_BG = '#282c34'            # Ana arka plan (koyu gri)
DARK_MODE_FG = '#abb2bf'            # Genel yazı rengi (açık gri)
DARK_MODE_INPUT_BG = '#3a3f4a'      # Giriş kutuları arka planı (biraz daha koyu gri)
DARK_MODE_HIGHLIGHT = '#61afef'     # Vurgu/aktif durum rengi (mavi)
DARK_MODE_BUTTON_BG = '#3e4451'     # Buton arka planı (orta koyu gri)
DARK_MODE_BUTTON_FG = '#c678dd'     # Buton yazı rengi (mor)
DARK_MODE_FRAME_BG = '#333842'      # Çerçeve arka planı (orta koyu gri)
DARK_MODE_TEXT_BG = '#21252b'       # Metin kutusu arka planı (çok koyu gri)
DARK_MODE_BORDER = '#4b5263'        # Kenarlık rengi (hafif daha açık gri)

# --- Fonksiyonlar ---
def write_to_memory():
    data = data_entry.get().strip()
    address = address_entry.get().strip()

    supported_lengths = [8, 16, 32]
    if not is_valid_binary_string(data, supported_lengths):
        messagebox.showerror("Geçersiz Veri", f"Veri {supported_lengths} bitlik olmalı ve sadece '0' ve '1' içermelidir.")
        update_status("Hata: Geçersiz veri formatı.", "red")
        return

    try:
        addr = int(address, 16)
        encoded_code = mem.write(addr, data)
        update_output(f"Belleğe yazıldı:\n{format_hamming_code(encoded_code)}\n\n"
                      f"Yazılan Orijinal Veri Uzunluğu: {len(data)} bit\n"
                      f"Oluşan Hamming Kodu Uzunluğu: {len(encoded_code)} bit")
        update_status("Veri başarıyla belleğe yazıldı.", "green")
    except ValueError as ve:
        messagebox.showerror("Giriş Hatası", f"Adres geçerli bir heksadesimal sayı değil veya {ve}")
        update_status("Hata: " + str(ve), "red")
    except Exception as e:
        messagebox.showerror("Hata", f"Yazma işlemi sırasında bir hata oluştu: {e}")
        update_status("Hata: " + str(e), "red")

def inject_error_gui():
    address = address_entry.get().strip()
    bit_pos = error_bit_entry.get().strip()

    try:
        addr = int(address, 16)
        
        stored_code = mem.read(addr)
        if stored_code is None:
            messagebox.showerror("Adres Hatası", "Bu adreste veri bulunamadı. Lütfen önce veri yazın.")
            update_status("Hata: Bellek adresi boş.", "red")
            return

        current_code_length = len(stored_code)
        
        pos = int(bit_pos)
        if not (1 <= pos <= current_code_length):
            messagebox.showerror("Geçersiz Bit Pozisyonu", f"Hata pozisyonu {current_code_length} bitlik kod için 1 ile {current_code_length} arasında olmalıdır.")
            update_status("Hata: Geçersiz bit pozisyonu.", "red")
            return

        corrupted_code = mem.inject_error(addr, pos)
        update_output(f"Hata Enjekte Edildi (Pozisyon {pos}):\n{format_hamming_code(corrupted_code)}")
        update_status(f"Hata pozisyon {pos}'a başarıyla enjekte edildi.", DARK_MODE_HIGHLIGHT)
    except ValueError as ve:
        messagebox.showerror("Giriş Hatası", f"Adres veya bit pozisyonu geçersiz: {ve}")
        update_status("Hata: " + str(ve), "red")
    except Exception as e:
        messagebox.showerror("Hata", f"Hata enjekte etme sırasında bir sorun oluştu: {e}")
        update_status("Hata: " + str(e), "red")

def read_and_correct():
    address = address_entry.get().strip()

    try:
        addr = int(address, 16)
        raw_code = mem.read(addr)
        if raw_code is None:
            messagebox.showerror("Adres Hatası", "Bu adreste veri bulunamadı.")
            update_status("Hata: Bellek adresi boş.", "red")
            return

        corrected_code, syndrome, status = detect_and_correct(raw_code)
        
        output_str = (
            f"Okunan Kod (Hamming):\n{format_hamming_code(raw_code)}\n\n"
            f"Durum: {status}\n"
        )
        
        if "Single Bit Error" in status:
            output_str += f"\nDüzeltilmiş Kod:\n{format_hamming_code(corrected_code)}\n"
            update_status(f"{status} ve düzeltildi.", "green")
        elif "Double Bit Error" in status:
            output_str += "\nÇift bit hatası tespit edildi, düzeltilemiyor."
            update_status(f"{status}", "red")
        else: # No Error
            output_str += "\nDüzeltilmiş Kod (Hata yoktu):\n"
            output_str += format_hamming_code(corrected_code) + "\n"
            update_status("Hata yok.", "green")

        update_output(output_str)

    except ValueError as ve:
        messagebox.showerror("Giriş Hatası", f"Adres geçersiz: {ve}")
        update_status("Hata: " + str(ve), "red")
    except Exception as e:
        messagebox.showerror("Hata", f"Okuma/Düzeltme sırasında bir sorun oluştu: {e}")
        update_status("Hata: " + str(e), "red")

# --- GUI Güncelleme Yardımcı Fonksiyonları ---
def update_output(text):
    output_text_widget.config(state=tk.NORMAL)
    output_text_widget.delete(1.0, tk.END)
    output_text_widget.insert(tk.END, text)
    output_text_widget.config(state=tk.DISABLED)

def update_status(message, color="white"):
    status_label.config(text=message, foreground=color)

# === GUI Kurulumu ===
root = tk.Tk()
root.title("Hamming SEC-DED Simülatörü")
root.geometry("680x500") # Pencere boyutunu büyüttük
root.resizable(False, False)

# Temalar ve Profesyonel Dark Mode Stili
style = ttk.Style()
style.theme_use('clam') # 'clam' teması dark mode için iyi bir başlangıç noktasıdır.

# Genel pencere ve varsayılan widget'lar için palet ayarı
root.tk_setPalette(background=DARK_MODE_BG, foreground=DARK_MODE_FG)

# TFrame (genel çerçeveler)
style.configure('TFrame', background=DARK_MODE_FRAME_BG)

# TLabelFrame (etiketli çerçeveler: Giriş Bilgileri, Çıktı)
style.configure('TLabelFrame', 
                background=DARK_MODE_FRAME_BG, 
                foreground=DARK_MODE_FG, 
                font=('Helvetica', 11, 'bold'),
                relief='solid',         # Düz kenarlık
                borderwidth=1,          # Kenarlık kalınlığı
                highlightbackground=DARK_MODE_BORDER) # Pencere kenarlığı rengi

# TLabel (metin etiketleri)
style.configure('TLabel', 
                background=DARK_MODE_FRAME_BG, # Label'ların arkaplanını bağlı oldukları çerçevenin rengiyle eşleştir
                foreground=DARK_MODE_FG,
                font=('Helvetica', 10))

# TButton (butonlar)
style.configure('TButton', 
                font=('Helvetica', 10, 'bold'), 
                padding=8, # Daha fazla dolgu
                background=DARK_MODE_BUTTON_BG, 
                foreground=DARK_MODE_BUTTON_FG,
                relief='flat',         # Düz butonlar
                borderwidth=0)         # Kenarlık yok
style.map('TButton', 
          background=[('active', DARK_MODE_HIGHLIGHT)], # Üzerine gelince mavi vurgu
          foreground=[('active', 'white')]) # Üzerine gelince yazı rengi beyaz

# TEntry (giriş kutuları)
style.configure('TEntry', 
                font=('Consolas', 10), # Monospace font daha iyi okunur
                fieldbackground=DARK_MODE_INPUT_BG, 
                foreground=DARK_MODE_FG, 
                insertbackground=DARK_MODE_FG, # İmleç rengi
                relief='flat',         # Düz görünüm
                borderwidth=1,         # Kenarlık kalınlığı
                # highlightbackground=DARK_MODE_BORDER, # Bu satır bazen sorun çıkarabilir, yorumda bıraktım
                # highlightthickness=1 # Bu satır bazen sorun çıkarabilir, yorumda bıraktım
                )

# Ana çerçeve
main_frame = ttk.Frame(root, padding="20 20 20 20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Giriş Çerçevesi
input_frame = ttk.LabelFrame(main_frame, text="Giriş Bilgileri", padding="15 15 15 15")
input_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky="ew") # Daha fazla boşluk
input_frame.columnconfigure(1, weight=1) # Giriş kutusunun genişlemesini sağlar

ttk.Label(input_frame, text="Veri (8, 16 veya 32 bit ikilik):").grid(row=0, column=0, sticky="w", padx=10, pady=8) # Daha fazla boşluk
data_entry = ttk.Entry(input_frame, width=40)
data_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

ttk.Label(input_frame, text="Adres (Hex):").grid(row=1, column=0, sticky="w", padx=10, pady=8)
address_entry = ttk.Entry(input_frame, width=40)
address_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

ttk.Label(input_frame, text="Hata Enjekte Edilecek Bit Pozisyonu (1-tabanlı):").grid(row=2, column=0, sticky="w", padx=10, pady=8)
error_bit_entry = ttk.Entry(input_frame, width=40)
error_bit_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

# Buton Çerçevesi
button_frame = ttk.Frame(main_frame, padding="10 0 10 10")
button_frame.grid(row=1, column=0, columnspan=2, pady=10) # Daha fazla boşluk

ttk.Button(button_frame, text="Belleğe Yaz", command=write_to_memory).pack(side=tk.LEFT, padx=10, pady=5) # Daha fazla boşluk
ttk.Button(button_frame, text="Hata Enjekte Et", command=inject_error_gui).pack(side=tk.LEFT, padx=10, pady=5)
ttk.Button(button_frame, text="Oku ve Düzelt", command=read_and_correct).pack(side=tk.LEFT, padx=10, pady=5)

# Çıktı Çerçevesi
output_frame = ttk.LabelFrame(main_frame, text="Çıktı", padding="15 15 15 15")
output_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=15, sticky="nsew") # Daha fazla boşluk
main_frame.grid_rowconfigure(2, weight=1) # Çıktı çerçevesi dikeyde genişlesin

# tk.Text widget'ı için özel ayarlar (ttk'nın Text widget'ı yok)
output_text_widget = tk.Text(output_frame, wrap=tk.WORD, height=10, width=60, 
                             font=('Consolas', 10), state=tk.DISABLED, 
                             bg=DARK_MODE_TEXT_BG, fg=DARK_MODE_FG, 
                             insertbackground=DARK_MODE_FG, # İmleç rengi
                             relief='flat',                # Düz görünüm
                             borderwidth=1,                # Kenarlık kalınlığı
                             highlightbackground=DARK_MODE_BORDER, # Vurgulu kenarlık rengi
                             highlightthickness=1)         # Vurgulu kenarlık kalınlığı
output_text_widget.pack(fill=tk.BOTH, expand=True)

# Durum Çubuğu
status_label = ttk.Label(root, text="Hazır", anchor="w", 
                         font=('Helvetica', 9, 'italic'), 
                         background=DARK_MODE_BG, 
                         foreground='#6a9955', # Durum mesajları için hafif yeşil ton
                         padding="5 0 0 5")
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Uygulama döngüsünü başlat
root.mainloop()