# main.py

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLineEdit, QCheckBox, QLabel,
                            QMessageBox, QFileDialog, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal

# Kendi modüllerimizi import et
from data_parser import MeasurementParser
from calculation_strategies import (ICalculationStrategy, AverageCalculationStrategy,
                                    MaximumCalculationStrategy, MinimumCalculationStrategy,
                                    StandardDeviationCalculationStrategy, FrequencyCalculationStrategy,
                                    MedianCalculationStrategy)
from output_writer import OutputWriter
from measurement import MeasurementData # MeasurementData tipini kullanabilmek için

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.measurement_parser = MeasurementParser()
        self.output_writer = None # Klasör seçildikten sonra başlatılacak
        self.all_measurements_by_type = {'sıcaklık': [], 'nem': []} # Okunan tüm ölçüm verileri

        # Strateji nesnelerini bir sözlükte tutalım
        self.calculation_strategies = {
            'Ortalama': AverageCalculationStrategy(),
            'Maksimum': MaximumCalculationStrategy(),
            'Minimum': MinimumCalculationStrategy(),
            'Standart Sapma': StandardDeviationCalculationStrategy(),
            'Frekans': FrequencyCalculationStrategy(),
            'Medyan': MedianCalculationStrategy()
        }

        self.initUI()

    def initUI(self):
        self.setWindowTitle('İstatistiksel Analiz Uygulaması')
        self.setGeometry(100, 100, 700, 550) # Pencere boyutu ve konumu ayarlandı

        mainLayout = QVBoxLayout()

        # 1. Bölüm: Klasör Seçimi
        folderSelectLayout = QHBoxLayout()
        self.folderPathLineEdit = QLineEdit(self)
        self.folderPathLineEdit.setPlaceholderText("Lütfen ölçüm verilerinin olduğu kök klasörü seçin (örn: olcumler)...")
        self.folderPathLineEdit.setReadOnly(True)
        self.selectFolderButton = QPushButton('Klasör Seç', self)
        self.selectFolderButton.clicked.connect(self.selectFolder)

        folderSelectLayout.addWidget(self.folderPathLineEdit)
        folderSelectLayout.addWidget(self.selectFolderButton)
        mainLayout.addLayout(folderSelectLayout)

        # 2. Bölüm: Hesaplama Checkbox'ları
        calculationGroupBox = QLabel("<h3>Yapılacak Hesaplamaları Seçin:</h3>")
        mainLayout.addWidget(calculationGroupBox)

        self.checkboxLayout = QVBoxLayout()
        # Checkbox'ları bir sözlükte tutarak erişimi kolaylaştıralım
        self.calculation_checkboxes = {}
        for name in self.calculation_strategies.keys():
            cb = QCheckBox(name, self)
            self.checkboxLayout.addWidget(cb)
            self.calculation_checkboxes[name] = cb

        self.globalCalculationCheckBox = QCheckBox("Global Hesaplama Yap (Tüm Dosyaları Birleştir)", self)
        self.checkboxLayout.addWidget(self.globalCalculationCheckBox) # Global checkbox'ı ekle

        mainLayout.addLayout(self.checkboxLayout)

        # 3. Bölüm: Hesapla Butonu
        self.calculateButton = QPushButton('Hesapla', self)
        self.calculateButton.setFixedSize(150, 50)
        # Fonksiyon adını _perform_calculations olarak değiştirdik
        self.calculateButton.clicked.connect(self._perform_calculations) 

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.calculateButton)
        buttonLayout.addStretch(1)
        mainLayout.addLayout(buttonLayout)

        # 4. Bölüm: Mesaj İçeriği
        self.messageLabel = QLabel("Mesajlar burada görüntülenecek...", self)
        self.messageLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.messageLabel.setStyleSheet("border: 1px solid gray; padding: 10px; background-color: #f0f0f0;")
        self.messageLabel.setWordWrap(True) # Uzun metinleri sarmala

        # Mesaj alanını kaydırılabilir yap
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.messageLabel)
        mainLayout.addWidget(scroll_area)

        self.setLayout(mainLayout)

    # Yardımcı metod: Mesaj etiketini güncellemek için
    def _update_message_label(self, message: str):
        """QLabel'in metnine yeni bir mesaj ekler."""
        current_text = self.messageLabel.text()
        # İlk boş mesaj için sadece yeni metni kullan
        if current_text == "Mesajlar burada görüntülenecek...":
            self.messageLabel.setText(message)
        else:
            self.messageLabel.setText(current_text + "\n" + message)
        QApplication.processEvents() # UI'ın güncellenmesini sağla

    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Ölçüm Kök Klasörünü Seç", "")
        if folder:
            self.folderPathLineEdit.setText(folder)
            self._update_message_label(f"Klasör seçildi: {folder}\nVeriler okunuyor...")

            # Seçilen klasöre göre OutputWriter'ı başlat
            self.output_writer = OutputWriter(folder) 

            # Tüm ölçüm verilerini oku
            self.all_measurements_by_type = self.measurement_parser.get_all_measurements_in_folder(folder)

            temp_count = len(self.all_measurements_by_type['sıcaklık'])
            hum_count = len(self.all_measurements_by_type['nem'])

            self._update_message_label(
                f"Klasör seçildi: {folder}\n"
                f"Toplam {temp_count} sıcaklık dosyası ve {hum_count} nem dosyası bulundu.\n"
                f"Hesaplamak istediğiniz işlemleri seçip 'Hesapla' butonuna basın."
            )
        else:
            self.messageLabel.setText("Klasör seçimi iptal edildi.")
            self.all_measurements_by_type = {'sıcaklık': [], 'nem': []}
            self.output_writer = None

    # Refactored performCalculations method
    # main.py içindeki _perform_calculations metodu

# main.py içindeki _perform_calculations metodu

def _perform_calculations(self):
    if not self.folderPathLineEdit.text():
        self._update_message_label("Lütfen önce bir klasör seçin.")
        return

    if not self.output_writer:
        self._update_message_label("Hata: Çıktı yazıcısı başlatılamadı. Klasör seçimi hatası olabilir.")
        return

    selected_strategies_local = []
    selected_strategies_global = []

    # Her bir hesaplama türü için lokal ve global seçimleri kontrol et
    for name, cb_local in self.calculation_checkboxes.items():
        cb_global = self.global_calculation_checkboxes[name]

        if cb_local.isChecked():
            selected_strategies_local.append(self.calculation_strategies[name])

        if cb_global.isChecked():
            selected_strategies_global.append(self.calculation_strategies[name])

    # Eğer hiçbir lokal veya global hesaplama seçilmemişse
    if not selected_strategies_local and not selected_strategies_global:
        self._update_message_label("Lütfen en az bir lokal veya global hesaplama türü seçin.")
        return

    self._update_message_label("Hesaplamalar başlatılıyor...\n")

    overall_status_message = ""

    for measurement_type, measurements_list in self.all_measurements_by_type.items():
        # _process_measurement_type metodunu güncelleyelim, artık hem lokal hem global stratejileri alacak
        overall_status_message += self._process_measurement_type(
            measurement_type, measurements_list, selected_strategies_local, selected_strategies_global
        )

    self._update_message_label("\n--- Hesaplamalar tamamlandı! ---")
    if overall_status_message: 
        self._update_message_label(overall_status_message)
    QMessageBox.information(self, "Hesaplama Tamamlandı", "Tüm hesaplamalar tamamlandı ve sonuçlar kaydedildi.")

# Yeni _process_measurement_type tanımı
    def _process_measurement_type(self, measurement_type: str, measurements_list: list[MeasurementData], 
                                    selected_strategies_local: list[ICalculationStrategy], 
                                    selected_strategies_global: list[ICalculationStrategy]) -> str:
        """Belirli bir ölçüm türü için hesaplamaları yönetir."""
        status_message = ""
        if not measurements_list:
            status_message += f"'{measurement_type}' için dosya bulunamadı. Hesaplama atlandı.\n"
            return status_message

        self._update_message_label(f"\n--- {measurement_type.capitalize()} Hesaplamaları ---")

        # Global hesaplama için tüm değerleri birleştir (eğer herhangi bir global hesaplama seçilmişse)
        global_values = []
        if selected_strategies_global: # Sadece global strateji seçilmişse global_values'ı doldur
            for data in measurements_list:
                global_values.extend(data.values)

        for strategy in selected_strategies_local:
            # Lokal (dosya bazında) hesaplamalar
            self._calculate_and_write_local_results(measurement_type, measurements_list, strategy)

        for strategy in selected_strategies_global:
            # Global hesaplamalar (sadece seçili olanlar için)
            self._calculate_and_write_global_results(measurement_type, global_values, strategy)

        return status_message
# Yeni _process_measurement_type tanımı
    def _process_measurement_type(self, measurement_type: str, measurements_list: list[MeasurementData], 
                                    selected_strategies_local: list[ICalculationStrategy], 
                                    selected_strategies_global: list[ICalculationStrategy]) -> str:
        """Belirli bir ölçüm türü için hesaplamaları yönetir."""
        status_message = ""
        if not measurements_list:
            status_message += f"'{measurement_type}' için dosya bulunamadı. Hesaplama atlandı.\n"
            return status_message

        self._update_message_label(f"\n--- {measurement_type.capitalize()} Hesaplamaları ---")

        # Global hesaplama için tüm değerleri birleştir (eğer herhangi bir global hesaplama seçilmişse)
        global_values = []
        if selected_strategies_global: # Sadece global strateji seçilmişse global_values'ı doldur
            for data in measurements_list:
                global_values.extend(data.values)

        for strategy in selected_strategies_local:
            # Lokal (dosya bazında) hesaplamalar
            self._calculate_and_write_local_results(measurement_type, measurements_list, strategy)

        for strategy in selected_strategies_global:
            # Global hesaplamalar (sadece seçili olanlar için)
            self._calculate_and_write_global_results(measurement_type, global_values, strategy)

        return status_message
    
    
    def _process_measurement_type(self, measurement_type: str, measurements_list: list[MeasurementData], 
                                selected_strategies: list[ICalculationStrategy], is_global_calculation_enabled: bool) -> str:
        """Belirli bir ölçüm türü için hesaplamaları yönetir."""
        status_message = ""
        if not measurements_list:
            status_message += f"'{measurement_type}' için dosya bulunamadı. Hesaplama atlandı.\n"
            return status_message

        self._update_message_label(f"\n--- {measurement_type.capitalize()} Hesaplamaları ---")

        # Global hesaplama için tüm değerleri birleştir
        global_values = []
        if is_global_calculation_enabled:
            for data in measurements_list:
                global_values.extend(data.values)

        for strategy in selected_strategies:
            # Lokal (dosya bazında) hesaplamalar
            self._calculate_and_write_local_results(measurement_type, measurements_list, strategy)

            # Global hesaplamalarin
            if is_global_calculation_enabled:
                self._calculate_and_write_global_results(measurement_type, global_values, strategy)

        return status_message # Dış fonksiyona eklenmesi gereken mesajlar

    def _calculate_and_write_local_results(self, measurement_type: str, measurements_list: list[MeasurementData], strategy: ICalculationStrategy):
        """Lokal (dosya bazında) hesaplamaları yapar ve sonuçları yazar."""
        local_results = {}
        for data in measurements_list:
            try:
                result = strategy.calculate(data.values)
                header_info = f"id:{data.id} ölçüm: {data.measurement_type} - yer: {data.location} - tarih: {data.date.strftime('%d.%m.%Y')}"
                local_results[header_info] = result
            except ValueError as e:
                self._update_message_label(f"Uyarı ({measurement_type} - {data.id} - {strategy.name}): {e}")

        if local_results:
            output_path = self.output_writer.write_results(
                local_results, measurement_type, strategy.name, is_global=False
            )
            if output_path:
                    self._update_message_label(f"- {measurement_type.capitalize()} {strategy.name} (Lokal) sonuçları kaydedildi: {os.path.basename(output_path)}")
            else:
                self._update_message_label(f"- {measurement_type.capitalize()} {strategy.name} (Lokal) kaydedilemedi.")

    def _calculate_and_write_global_results(self, measurement_type: str, global_values: list[float], strategy: ICalculationStrategy):
        """Global hesaplamaları yapar ve sonuçları yazar."""
        if not global_values:
            self._update_message_label(f"Uyarı ({measurement_type} - Global - {strategy.name}): Global hesaplama için veri bulunamadı.")
            return

        try:
            global_result = strategy.calculate(global_values)
            global_results_dict = {f"Tüm {measurement_type} değerlerinin {strategy.name.lower()}": global_result}

            output_path = self.output_writer.write_results(
                global_results_dict, measurement_type, strategy.name, is_global=True
            )
            if output_path:
                self._update_message_label(f"- {measurement_type.capitalize()} {strategy.name} (Global) sonuçları kaydedildi: {os.path.basename(output_path)}")
            else:
                self._update_message_label(f"- {measurement_type.capitalize()} {strategy.name} (Global) kaydedilemedi.")
        except ValueError as e:
            self._update_message_label(f"Uyarı ({measurement_type} - Global - {strategy.name}): {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())