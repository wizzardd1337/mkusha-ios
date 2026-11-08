# mkusha ios — Setup Guide

## Быстрый старт

### 1. Сборка IPA

**Вариант A: GitHub Actions (рекомендуется)**
1. Пушь код в GitHub-репозиторий
2. GitHub Actions автоматически соберёт unsigned IPA
3. Скачай артефакт из вкладки Actions

**Вариант B: Локально на macOS**
1. Установи Xcode 15+
2. Установи XcodeGen: `brew install xcodegen`
3. Собери Go-библиотеку:
   ```bash
   cd GoSpoofer
   chmod +x make.sh
   ./make.sh
   ```
4. Сгенерируй проект:
   ```bash
   xcodegen generate
   ```
5. Открой `location-spoofer.xcodeproj` в Xcode
6. Выбери свой Team в Signing & Capabilities
7. Build → Archive → Export IPA

### 2. Установка на iPhone

#### Автоматический установщик (Windows)
1. Подключи iPhone к ПК по USB
2. На iPhone нажми «Доверять этому компьютеру»
3. Положи `.ipa` файл в папку `installer/`
4. Запусти `installer/install.cmd`
   - Автоматически создаст Python venv
   - Установит pymobiledevice3
   - Найдёт iPhone и установит приложение

#### Ручная установка
```
cd installer
python -m pip install pymobiledevice3
python install.py --ipa path\to\mkusha.ipa
```

### 3. Первый запуск на iPhone

1. Открой приложение **mkusha ios**
2. Пройди 3 шага настройки:
   - **Шаг 1:** Авторизуй VPN (нажми «Разрешить» в системном диалоге)
   - **Шаг 2:** Скачай и установи сертификат (через Safari → Настройки)
   - **Шаг 3:** Доверь сертификату (Настройки → Основные → Об этом устройстве → Доверие сертификатам)
3. Готово! Выбери точку на карте и нажми **Spoof**

## Подписание приложения

> **Важно:** NetworkExtension (PacketTunnel) требует платный Apple Developer Account (\$99/год).

### Варианты подписи:

| Способ | Стоимость | Примечание |
|--------|-----------|------------|
| Apple Developer Program | \$99/год | Официальный, стабильный |
| SideStore / AltStore | Бесплатно | Требует периодическое переподписание (7 дней) |
| TrollStore | Бесплатно | Только для уязвимых версий iOS |

### Для LocalDevVPN (без сотовой связи):
Если ты используешь LocalDevVPN подход — отключи сотовую связь на iPhone перед использованием спуфинга.

## Структура проекта

```
mkusha-ios/
├── App/                    # Основное приложение (SwiftUI)
│   ├── ContentView.swift   # Точка входа, VPN-менеджер
│   ├── MapHomeView.swift   # Карта, поиск, спуфинг
│   ├── FirstSetupView.swift # Первоначальная настройка
│   ├── MkushaTheme.swift   # Тема Liquid Glass
│   ├── PulseMarker.swift   # Зелёная пульсирующая точка
│   └── ...
├── Tunnel/                 # Network Extension (VPN)
├── GoSpoofer/              # Go MITM-прокси
├── Widgets/                # Live Activity / Dynamic Island
├── Shared/                 # Общий код (ActivityAttributes)
├── Resources/              # Info.plist, иконки, entitlements
├── installer/              # Windows-установщик
│   ├── install.cmd         # Запуск (создаёт venv автоматически)
│   └── install.py          # Установщик (Tkinter + pymobiledevice3)
└── project.yml             # XcodeGen конфигурация
```

## Требования

- **Сборка:** macOS + Xcode 15+ или GitHub Actions
- **Установка:** Windows + Python 3.10+ + USB-кабель
- **iPhone:** iOS 18.0+
- **Live Activity:** iPhone 14 Pro+ (Dynamic Island)

## Устранение неполадок

### iPhone не найден
- Проверь USB-кабель (используй оригинальный)
- На iPhone нажми «Доверять этому компьютеру»
- Установи iTunes (для Windows-драйверов)

### VPN не подключается
- Перезапусти приложение
- Проверь Настройки → VPN, что профиль mkusha ios выбран
- Перезагрузи iPhone

### Локация не меняется
- Выключи и включи Службы геолокации (Настройки → Конфиденциальность)
- Подожди 3 секунды между выключением и включением
- Убедись, что сертификат установлен И доверен

