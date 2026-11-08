"""
mkusha iOS Installer
Автоматически скачивает последний IPA из GitHub Actions и устанавливает на iPhone.
"""
import subprocess
import sys
import os
import zipfile
import tempfile
import urllib.request
import json
import time
import shutil

REPO = "wizzardd1337/mkusha-ios"
ARTIFACT_NAME = "mkusha-unsigned-ipa"
WORKFLOW_FILE = "build-unsigned.yml"

# nightly.link дает прямые ссылки на артефакты публичных репо без авторизации
NIGHTLY_LINK = f"https://nightly.link/{REPO}/workflows/{WORKFLOW_FILE}/main/{ARTIFACT_NAME}.zip"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IPA_DIR = os.path.join(SCRIPT_DIR, "ipa_cache")


def log(msg):
    print(f"[mkusha] {msg}")


def ensure_pymobiledevice3():
    """Устанавливает pymobiledevice3 если не установлен."""
    try:
        import pymobiledevice3
        log(f"pymobiledevice3 v{pymobiledevice3.__version__} найден")
        return True
    except ImportError:
        pass

    log("Устанавливаю pymobiledevice3...")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pymobiledevice3"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        log(f"Ошибка установки pymobiledevice3: {r.stderr}")
        return False
    log("pymobiledevice3 установлен!")
    return True


def download_ipa():
    """Скачивает последний IPA из GitHub Actions через nightly.link."""
    os.makedirs(IPA_DIR, exist_ok=True)
    ipa_path = os.path.join(IPA_DIR, "mkusha-unsigned.ipa")
    zip_path = os.path.join(IPA_DIR, "artifact.zip")

    log("Скачиваю последний IPA из GitHub Actions...")
    log(f"URL: {NIGHTLY_LINK}")

    try:
        req = urllib.request.Request(NIGHTLY_LINK, headers={"User-Agent": "mkusha-installer"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            with open(zip_path, "wb") as f:
                f.write(data)
        log(f"Скачано {len(data)} байт")
    except Exception as e:
        log(f"Ошибка скачивания: {e}")
        # Попробуем альтернативный способ через GitHub API
        log("Пробую альтернативный способ через GitHub API...")
        if not download_ipa_via_api(ipa_path):
            # Проверим, есть ли уже IPA в кэше
            if os.path.exists(ipa_path):
                log(f"Использую кэшированный IPA: {ipa_path}")
                return ipa_path
            log("Не удалось скачать IPA. Скачай вручную:")
            log(f"  https://github.com/{REPO}/actions")
            log(f"  Скачай артефакт '{ARTIFACT_NAME}' и положи в: {IPA_DIR}")
            return None

    # Распаковываем ZIP
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            log(f"Содержимое архива: {names}")
            for name in names:
                if name.endswith(".ipa"):
                    zf.extract(name, IPA_DIR)
                    extracted = os.path.join(IPA_DIR, name)
                    if extracted != ipa_path:
                        shutil.move(extracted, ipa_path)
                    break
            else:
                # IPA может быть единственным файлом
                zf.extractall(IPA_DIR)
                # Ищем IPA
                for root, dirs, files in os.walk(IPA_DIR):
                    for f in files:
                        if f.endswith(".ipa"):
                            found = os.path.join(root, f)
                            if found != ipa_path:
                                shutil.move(found, ipa_path)
                            break
    except zipfile.BadZipFile:
        # Может быть сам файл уже IPA
        if zip_path != ipa_path:
            shutil.move(zip_path, ipa_path)

    if os.path.exists(zip_path) and zip_path != ipa_path:
        os.remove(zip_path)

    if os.path.exists(ipa_path):
        size_mb = os.path.getsize(ipa_path) / (1024 * 1024)
        log(f"IPA готов: {ipa_path} ({size_mb:.1f} MB)")
        return ipa_path
    else:
        log("IPA файл не найден после распаковки!")
        return None


def download_ipa_via_api(ipa_path):
    """Альтернативный способ через GitHub API (для публичных репо артефакты требуют токен)."""
    try:
        headers = {"User-Agent": "mkusha-installer"}
        url = f"https://api.github.com/repos/{REPO}/actions/artifacts?name={ARTIFACT_NAME}&per_page=1"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            artifacts = data.get("artifacts", [])
            if not artifacts:
                log("Артефакты не найдены")
                return False
            art = artifacts[0]
            log(f"Найден артефакт: {art['name']} ({art['size_in_bytes']} bytes)")
            log("Для скачивания артефактов через API нужен GitHub токен.")
            log("Используй nightly.link или скачай вручную.")
            return False
    except Exception as e:
        log(f"GitHub API ошибка: {e}")
        return False


def find_device():
    """Находит подключенный iPhone."""
    log("Ищу подключенный iPhone...")
    r = subprocess.run(
        [sys.executable, "-m", "pymobiledevice3", "usbmux", "list", "--no-color"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        # Попробуем другой формат
        r = subprocess.run(
            [sys.executable, "-m", "pymobiledevice3", "usbmux", "list"],
            capture_output=True, text=True
        )
    
    output = r.stdout.strip()
    if not output or "no devices" in output.lower() or output == "[]":
        log("iPhone не найден! Убедись что:")
        log("  1. iPhone подключен USB-кабелем")
        log("  2. На iPhone нажал 'Доверять этому компьютеру'")
        log("  3. iTunes/Apple Devices установлен на Windows")
        return None
    
    log(f"Устройства:\n{output}")
    return output


def install_ipa(ipa_path):
    """Устанавливает IPA на iPhone через pymobiledevice3."""
    log(f"Устанавливаю {os.path.basename(ipa_path)} на iPhone...")
    log("Это может занять 1-2 минуты...")

    r = subprocess.run(
        [sys.executable, "-m", "pymobiledevice3", "apps", "install", ipa_path],
        capture_output=False,  # показываем прогресс в реальном времени
        text=True
    )

    if r.returncode == 0:
        log("="*50)
        log("✅ ПРИЛОЖЕНИЕ УСТАНОВЛЕНО УСПЕШНО!")
        log("="*50)
        log("")
        log("Что дальше:")
        log("  1. На iPhone: Настройки -> Основные -> VPN и управление устройством")
        log("     -> Доверяй профилю разработчика")
        log("  2. Открой приложение mkusha")
        log("  3. Включи VPN-профиль в приложении")
        log("  4. Отключи сотовую связь (оставь Wi-Fi)")
        log("  5. Выбери точку на карте -> 'Set as Location'")
        return True
    else:
        log(f"Ошибка установки (код {r.returncode})")
        log("Попробуй:")
        log("  1. Разблокировать iPhone")
        log("  2. Нажать 'Доверять' если появится запрос")
        log("  3. Установить iTunes/Apple Devices из Microsoft Store")
        log("  4. Запустить скрипт от имени администратора")
        return False


def main():
    print()
    print("=" * 50)
    print("  mkusha iOS Installer")
    print("  Автоустановка приложения на iPhone")
    print("=" * 50)
    print()

    # 1. Проверяем pymobiledevice3
    if not ensure_pymobiledevice3():
        input("\nНажми Enter для выхода...")
        return

    # 2. Проверяем подключение iPhone
    device = find_device()
    if not device:
        input("\nПодключи iPhone и нажми Enter для повтора...")
        device = find_device()
        if not device:
            input("\nНажми Enter для выхода...")
            return

    # 3. Скачиваем IPA
    ipa_path = download_ipa()
    if not ipa_path:
        input("\nНажми Enter для выхода...")
        return

    # 4. Устанавливаем
    install_ipa(ipa_path)
    
    print()
    input("Нажми Enter для выхода...")


if __name__ == "__main__":
    main()
