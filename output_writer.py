# output_writer.py

import os
from typing import Dict, List
from measurement import MeasurementData

class OutputWriter:
    """Hesaplama sonuçlarını dosyalara yazmak için sınıf."""

    def __init__(self, output_root_folder: str):
        self.output_root_folder = os.path.join(output_root_folder, "sonuc")
        os.makedirs(self.output_root_folder, exist_ok=True) # Sonuç klasörünü oluştur

    def _get_output_path(self, measurement_type: str, calculation_name: str, is_global: bool = False) -> str:
        """
        Çıktı dosyasının tam yolunu oluşturur.
        Örn: sonuc/sıcaklık/ortalamalar.txt veya sonuc/sıcaklık/global_ortalama.txt
        """
        type_folder = os.path.join(self.output_root_folder, measurement_type)
        os.makedirs(type_folder, exist_ok=True) # Fiziksel büyüklük klasörünü oluştur

        if is_global:
            filename = f"global_{calculation_name.lower().replace(' ', '')}.txt"
        else:
            filename = f"{calculation_name.lower().replace(' ', '')}lar.txt" # Çoğul isim

        return os.path.join(type_folder, filename)

    def write_results(self, 
                      results: Dict[str, Dict[str, any]], 
                      measurement_type: str, 
                      calculation_name: str, 
                      is_global: bool = False):
        """
        Hesaplama sonuçlarını ilgili dosyaya yazar.

        Args:
            results: Hesaplama sonuçlarını içeren sözlük. Formatı hesaplama türüne göre değişir.
                     Örn: {'id:1 ölçüm: sıcaklık ...': 'max: 20', ...} veya frekans için daha karmaşık.
            measurement_type: 'sıcaklık' veya 'nem'.
            calculation_name: Hesaplama stratejisinin adı (Ortalama, Maksimum vb.).
            is_global: Global bir hesaplama sonucu mu olduğu.
        """
        output_file_path = self._get_output_path(measurement_type, calculation_name, is_global)

        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                if is_global:
                    # Global sonuçlar genellikle tek bir anahtar-değer çifti içerir
                    for key, value in results.items(): # Global sonuç {'max': 21} veya {'ortalama': 15.5} gibi
                        f.write(f"{key}: {value}\n")
                elif calculation_name == "Frekans":
                    # Frekans çıktısı özel format istiyor
                    # Örnek:
                    # id:1 ölçüm: sıcaklık - yer: YER - tarih: 11.11.2011
                    # 9 Derece 8 defa ölçüldü
                    # 10 Derece 14 defa ölçüldü
                    # ---------------
                    for header_info, freq_data in results.items():
                        f.write(f"{header_info}\n")
                        for value, count in freq_data.items():
                            f.write(f"{value} Derece {count} defa ölçüldü\n")
                        f.write("---------------\n")
                else:
                    # Diğer sonuçlar (Ortalama, Maksimum, Minimum, Medyan, Standart Sapma)
                    # Örnek: id:1 ölçüm: sıcaklık - yer: YER - tarih: 11.11.2011 , max: 20
                    for header_info, value in results.items():
                        f.write(f"{header_info} , {calculation_name.lower()}: {value}\n")
            print(f"Sonuçlar başarıyla yazıldı: {output_file_path}")
            return output_file_path
        except Exception as e:
            print(f"Sonuçlar '{output_file_path}' dosyasına yazılırken hata oluştu: {e}")
            return None