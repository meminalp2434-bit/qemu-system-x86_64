import os
import sys
import zipfile
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Projenin ana çalışma dizini doğrudan senin klasör yoluna sabitlendi
Gecerli_Dizin = r"C:\Users\Emin\Desktop\0060046070038"

# SDK Çevre Değişkenlerini Sabitleme
SDK_Yolu = os.path.join(Gecerli_Dizin, "android_sdk")
os.environ["ANDROID_HOME"] = SDK_Yolu
os.environ["ANDROID_SDK_ROOT"] = SDK_Yolu
os.environ["ANDROID_AVD_HOME"] = os.path.join(Gecerli_Dizin, ".android", "avd")
os.environ["USERPROFILE"] = Gecerli_Dizin

# Taşınabilir Yerel Python Ortamı Ayarları
Lokal_Python_Klasor = os.path.join(Gecerli_Dizin, "python_ortami")
Lokal_Python_Exe = os.path.join(Lokal_Python_Klasor, "Scripts", "python.exe")

def lokal_python_ortami_kur():
    """ Yönetici izni istemeden klasörün içine bağımsız bir Python sanal ortamı (venv) kurar """
    if not os.path.exists(Lokal_Python_Exe):
        try:
            subprocess.run([sys.executable, "-m", "venv", Lokal_Python_Klasor], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run([Lokal_Python_Exe, "-m", "pip", "install", "--upgrade", "pip"], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
            messagebox.showinfo("Başarılı", "Projenize özel izole Python Ortamı başarıyla kuruldu!")
        except Exception as e:
            messagebox.showerror("Hata", f"Lokal Python ortamı oluşturulamadı: {e}")

def sdk_doldur_komutu():
    """ Windows PowerShell altyapısını kullanarak dosyayı %100 eksiksiz indirir ve ayıklar """
    if not os.path.exists(SDK_Yolu):
        os.makedirs(SDK_Yolu)
        
    url = "https://google.com"
    zip_hedef = os.path.join(Gecerli_Dizin, "tools.zip")
    
    if os.path.exists(zip_hedef):
        try: os.remove(zip_hedef)
        except: pass
        
    try:
        indirme_penceresi = tk.Toplevel(Ana_Pencere)
        indirme_penceresi.title("Sistem Dolduruluyor...")
        indirme_penceresi.geometry("340x120")
        indirme_penceresi.configure(bg="#2c3e50")
        
        tk.Label(indirme_penceresi, text="Windows motoru ile güvenli indirme başladı...\nLütfen bitene kadar bu pencereyi kapatmayın.", font=("Arial", 9), bg="#2c3e50", fg="white").pack(pady=10)
        ilerleme = ttk.Progressbar(indirme_penceresi, mode='indeterminate')
        ilerleme.pack(fill=tk.X, padx=20)
        ilerleme.start()
        indirme_penceresi.update()

        # PowerShell ile güvenli indirme
        ps_komutu = f'[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile("{url}", "{zip_hedef}")'
        subprocess.run(["powershell", "-Command", ps_komutu], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
        
        indirme_penceresi.update()
        
        if os.path.exists(zip_hedef) and zipfile.is_zipfile(zip_hedef):
            with zipfile.ZipFile(zip_hedef, 'r') as zip_ref:
                zip_ref.extractall(SDK_Yolu)
        else:
            raise Exception("İndirilen dosya bütünlüğü doğrulanamadı.")
            
        if os.path.exists(zip_hedef):
            os.remove(zip_hedef)
            
        ilerleme.stop()
        indirme_penceresi.destroy()
        
        messagebox.showinfo("Başarılı", "Android SDK araçları tamamen indirildi ve klasör dolduruldu!")
    except Exception as e:
        if 'indirme_penceresi' in locals():
            try: indirme_penceresi.destroy()
            except: pass
        messagebox.showerror("Hata", f"İşlem sırasında bir sorun oluştu:\n{e}")

def android_cli_emulator_baslat():
    """ Android emülatörünü CLI/KSA üzerinden izinsiz tetikler """
    sdk_bin = os.path.join(SDK_Yolu, "cmdline-tools", "bin", "avdmanager.bat")
    emulator_bin = os.path.join(SDK_Yolu, "emulator", "emulator.exe")

    if not os.path.exists(emulator_bin):
        cevap = messagebox.askyesno("Altyapı Eksik", "Android SDK araçları bulunamadı. Otomatik doldurulsun mu?")
        if cevap:
            sdk_doldur_komutu()
        return

    try:
        avd_kontrol = subprocess.run([emulator_bin, "-list-avds"], stdout=subprocess.PIPE, text=True, shell=False)
        
        if "EminCihaz" not in avd_kontrol.stdout:
            olusturma_komutu = f'echo n | "{sdk_bin}" --sdk_root="{SDK_Yolu}" create avd -n EminCihaz -k "system-images;android-25;google_apis;x86"'
            subprocess.run(olusturma_komutu, shell=True)

        emulator_komut = [
            emulator_bin, 
            "-avd", "EminCihaz", 
            "-no-snapshot-load", 
            "-gpu", "swiftshader_indirect", 
            "-qemu", "-m", "2048"
        ]
        subprocess.Popen(emulator_komut, shell=False)
        messagebox.showinfo("Başarılı", "Android CLI Emülatörü başarıyla tetiklendi!")
    except Exception as e:
        messagebox.showerror("Hata", f"Emülatör başlatılamadı: {e}")

def pc_vm_baslat():
    """ Konsol/Monitor hattı açık ve Windows 7/XP uyumlu sanal makine başlatıcı """
    sistemler_klasoru = os.path.join(Gecerli_Dizin, "sistemler")
    if not os.path.exists(sistemler_klasoru):
        os.makedirs(sistemler_klasoru)

    qemu_bin = os.path.join(Gecerli_Dizin, "qemu", "qemu-system-x86_64.exe")
    if not os.path.exists(qemu_bin):
        messagebox.showerror("Hata", "Taşınabilir QEMU motoru bulunamadı!")
        return

    disk_yolu = os.path.join(sistemler_klasoru, "sanal_disk.img")
    
    if not os.path.exists(disk_yolu):
        qemu_img_bin = os.path.join(Gecerli_Dizin, "qemu", "qemu-img.exe")
        if os.path.exists(qemu_img_bin):
            subprocess.run([qemu_img_bin, "create", "-f", "raw", disk_yolu, "20G"], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)

    # Kararlı Windows 7 / XP donanım parametreleri
    komut = [
        qemu_bin, 
        "-m", "2G", 
        "-smp", "2,sockets=1,cores=2,threads=1", 
        "-cpu", "kvm64", 
        "-vga", "std", 
        "-device", "usb-ehci", 
        "-device", "usb-tablet", 
        "-net", "nic,model=rtl8139", 
        "-net", "user",
        "-rtc", "base=localtime",
        "-monitor", "stdio", # 🛠️ KISAYOL ENGELİNİ BYPASS EDER: Konsolu doğrudan arka plandaki terminale bağlar
        "-drive", f"file={disk_yolu},media=disk,format=raw"
    ]
    
    iso_yolu = os.path.join(sistemler_klasoru, "isletim_sistemi.iso")
    
    if os.path.exists(iso_yolu):
        komut.extend(["-drive", f"file={iso_yolu},media=cdrom,format=raw", "-boot", "d"])
        messagebox.showinfo("Başarılı", "Kurulum Medyası bağlandı. Canlı konsol komutları için arkadaki siyah terminali kullanabilirsiniz.")
    else:
        komut.extend(["-boot", "c"])
        messagebox.showinfo("Başarılı", "Kurulu Windows doğrudan sabit diskten başlatılıyor!")

    # ⚠️ ÖNEMLİ: Konsolu (stdio) görebilmemiz için bu sefer PyInstaller derlemesinde arkadaki siyah ekranı kapatmamalıyız!
    subprocess.Popen(komut, shell=False)


    # Windows 11 donanım optimizasyonları ve USB fare entegrasyonu
    komut = [
        qemu_bin, 
        "-m", "4G",                      # Windows 11 için 4 GB RAM
        "-smp", "4,cores=2,threads=2",   # 4 Sanal Çekirdek
        "-cpu", "max",                   # İşlemcinin tüm gücünü aktarır
        "-vga", "virtio",                # Grafik donmasını önler
        "-device", "usb-ehci",           # Fare kilitlenmesini çözen USB kontrolcü
        "-device", "usb-tablet",         # Akıcı fare entegrasyonu
        "-net", "nic,model=e1000", 
        "-net", "user",
        "-rtc", "base=localtime"
    ]
    
    iso_yolu = os.path.join(sistemler_klasoru, "isletim_sistemi.iso")
    
    if os.path.exists(iso_yolu):
        # 🛠️ FORMAT VE BOOT DÜZELTMESİ: format=raw ekleyerek QEMU imaj hatasını çözüyoruz
        komut.extend(["-drive", f"file={iso_yolu},media=cdrom,format=raw", "-boot", "d"])
        subprocess.Popen(komut, shell=False)
        messagebox.showinfo("Başarılı", "Windows 11 Sanal Makinesi imaj format korumaları aşılarak başlatıldı!")
    else:
        messagebox.showwarning(
            "ISO Bulunamadı", 
            f"Lütfen indirdiğiniz Windows 11 ISO dosyasının adını tam olarak 'isletim_sistemi.iso' yapın ve şu klasörün içine koyun:\n\n{sistemler_klasoru}"
        )

# --- DOĞRUDAN BAŞLAYAN MASAÜSTÜ GUI ARAYÜZÜ ---
Ana_Pencere = tk.Tk()
Ana_Pencere.title("Proje: 0060046070038")
Ana_Pencere.geometry("500x450")
Ana_Pencere.configure(bg="#2c3e50")

baslik = tk.Label(Ana_Pencere, text="0060046070038 ALET ÇANTASI", font=("Arial", 16, "bold"), bg="#2c3e50", fg="#ecf0f1")
baslik.pack(pady=15)

btn_python = tk.Button(Ana_Pencere, text="🐍 LOKAL PORTABLE PYTHON ORTAMI KUR 🐍", font=("Arial", 10, "bold"), bg="#9b59b6", fg="white", width=40, height=2, command=lokal_python_ortami_kur)
btn_python.pack(pady=10)

btn_doldur = tk.Button(Ana_Pencere, text="⚙️ TEK TIKLA ANDROID ALTYAPISINI DOLDUR ⚙️", font=("Arial", 10, "bold"), bg="#e67e22", fg="white", width=40, height=2, command=sdk_doldur_komutu)
btn_doldur.pack(pady=10)

btn_pc = tk.Button(Ana_Pencere, text="1 - Bilgisayar VM Başlat (x86_64)", font=("Arial", 11, "bold"), bg="#2980b9", fg="white", width=35, height=2, command=pc_vm_baslat)
btn_pc.pack(pady=10)

btn_mobil = tk.Button(Ana_Pencere, text="2 - Android CLI Emülatör Başlat (KSA)", font=("Arial", 11, "bold"), bg="#27ae60", fg="white", width=35, height=2, command=android_cli_emulator_baslat)
btn_mobil.pack(pady=10)

# İlk açılışta venv kontrolü
Ana_Pencere.after(100, lokal_python_ortami_kur)

Ana_Pencere.mainloop()
