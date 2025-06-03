# measurement.py

from dataclasses import dataclass, field
from typing import List, Dict
import datetime

@dataclass
class MeasurementPoint:
    """Tek bir ölçüm noktasını (zaman ve değer) temsil eder."""
    time: datetime.time
    value: float

@dataclass
class MeasurementData:
    """Tek bir ölçüm dosyasındaki tüm veriyi temsil eder."""
    id: str
    measurement_type: str # 'sıcaklık' veya 'nem'
    location: str
    date: datetime.date
    points: List[MeasurementPoint] = field(default_factory=list) # Ölçüm noktaları listesi

    @property
    def values(self) -> List[float]:
        """Tüm ölçüm değerlerini bir liste olarak döndürür."""
        return [p.value for p in self.points]