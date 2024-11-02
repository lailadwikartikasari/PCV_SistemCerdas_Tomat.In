import cv2
import os
import pandas as pd
import numpy as np

class SistemCerdasPCV:
    @staticmethod
    def resize_image(image, lebar=100, tinggi=100, output_path=None):
        # Mengatur ukuran gambar yang diinginkan
        lebar_baru = int(image.shape[1] * lebar / 100)
        tinggi_baru = int(image.shape[0] * tinggi / 100)
        
        # Resize gambar
        image_resized = cv2.resize(image, (lebar_baru, tinggi_baru))
        
        # Simpan gambar hasil resize jika output_path diberikan
        if output_path is not None:
            cv2.imwrite(output_path, image_resized)
            print(f"Gambar yang diubah ukuran disimpan di: {output_path}")
        
        return image_resized

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
        if R > 150 and G < 150 and B < 150:  # Merah pekat (R tinggi)
            return 'Matang'
        elif R > 120 and G > 120 and B < 130:  # Kuning ke oranye
            return 'Setengah Matang'
        else:
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
        
        # Direktori untuk menyimpan gambar yang diresize
        output_resize_directory = "D:/New folder/Tomat.in/PCV_SistemCerdas_Tomat.In/REVISI/hasil_resize"
        os.makedirs(output_resize_directory, exist_ok=True)

        for namagambar in os.listdir(folder_path):
            path_file = os.path.join(folder_path, namagambar)
            gambar_asli = cv2.imread(path_file)
            if gambar_asli is not None:
                # Simpan gambar yang diresize
                output_resize_path = os.path.join(output_resize_directory, f'resize_{namagambar}')
                gambar_diubah = SistemCerdasPCV.resize_image(gambar_asli, output_path=output_resize_path)
                
                # Crop bagian tengah gambar
                gambar_diubah = SistemCerdasPCV.crop_tengah_tomat(gambar_diubah)

                # Penyesuaian kecerahan dan kontras
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
                output_directory = "D:/New folder/Tomat.in/PCV_SistemCerdas_Tomat.In/REVISI/hasil_cropping_matang"
                os.makedirs(output_directory, exist_ok=True)
                output_path = os.path.join(output_directory, f"hasil_{namagambar}")
                SistemCerdasPCV.simpan_hasil(gambar_diubah, output_path)

        # Simpan hasil ke Excel
        df = pd.DataFrame(data)
        output_file = 'D:/New folder/Tomat.in/PCV_SistemCerdas_Tomat.In/REVISI/hasil_cropping_matang_v2.xlsx'
        df.to_excel(output_file, index=False)
        print("Hasil ekstraksi disimpan ke 'hasil_cropping_matang.xlsx'")

if __name__ == "__main__":
    folder_path = "D:/New folder/Tomat.in/PCV_SistemCerdas_Tomat.In/REVISI/TM_BARU"
    SistemCerdasPCV.proses_gambar(folder_path)
