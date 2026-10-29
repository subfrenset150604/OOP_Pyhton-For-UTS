"""Jawaban UTS Pemrograman Berorientasi Objek (Python).

Membaca employee.json dan sensor_logs.json, menerapkan rule-based processing,
inheritance, polymorphism, serta method overriding.

Catatan: PDF soal tidak menentukan persentase bonus ataupun ambang suhu.
Aturan yang digunakan di bawah merupakan asumsi implementasi dan bisa diubah
pada bagian KONFIGURASI ATURAN.
"""

from abc import ABC, abstractmethod
from collections import Counter
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
EMPLOYEE_FILE = BASE_DIR / "employee.json"
SENSOR_FILE = BASE_DIR / "sensor_logs.json"

# ============================================================
# KONFIGURASI ATURAN (RULE-BASED)
# ============================================================
# Asumsi untuk contoh perhitungan payroll:
# - PERF2026 : bonus 10% dari gaji pokok
# - SENIOR10 : bonus 10% dari gaji pokok
# - LEAD2026 : bonus 15% dari gaji pokok
# - Bonus hanya diberikan kepada pegawai tetap.
BONUS_RATE_BY_CODE = {
    "PERF2026": 0.10,
    "SENIOR10": 0.10,
    "LEAD2026": 0.15,
}

# Aturan klasifikasi suhu berdasarkan asumsi implementasi:
# - suhu >= 85 derajat: DANGER
# - suhu >= 65 dan < 85 derajat: WARNING
# - suhu < 65 derajat: NORMAL
DANGER_MIN_TEMPERATURE = 85.0
WARNING_MIN_TEMPERATURE = 65.0


def rupiah(amount: float) -> str:
    """Format angka menjadi teks Rupiah tanpa angka desimal."""
    return f"Rp{amount:,.0f}".replace(",", ".")


def load_json(path: Path, collection_key: str) -> list[dict[str, Any]]:
    """Memuat koleksi dari JSON dengan validasi error dasar."""
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"File '{path.name}' tidak ditemukan. Pastikan file JSON satu folder dengan main.py."
        ) from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Isi JSON '{path.name}' tidak valid: {error}") from error

    if collection_key not in data or not isinstance(data[collection_key], list):
        raise ValueError(
            f"Struktur '{path.name}' harus memiliki key '{collection_key}' berupa list."
        )
    return data[collection_key]


# ============================================================
# BAGIAN 1 - EMPLOYEE: INHERITANCE, OVERRIDE, POLYMORPHISM
# ============================================================
class Employee(ABC):
    """Kelas induk/abstrak untuk semua jenis pegawai."""

    def __init__(
        self,
        emp_id: str,
        name: str,
        base_salary: float,
        bonus_code: str | None,
    ) -> None:
        self.emp_id = emp_id
        self.name = name
        self.base_salary = float(base_salary)
        self.bonus_code = bonus_code

    @property
    @abstractmethod
    def employment_type(self) -> str:
        """Jenis pegawai yang diisi oleh kelas turunan."""
        raise NotImplementedError

    @abstractmethod
    def calculate_bonus(self) -> float:
        """Aturan bonus di-override oleh setiap kelas turunan."""
        raise NotImplementedError

    def calculate_total_salary(self) -> float:
        """Memanggil calculate_bonus() sesuai objek sebenarnya (polymorphism)."""
        return self.base_salary + self.calculate_bonus()

    def report(self) -> str:
        bonus = self.calculate_bonus()
        code = self.bonus_code if self.bonus_code else "-"
        return (
            f"{self.emp_id:<9} | {self.name:<20} | {self.employment_type:<8} | "
            f"{code:<10} | {rupiah(self.base_salary):>14} | "
            f"{rupiah(bonus):>12} | {rupiah(self.calculate_total_salary()):>14}"
        )


class PermanentEmployee(Employee):
    """Kelas turunan untuk pegawai tetap."""

    @property
    def employment_type(self) -> str:
        return "Tetap"

    def calculate_bonus(self) -> float:
        """OVERRIDE: pegawai tetap memperoleh bonus sesuai bonus_code."""
        if not self.bonus_code:
            return 0.0
        rate = BONUS_RATE_BY_CODE.get(self.bonus_code, 0.0)
        return self.base_salary * rate


class ContractEmployee(Employee):
    """Kelas turunan untuk pegawai kontrak."""

    @property
    def employment_type(self) -> str:
        return "Kontrak"

    def calculate_bonus(self) -> float:
        """OVERRIDE: berdasarkan aturan yang dipilih, pegawai kontrak tidak mendapat bonus."""
        return 0.0


def create_employee(record: dict[str, Any]) -> Employee:
    """Factory sederhana: memilih kelas pegawai berdasarkan is_permanent."""
    employee_class = PermanentEmployee if record.get("is_permanent", False) else ContractEmployee
    return employee_class(
        emp_id=record["emp_id"],
        name=record["name"],
        base_salary=record["base_salary"],
        bonus_code=record.get("bonus_code"),
    )


def process_employees(records: list[dict[str, Any]]) -> None:
    employees = [create_employee(record) for record in records]

    print("=" * 115)
    print("1. LAPORAN DATA PEGAWAI")
    print("=" * 115)
    print(
        f"{'ID':<9} | {'Nama':<20} | {'Status':<8} | {'Kode Bonus':<10} | "
        f"{'Gaji Pokok':>14} | {'Bonus':>12} | {'Total Gaji':>14}"
    )
    print("-" * 115)

    # POLYMORPHISM: setiap objek memproses calculate_bonus() dengan aturan kelasnya.
    for employee in employees:
        print(employee.report())

    permanent_count = sum(isinstance(employee, PermanentEmployee) for employee in employees)
    contract_count = len(employees) - permanent_count
    total_base_salary = sum(employee.base_salary for employee in employees)
    total_bonus = sum(employee.calculate_bonus() for employee in employees)
    total_payroll = sum(employee.calculate_total_salary() for employee in employees)

    print("-" * 115)
    print(f"Jumlah pegawai       : {len(employees)} orang")
    print(f"Pegawai tetap        : {permanent_count} orang")
    print(f"Pegawai kontrak      : {contract_count} orang")
    print(f"Total gaji pokok     : {rupiah(total_base_salary)}")
    print(f"Total bonus          : {rupiah(total_bonus)}")
    print(f"Total penggajian     : {rupiah(total_payroll)}")


# ============================================================
# BAGIAN 2 - SENSOR: RULE-BASED CLASSIFICATION + OOP
# ============================================================
class SensorReading(ABC):
    """Kelas induk/abstrak untuk data pembacaan sensor."""

    status_label = "UNKNOWN"

    def __init__(self, record: dict[str, Any]) -> None:
        self.sensor_id = record["sensor_id"]
        self.location = record["location"]
        self.temperature = float(record["temperature"])
        # Status dari JSON disimpan untuk dibandingkan dengan hasil rule suhu.
        self.reported_status = str(record.get("status", "UNKNOWN")).upper()
        self.operator_id = record.get("operator_id")

    @abstractmethod
    def recommended_action(self) -> str:
        """Pesan tindak lanjut di-override oleh kelas status sensor."""
        raise NotImplementedError

    def is_reported_status_consistent(self) -> bool:
        return self.reported_status == self.status_label

    def report(self) -> str:
        operator = str(self.operator_id) if self.operator_id is not None else "Belum ditugaskan"
        consistency = "Sesuai" if self.is_reported_status_consistent() else (
            f"Tidak sesuai (JSON={self.reported_status}, rule={self.status_label})"
        )
        return (
            f"{self.sensor_id} | {self.location:<15} | {self.temperature:>5.1f} C | "
            f"Status: {self.status_label:<7} | Operator: {operator:<16} | "
            f"Validasi: {consistency} | Tindakan: {self.recommended_action()}"
        )


class DangerSensor(SensorReading):
    """Kelas turunan untuk suhu berbahaya."""

    status_label = "DANGER"

    def recommended_action(self) -> str:
        """OVERRIDE: tindakan saat suhu mencapai atau melampaui ambang bahaya."""
        return "Aktifkan alarm dan periksa sistem pendinginan segera."


class WarningSensor(SensorReading):
    """Kelas turunan untuk suhu peringatan."""

    status_label = "WARNING"

    def recommended_action(self) -> str:
        """OVERRIDE: tindakan saat suhu berada dalam rentang peringatan."""
        return "Periksa kondisi dan tingkatkan pemantauan suhu."


class NormalSensor(SensorReading):
    """Kelas turunan untuk suhu normal."""

    status_label = "NORMAL"

    def recommended_action(self) -> str:
        """OVERRIDE: tindakan saat suhu masih dalam rentang normal."""
        return "Kondisi normal; lanjutkan pemantauan rutin."


def classify_sensor(record: dict[str, Any]) -> SensorReading:
    """RULE: menentukan kelas sensor berdasarkan temperatur."""
    temperature = float(record["temperature"])
    if temperature >= DANGER_MIN_TEMPERATURE:
        sensor_class = DangerSensor
    elif temperature >= WARNING_MIN_TEMPERATURE:
        sensor_class = WarningSensor
    else:
        sensor_class = NormalSensor
    return sensor_class(record)


def process_sensors(records: list[dict[str, Any]]) -> None:
    sensors = [classify_sensor(record) for record in records]

    print("\n" + "=" * 145)
    print("2. LAPORAN PEMBACAAN SENSOR")
    print("=" * 145)
    print("Aturan suhu: DANGER >= 85 C; WARNING >= 65 C dan < 85 C; NORMAL < 65 C.")
    print("-" * 145)

    # POLYMORPHISM: semua objek memanggil recommended_action(), tetapi hasilnya berbeda.
    for sensor in sensors:
        print(sensor.report())

    counts = Counter(sensor.status_label for sensor in sensors)
    consistent_count = sum(sensor.is_reported_status_consistent() for sensor in sensors)
    unassigned_count = sum(sensor.operator_id is None for sensor in sensors)
    danger_locations = [
        f"{sensor.sensor_id} ({sensor.location}, {sensor.temperature:.1f} C)"
        for sensor in sensors
        if sensor.status_label == "DANGER"
    ]

    print("-" * 145)
    print(f"Jumlah pembacaan sensor            : {len(sensors)}")
    print(f"Sensor DANGER                     : {counts['DANGER']}")
    print(f"Sensor WARNING                    : {counts['WARNING']}")
    print(f"Sensor NORMAL                     : {counts['NORMAL']}")
    print(f"Status JSON sesuai dengan rule suhu: {consistent_count}/{len(sensors)}")
    print(f"Sensor tanpa operator             : {unassigned_count}")
    print("Daftar sensor DANGER:")
    for item in danger_locations:
        print(f"  - {item}")


def main() -> None:
    try:
        employee_records = load_json(EMPLOYEE_FILE, "employees")
        sensor_records = load_json(SENSOR_FILE, "readings")
    except (FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}")
        return

    print("PROGRAM OOP - PENGOLAHAN DATA JSON")
    print("Konsep: Rule-Based, Inheritance, Polymorphism, dan Method Overriding")
    process_employees(employee_records)
    process_sensors(sensor_records)
    print("\nProgram selesai.")


if __name__ == "__main__":
    main()
