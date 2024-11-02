import cv2
import os
import pandas as pd
import numpy as np
from PIL import Image
from rembg import remove 

class SistemCerdasPCV:
    @staticmethod
    def resize_image(image, lebar=100, tinggi=100):
        lebar = int(image.shape[1] * lebar / 100)
        tinggi = int(image.shape[0] * tinggi / 100)
        dimensi = (lebar, tinggi)
        return cv2.resize(image, dimensi)

    @staticmethod
    def adjust_brightness_contrast(image, brightness=30, contrast=30):
        return cv2.convertScaleAbs(image, alpha=1 + (contrast / 100), beta=brightness)

    @staticmethod
    def ambil_rata_rgb(gambar):
        gambar_rgb = cv2.cvtColor(gambar, cv2.COLOR_BGR2RGB)  # Konversi BGR ke RGB
        rata_rgb = np.mean(gambar_rgb, axis=(0, 1))  # Rata-rata berdasarkan semua piksel
        rata_rgb = np.round(rata_rgb).astype(int)  # Pembulatan ke integer
        print("Rata-rata RGB:", rata_rgb)  # Tampilkan nilai RGB
        return rata_rgb

    @staticmethod
    def label_kematangan(rgb):
        R, G, B = rgb
        
        # Atur batasan untuk kematangan berdasarkan nilai RGB
        if R > 150 and G < 150 and B < 150:  # Merah pekat (R tinggi)
            return 'Matang'
        elif R > 120 and G > 120 and B < 130:  # Kuning ke oranye
            return 'Matang'
        else:  # Jika tidak memenuhi syarat untuk Merah Pekat, Matang, atau Setengah Matang
            return 'Matang'

    @staticmethod
    def simpan_hasil(gambar, path_output):
        cv2.imwrite(path_output, gambar)

    @staticmethod
    def hapus_bg(img, filename, output_directory):
        """Fungsi untuk menghapus background gambar dan menyimpannya ke direktori output."""
        try:
            # Menghapus latar belakang menggunakan rembg
            img_no_bg = remove(img)

            # Mengubah hasil dari NumPy array ke PIL Image
            img_no_bg_pil = Image.fromarray(cv2.cvtColor(img_no_bg, cv2.COLOR_BGR2RGB))

            # Ubah ekstensi file menjadi .png
            output_file_path = os.path.join(output_directory, f'no_bg_{os.path.splitext(filename)[0]}.png')

            # Simpan gambar hasil tanpa background dengan format PNG
            img_no_bg_pil.save(output_file_path, format='PNG')
            print(f"Gambar dengan background dihapus disimpan di {output_file_path}")

            return img_no_bg  # Mengembalikan gambar yang telah dihapus latar belakang
        except Exception as e:
            print(f"Kesalahan saat menghapus latar belakang pada {filename}: {e}")
            return img  # Kembalikan gambar asli jika terjadi kesalahan

    @staticmethod
    def proses_gambar(folder_path):
        data = {'Nama Gambar': [], 'R': [], 'G': [], 'B': [], 'label': []}
        
        for namagambar in os.listdir(folder_path):
            path_file = os.path.join(folder_path, namagambar)
            gambar_asli = cv2.imread(path_file)
            if gambar_asli is not None:
                gambar_diubah = SistemCerdasPCV.resize_image(gambar_asli)

                # Menghapus latar belakang gambar
                output_directory = "D:/New folder/Tomat.in/PCV_SistemCerdas_Tomat.In/REVISI/hasil_cropping_matang"
                os.makedirs(output_directory, exist_ok=True)  # Membuat direktori jika belum ada
                gambar_diubah = SistemCerdasPCV.hapus_bg(gambar_diubah, namagambar, output_directory)

                # Penyesuaian kecerahan dan kontras pada gambar yang diubah
                gambar_diubah = SistemCerdasPCV.adjust_brightness_contrast(gambar_diubah)

                rata_rgb = SistemCerdasPCV.ambil_rata_rgb(gambar_diubah)
                label = SistemCerdasPCV.label_kematangan(rata_rgb)

                # Menyimpan hasil ke dalam dictionary
                data['Nama Gambar'].append(namagambar)
                data['R'].append(rata_rgb[0])
                data['G'].append(rata_rgb[1])
                data['B'].append(rata_rgb[2])
                data['label'].append(label)

        # Mengonversi hasil ke DataFrame dan menyimpannya ke file Excel
        df = pd.DataFrame(data)
        output_file = 'D:/New folder/Tomat.in/PCV_SistemCerdas_Tomat.In/REVISI/hasil_cropping_matang.xlsx'
        df.to_excel(output_file, index=False)
        print("Hasil ekstraksi disimpan ke 'hasil_cropping_matang.xlsx'")

if __name__ == "__main__":
    folder_path = "D:/New folder/Tomat.in/PCV_SistemCerdas_Tomat.In/REVISI/TM_BARU"
    os.makedirs("hasil_cropping_matang", exist_ok=True)
    SistemCerdasPCV.proses_gambar(folder_path)
