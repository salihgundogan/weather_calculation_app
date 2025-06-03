# calculation_strategies.py

from abc import ABC, abstractmethod
from typing import List, Dict # Buraya Dict eklendi!
import math
from collections import Counter

# Strateji arayüzü (soyut sınıf)
class ICalculationStrategy(ABC):
    """Tüm hesaplama stratejileri için ortak arayüz."""

    @abstractmethod
    def calculate(self, data_values: List[float]) -> any:
        """Verilen değerler listesi üzerinde hesaplamayı yapar."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Hesaplama stratejisinin adını döndürür."""
        pass

# Somut Stratejiler
class AverageCalculationStrategy(ICalculationStrategy):
    def calculate(self, data_values: List[float]) -> float:
        if not data_values:
            return 0.0
        return sum(data_values) / len(data_values)

    @property
    def name(self) -> str:
        return "Ortalama"

class MaximumCalculationStrategy(ICalculationStrategy):
    def calculate(self, data_values: List[float]) -> float:
        if not data_values:
            raise ValueError("Maksimum hesaplamak için veri bulunmuyor.")
        return max(data_values)

    @property
    def name(self) -> str:
        return "Maksimum"

class MinimumCalculationStrategy(ICalculationStrategy):
    def calculate(self, data_values: List[float]) -> float:
        if not data_values:
            raise ValueError("Minimum hesaplamak için veri bulunmuyor.")
        return min(data_values)

    @property
    def name(self) -> str:
        return "Minimum"

class StandardDeviationCalculationStrategy(ICalculationStrategy):
    def calculate(self, data_values: List[float]) -> float:
        if len(data_values) < 2:
            # Standart sapma için en az iki veri noktası gerekir
            return 0.0 # Veya ValueError raise edilebilir

        n = len(data_values)
        mean = sum(data_values) / n
        variance = sum([(x - mean) ** 2 for x in data_values]) / (n - 1) # Örneklem standart sapması
        return math.sqrt(variance)

    @property
    def name(self) -> str:
        return "Standart Sapma"

class FrequencyCalculationStrategy(ICalculationStrategy):
    def calculate(self, data_values: List[float]) -> Dict[float, int]:
        if not data_values:
            return {}
        # Sayıları tam sayıya yuvarlayarak frekans sayımı yapabiliriz
        # Float değerler için doğrudan Counter kullanmak bazı ondalık farklardan dolayı sorun yaratabilir.
        # Ödevde örnek çıktıya bakılırsa "9 Derece 8 defa ölçüldü" gibi tam sayı kullanılmış.
        # Bu yüzden float değerleri tam sayıya çevirme varsayımı yapabiliriz veya
        # float değerleri direkt sayabiliriz. Şimdilik direkt sayım yapalım.
        return dict(Counter(data_values))

    @property
    def name(self) -> str:
        return "Frekans"

class MedianCalculationStrategy(ICalculationStrategy):
    def calculate(self, data_values: List[float]) -> float:
        if not data_values:
            raise ValueError("Medyan hesaplamak için veri bulunmuyor.")

        sorted_values = sorted(data_values)
        n = len(sorted_values)

        if n % 2 == 1: # Tek sayıda eleman
            return sorted_values[n // 2]
        else: # Çift sayıda eleman
            mid1 = sorted_values[n // 2 - 1]
            mid2 = sorted_values[n // 2]
            return (mid1 + mid2) / 2

    @property
    def name(self) -> str:
        return "Medyan"