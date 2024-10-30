import cv2
import os
import pandas as pd
import numpy as np

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
            return 'Mentah'
        elif R > 120 and G > 120 and B < 130:  # Kuning ke oranye
            return 'Mentah'
        else:  # Jika tidak memenuhi syarat untuk Merah Pekat, Matang, atau Setengah Matang
            return 'Mentah'

    @staticmethod
    def simpan_hasil(gambar, path_output):
        cv2.imwrite(path_output, gambar)

    @staticmethod
    def crop_tengah_tomat(gambar):
        tmp = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(tmp, 127, 255, cv2.THRESH_BINARY_INV)

        mask = cv2.dilate(mask.copy(), None, iterations=5)
        mask = cv2.erode(mask.copy(), None, iterations=5)
        b, g, r = cv2.split(gambar)
        rgba = [b, g, r, mask]
        dst = cv2.merge(rgba, 4)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:  # Pastikan ada kontur
            # Ambil kontur terbesar
            c = max(contours, key=cv2.contourArea)
            # Mendapatkan bounding box dari kontur terbesar
            x, y, w, h = cv2.boundingRect(c)
            # Mengcrop gambar berdasarkan bounding box
            return gambar[y:y + h, x:x + w]
        
        return gambar  # Jika tidak ada kontur, kembalikan gambar asli

    @staticmethod
    def proses_gambar(folder_path):
        data = {'Nama Gambar': [], 'R': [], 'G': [], 'B': [], 'label': []}
        
        for namagambar in os.listdir(folder_path):
            path_file = os.path.join(folder_path, namagambar)
            gambar_asli = cv2.imread(path_file)
            if gambar_asli is not None:
                gambar_diubah = SistemCerdasPCV.resize_image(gambar_asli)
                gambar_diubah = SistemCerdasPCV.crop_tengah_tomat(gambar_diubah)

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

                # Simpan gambar hasil crop
                output_path = os.path.join("hasil_cropping_mentah", f"hasil_{namagambar}")
                SistemCerdasPCV.simpan_hasil(gambar_diubah, output_path)

        # Mengonversi hasil ke DataFrame dan menyimpannya ke file Excel
        df = pd.DataFrame(data)
        df.to_excel('hasil_ekstraksi_mentah.xlsx', index=False)
        print("Hasil ekstraksi disimpan ke 'hasil_ekstraksi.xlsx'")

if __name__ == "__main__":
    folder_path = "D:/New folder/Tomat.in/PCV_SistemCerdas_Tomat.In/Tomat Mentah"
    os.makedirs("hasil_cropping_mentah", exist_ok=True)
    SistemCerdasPCV.proses_gambar(folder_path)
