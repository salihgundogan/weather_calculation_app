# data_parser.py

import os
import re
import datetime
from typing import List, Optional, Dict
from measurement import MeasurementData, MeasurementPoint

class MeasurementParser:
    """Ölçüm dosyalarını okumak ve ayrıştırmak için sınıf."""

    def parse_file(self, file_path: str) -> Optional[MeasurementData]:
        """Verilen dosya yolundan ölçüm verilerini ayrıştırır."""
        print(f"DEBUG: 'parse_file' çağrıldı: {file_path}") # Debug çıktısı
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if not lines:
                print(f"DEBUG: '{file_path}' dosyası boş.") # Debug çıktısı
                return None

            # İlk satırı başlık bilgisi olarak ayrıştır
            header_line = lines[0].strip()
            print(f"DEBUG: Başlık satırı: '{header_line}'") # Debug çıktısı
            header_info = self._parse_header(header_line)
            if not header_info:
                print(f"DEBUG: Başlık bilgisi ayrıştırılamadı: '{header_line}'") # Debug çıktısı
                return None
            print(f"DEBUG: Başlık bilgisi: {header_info}") # Debug çıktısı

            # Diğer satırları ölçüm noktaları olarak ayrıştır
            points = []
            for i, line in enumerate(lines[1:]):
                point = self._parse_measurement_point(line.strip())
                if point:
                    points.append(point)
                else:
                    print(f"DEBUG: Ölçüm noktası ayrıştırılamadı: Satır {i+2}: '{line.strip()}'") # Debug çıktısı

            if not points:
                print(f"DEBUG: '{file_path}' dosyasında geçerli ölçüm noktası bulunamadı.") # Debug çıktısı
                return None

            return MeasurementData(
                id=header_info['id'],
                measurement_type=header_info['measurement_type'],
                location=header_info['location'],
                date=header_info['date'],
                points=points
            )
        except Exception as e:
            print(f"HATA: Dosya '{file_path}' okunurken hata oluştu: {e}") # Debug çıktısı
            return None

    def _parse_header(self, header_line: str) -> Optional[Dict[str, any]]:
        """Başlık satırını ayrıştırır ve bir sözlük döndürür."""
        # Örnek: id:1 ölçüm: sıcaklık - yer: YER - tarih: 11.11.2011
        # Burada 'sıcaklık' ve 'nem' kelimelerindeki Türkçe karakterlerin Regex'te doğru eşleştiğinden emin olmalıyız.
        # Python'ın re modülü genellikle UTF-8 ile iyi çalışır, ancak yine de dikkat etmekte fayda var.
        match = re.match(r"id:(\d+) ölçüm: (.+?) - yer: (.+?) - tarih: (\d{2}\.\d{2}\.\d{4})", header_line)
        if match:
            try:
                date_obj = datetime.datetime.strptime(match.group(4), '%d.%m.%Y').date()
                # Ölçüm tipi de düzgünce alınmalı
                measurement_type_str = match.group(2).strip()
                if measurement_type_str not in ['sıcaklık', 'nem']:
                    print(f"HATA: Geçersiz ölçüm tipi '{measurement_type_str}' bulundu.")
                    return None

                return {
                    'id': match.group(1),
                    'measurement_type': measurement_type_str,
                    'location': match.group(3).strip(),
                    'date': date_obj
                }
            except ValueError as e:
                print(f"HATA: Tarih ayrıştırma hatası: {e} in '{header_line}'") # Debug çıktısı
                return None
        print(f"DEBUG: Başlık satırı Regex ile eşleşmedi: '{header_line}'") # Debug çıktısı
        return None

    def _parse_measurement_point(self, line: str) -> Optional[MeasurementPoint]:
        """Ölçüm noktası satırını ayrıştırır (örn: 08:00:00,12)."""
        parts = line.split(',')
        if len(parts) == 2:
            try:
                time_obj = datetime.datetime.strptime(parts[0].strip(), '%H:%M:%S').time()
                value = float(parts[1].strip())
                return MeasurementPoint(time=time_obj, value=value)
            except ValueError as e:
                print(f"HATA: Ölçüm noktası ayrıştırma hatası: {e} in '{line}'") # Debug çıktısı
                return None
        print(f"DEBUG: Ölçüm noktası formatı geçersiz: '{line}'") # Debug çıktısı
        return None

    def get_all_measurements_in_folder(self, root_folder: str) -> Dict[str, List[MeasurementData]]:
        """
        Kök klasördeki tüm sıcaklık ve nem ölçüm dosyalarını okur.
        Dönüş değeri: {'sıcaklık': [MeasurementData, ...], 'nem': [MeasurementData, ...]}
        """
        print(f"DEBUG: 'get_all_measurements_in_folder' çağrıldı, kök klasör: {root_folder}") # Debug çıktısı
        all_measurements = {'sıcaklık': [], 'nem': []}

        temp_folder = os.path.join(root_folder, 'sıcaklık')
        humidity_folder = os.path.join(root_folder, 'nem')

        if os.path.isdir(temp_folder):
            print(f"DEBUG: Sıcaklık klasörü bulundu: {temp_folder}") # Debug çıktısı
            for filename in os.listdir(temp_folder):
                print(f"DEBUG: Sıcaklık klasöründe dosya: {filename}") # Debug çıktısı
                if filename.endswith('.txt'):
                    file_path = os.path.join(temp_folder, filename)
                    data = self.parse_file(file_path)
                    if data and data.measurement_type == 'sıcaklık':
                        all_measurements['sıcaklık'].append(data)
                        print(f"DEBUG: Sıcaklık dosyası okundu: {filename}")
                    else:
                        print(f"UYARI: Sıcaklık klasöründe geçersiz dosya veya tür: {filename}") # Debug çıktısı
                else:
                    print(f"UYARI: Sıcaklık klasöründe .txt uzantılı olmayan dosya atlandı: {filename}") # Debug çıktısı

        else:
            print(f"UYARI: Sıcaklık klasörü bulunamadı: {temp_folder}") # Debug çıktısı

        if os.path.isdir(humidity_folder):
            print(f"DEBUG: Nem klasörü bulundu: {humidity_folder}") # Debug çıktısı
            for filename in os.listdir(humidity_folder):
                print(f"DEBUG: Nem klasöründe dosya: {filename}") # Debug çıktısı
                if filename.endswith('.txt'):
                    file_path = os.path.join(humidity_folder, filename)
                    data = self.parse_file(file_path)
                    if data and data.measurement_type == 'nem':
                        all_measurements['nem'].append(data)
                        print(f"DEBUG: Nem dosyası okundu: {filename}")
                    else:
                        print(f"UYARI: Nem klasöründe geçersiz dosya veya tür: {filename}") # Debug çıktısı
                else:
                    print(f"UYARI: Nem klasöründe .txt uzantılı olmayan dosya atlandı: {filename}") # Debug çıktısı
        else:
            print(f"UYARI: Nem klasörü bulunamadı: {humidity_folder}") # Debug çıktısı

        return all_measurements