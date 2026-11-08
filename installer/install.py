"""Установщик mkusha ios: находит iPhone по USB и ставит IPA.

GUI на Tkinter + pymobiledevice3 под капотом.

Запуск:  install.cmd  (сам создаст venv и поставит зависимости)
Или:     python install.py --ipa path\to\app.ipa
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent


def pmd(*args: str, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pymobiledevice3", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def list_devices() -> list[dict]:
    try:
        proc = pmd("usbmux", "list", timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    text = (proc.stdout or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def device_label(dev: dict) -> str:
    name = dev.get("DeviceName") or dev.get("DeviceNameString") or "iPhone"
    udid = dev.get("UniqueDeviceID") or dev.get("Identifier") or ""
    ios = dev.get("ProductVersion") or dev.get("iOSVersion") or "?"
    return f"{name} · iOS {ios} · {udid[:8]}…"


def install_ipa(ipa: Path, udid: str | None = None) -> tuple[bool, str]:
    if not ipa.exists():
        return False, f"Файл не найден: {ipa}"
    args = ["apps", "install", str(ipa)]
    if udid:
        args += ["--udid", udid]
    try:
        proc = pmd(*args, timeout=600)
    except subprocess.TimeoutExpired:
        return False, "Установка не завершилась за 10 минут."
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, out or "(нет вывода)"


# ---------------------------------------------------------------- CLI

def run_cli(ipa: Path, udid: str | None) -> int:
    devices = list_devices()
    if not devices:
        print("iPhone не найден. Подключи кабелем и нажми «Доверять».")
        return 1
    print("Найдено устройств:", len(devices))
    for dev in devices:
        print("  -", device_label(dev))
    ok, out = install_ipa(ipa, udid)
    print(out)
    print("Готово." if ok else "Ошибка установки.")
    return 0 if ok else 1


# ---------------------------------------------------------------- GUI

def run_gui() -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("mkusha ios — установка")
    root.geometry("620x460")
    root.configure(bg="#0f1115")

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TLabel", background="#0f1115", foreground="#e6e9ef", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10), padding=8)
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
    style.configure("Dim.TLabel", foreground="#8b93a3")

    tk.Label(
        root, text="mkusha ios", bg="#0f1115", fg="#ffffff",
        font=("Segoe UI", 18, "bold"),
    ).pack(anchor="w", padx=18, pady=(18, 2))
    tk.Label(
        root, text="Найди iPhone по USB и установи IPA",
        bg="#0f1115", fg="#8b93a3", font=("Segoe UI", 10),
    ).pack(anchor="w", padx=18, pady=(0, 12))

    device_var = tk.StringVar(value="поиск устройства…")
    tk.Label(
        root, textvariable=device_var, bg="#0f1115", fg="#4f9cf9",
        font=("Segoe UI", 11, "bold"),
    ).pack(anchor="w", padx=18)

    ipa_var = tk.StringVar(value="")
    row = tk.Frame(root, bg="#0f1115")
    row.pack(fill="x", padx=18, pady=12)

    entry = tk.Entry(
        row, textvariable=ipa_var, bg="#0b0d11", fg="#e6e9ef",
        insertbackground="#e6e9ef", relief="flat",
    )
    entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))

    def pick_ipa() -> None:
        path = filedialog.askopenfilename(
            title="Выбери IPA", filetypes=[("iOS app", "*.ipa"), ("All", "*.*")]
        )
        if path:
            ipa_var.set(path)

    tk.Button(row, text="Обзор", command=pick_ipa, bg="#1c2029", fg="#e6e9ef",
              relief="flat", padx=14).pack(side="left")

    log_box = tk.Text(
        root, height=14, bg="#0b0d11", fg="#9aa4b5", relief="flat",
        font=("Consolas", 9), wrap="word",
    )
    log_box.pack(fill="both", expand=True, padx=18, pady=(4, 8))

    def log(text: str) -> None:
        log_box.insert("end", text + "\n")
        log_box.see("end")

    devices: list[dict] = []

    def refresh() -> None:
        nonlocal devices
        device_var.set("поиск устройства…")
        root.update_idletasks()
        devices = list_devices()
        if devices:
            device_var.set("● " + device_label(devices[0]))
            log("Найдено: " + device_label(devices[0]))
        else:
            device_var.set("○ iPhone не найден")
            log("Устройство не найдено. Проверь кабель и «Доверять компьютеру».")

    def do_install() -> None:
        ipa = Path(ipa_var.get().strip())
        if not ipa_var.get().strip():
            messagebox.showwarning("mkusha", "Сначала выбери IPA.")
            return
        if not devices:
            messagebox.showwarning("mkusha", "iPhone не найден.")
            return
        btn_install.config(state="disabled", text="Устанавливаю…")

        def worker() -> None:
            ok, out = install_ipa(ipa, devices[0].get("UniqueDeviceID"))
            log(out)
            log("Готово." if ok else "Ошибка установки.")
            btn_install.config(state="normal", text="Установить")
            if ok:
                messagebox.showinfo("mkusha", "Приложение установлено.")

        threading.Thread(target=worker, daemon=True).start()

    buttons = tk.Frame(root, bg="#0f1115")
    buttons.pack(fill="x", padx=18, pady=(0, 16))

    tk.Button(buttons, text="Обновить", command=refresh, bg="#1c2029", fg="#e6e9ef",
              relief="flat", padx=14, pady=8).pack(side="left")
    btn_install = tk.Button(buttons, text="Установить", command=do_install,
                            bg="#ffffff", fg="#000000", relief="flat",
                            font=("Segoe UI", 10, "bold"), padx=24, pady=8)
    btn_install.pack(side="right")

    # авто-поиск IPA рядом со скриптом
    for candidate in list(APP_DIR.glob("*.ipa")) + list((APP_DIR / "..").glob("*.ipa")):
        ipa_var.set(str(candidate.resolve()))
        break

    refresh()
    root.mainloop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="mkusha ios installer")
    parser.add_argument("--ipa", type=Path, help="путь к .ipa")
    parser.add_argument("--udid", help="UDID устройства (если подключено несколько)")
    parser.add_argument("--gui", action="store_true", help="открыть окно")
    args = parser.parse_args()

    if args.ipa:
        return run_cli(args.ipa, args.udid)
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
