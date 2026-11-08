"""
mkusha PC Location Spoofer for iOS 17 / 18
Работает напрямую через Apple DVT без Apple ID, без паролей и без Sideloadly!
"""
import http.server
import socketserver
import urllib.parse
import json
import subprocess
import sys
import os
import webbrowser
import threading
import time

PORT = 8777
current_proc = None
current_location = None
device_name = "iPhone"


def log(msg):
    print(f"[mkusha-spoofer] {msg}")


def get_connected_device():
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pymobiledevice3", "usbmux", "list", "--no-color"],
            capture_output=True, text=True, timeout=5
        )
        out = r.stdout.strip()
        if out and out != "[]":
            return "Mark's iPhone (Подключен ✅)"
    except Exception:
        pass
    return "iPhone (Проверьте подключение USB)"


def set_location(lat, lon):
    global current_proc, current_location
    stop_simulation()
    log(f"Устанавливаю локацию: lat={lat}, lon={lon}")
    cmd = [
        sys.executable, "-m", "pymobiledevice3",
        "developer", "dvt", "simulate-location", "set",
        "--", str(lat), str(lon)
    ]
    current_proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    current_location = {"lat": lat, "lon": lon}
    return True


def stop_simulation():
    global current_proc, current_location
    if current_proc:
        try:
            current_proc.terminate()
            current_proc.wait(timeout=2)
        except Exception:
            try:
                current_proc.kill()
            except Exception:
                pass
        current_proc = None
    
    # Сбрасываем в iOS
    try:
        subprocess.run(
            [sys.executable, "-m", "pymobiledevice3", "developer", "dvt", "simulate-location", "clear"],
            capture_output=True, timeout=5
        )
    except Exception:
        pass
    current_location = None
    log("Локация сброшена на реальный GPS.")


HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>mkusha - Подмена локации iPhone</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #121214; color: #fff; height: 100vh; display: flex; flex-direction: column; }
        header { background: #1a1a1e; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a2a30; }
        .logo { font-size: 18px; font-weight: 700; color: #3b82f6; display: flex; align-items: center; gap: 8px; }
        .status-badge { background: #1e293b; color: #60a5fa; padding: 6px 12px; border-radius: 20px; font-size: 13px; border: 1px solid #3b82f6; }
        #main { display: flex; flex: 1; height: calc(100vh - 60px); }
        #sidebar { width: 340px; background: #18181c; padding: 20px; border-right: 1px solid #2a2a30; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
        #map { flex: 1; height: 100%; }
        .input-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 6px; }
        .input-group input { width: 100%; background: #222228; border: 1px solid #33333d; border-radius: 8px; padding: 10px 12px; color: #fff; font-size: 14px; outline: none; }
        .input-group input:focus { border-color: #3b82f6; }
        .btn { padding: 12px 16px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; border: none; transition: 0.2s; display: flex; justify-content: center; align-items: center; gap: 8px; }
        .btn-primary { background: #2563eb; color: #fff; }
        .btn-primary:hover { background: #1d4ed8; }
        .btn-danger { background: #dc2626; color: #fff; }
        .btn-danger:hover { background: #b91c1c; }
        .presets { display: flex; flex-wrap: wrap; gap: 6px; }
        .preset-btn { background: #24242c; border: 1px solid #33333e; color: #cbd5e1; padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; }
        .preset-btn:hover { background: #2d2d38; color: #fff; border-color: #3b82f6; }
        .info-box { background: #1e293b; border-left: 4px solid #3b82f6; padding: 10px 12px; font-size: 12px; border-radius: 4px; color: #cbd5e1; line-height: 1.5; }
        .active-box { background: #064e3b; border-left: 4px solid #10b981; color: #a7f3d0; padding: 10px; border-radius: 6px; font-size: 13px; display: none; }
    </style>
</head>
<body>
    <header>
        <div class="logo">📍 mkusha Location Spoofer</div>
        <div class="status-badge" id="deviceStatus">🔍 Поиск iPhone...</div>
    </header>
    <div id="main">
        <div id="sidebar">
            <div id="activeBox" class="active-box">
                <b>Активно:</b> <span id="activeCoords">-</span>
            </div>

            <div class="input-group">
                <label>Поиск города или места:</label>
                <input type="text" id="searchInput" placeholder="Например: Дубай, Париж, Сочи..." onkeydown="if(event.key==='Enter') searchLocation()">
            </div>

            <div class="input-group">
                <label>Широта (Latitude):</label>
                <input type="number" step="any" id="latInput" placeholder="55.7558">
            </div>

            <div class="input-group">
                <label>Долгота (Longitude):</label>
                <input type="number" step="any" id="lonInput" placeholder="37.6173">
            </div>

            <button class="btn btn-primary" onclick="applyLocation()">
                📍 Установить на iPhone
            </button>

            <button class="btn btn-danger" onclick="resetLocation()">
                🔄 Сбросить на реальный GPS
            </button>

            <div>
                <label style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 8px;">Быстрые пресеты:</label>
                <div class="presets">
                    <button class="preset-btn" onclick="setPreset(55.7558, 37.6173, 'Москва')">Москва</button>
                    <button class="preset-btn" onclick="setPreset(59.9343, 30.3351, 'Санкт-Петербург')">СПб</button>
                    <button class="preset-btn" onclick="setPreset(25.2048, 55.2708, 'Дубай')">Дубай</button>
                    <button class="preset-btn" onclick="setPreset(52.5200, 13.4050, 'Берлин')">Берлин</button>
                    <button class="preset-btn" onclick="setPreset(48.8566, 2.3522, 'Париж')">Париж</button>
                    <button class="preset-btn" onclick="setPreset(40.7128, -74.0060, 'Нью-Йорк')">Нью-Йорк</button>
                    <button class="preset-btn" onclick="setPreset(35.6762, 139.6503, 'Токио')">Токио</button>
                </div>
            </div>

            <div class="info-box">
                <b>💡 Как пользоваться:</b><br>
                1. Кликни в любую точку на карте.<br>
                2. Нажми кнопку «Установить на iPhone».<br>
                3. Открой «Карты» или Telegram на телефоне — ты сразу будешь там!
            </div>
        </div>
        <div id="map"></div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        var map = L.map('map').setView([55.7558, 37.6173], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(map);

        var currentMarker = null;

        function setMarker(lat, lon, zoomTo=false) {
            document.getElementById('latInput').value = lat.toFixed(6);
            document.getElementById('lonInput').value = lon.toFixed(6);
            if (currentMarker) map.removeLayer(currentMarker);
            currentMarker = L.marker([lat, lon]).addTo(map);
            if (zoomTo) map.setView([lat, lon], 14);
        }

        map.on('click', function(e) {
            setMarker(e.latlng.lat, e.latlng.lng);
        });

        function setPreset(lat, lon, name) {
            setMarker(lat, lon, true);
            applyLocation();
        }

        function applyLocation() {
            var lat = parseFloat(document.getElementById('latInput').value);
            var lon = parseFloat(document.getElementById('lonInput').value);
            if (isNaN(lat) || isNaN(lon)) {
                alert('Сначала выберите точку на карте или введите координаты!');
                return;
            }
            fetch('/api/set?lat=' + lat + '&lon=' + lon)
                .then(r => r.json())
                .then(d => {
                    if (d.ok) {
                        document.getElementById('activeBox').style.display = 'block';
                        document.getElementById('activeCoords').innerText = lat.toFixed(4) + ', ' + lon.toFixed(4);
                        alert('✅ Локация установлена на iPhone: ' + lat + ', ' + lon);
                    } else {
                        alert('Ошибка: ' + d.error);
                    }
                });
        }

        function resetLocation() {
            fetch('/api/clear')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('activeBox').style.display = 'none';
                    if (currentMarker) map.removeLayer(currentMarker);
                    alert('🔄 Локация сброшена на реальный GPS!');
                });
        }

        function searchLocation() {
            var q = document.getElementById('searchInput').value;
            if (!q) return;
            fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(q))
                .then(r => r.json())
                .then(data => {
                    if (data && data.length > 0) {
                        var lat = parseFloat(data[0].lat);
                        var lon = parseFloat(data[0].lon);
                        setMarker(lat, lon, true);
                    } else {
                        alert('Место не найдено');
                    }
                });
        }

        // Обновляем статус устройства
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('deviceStatus').innerText = d.device;
                });
        }
        setInterval(updateStatus, 3000);
        updateStatus();
    </script>
</body>
</html>
"""


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

        elif path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            dev = get_connected_device()
            resp = {
                "device": dev,
                "active": current_location is not None,
                "location": current_location
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        elif path == "/api/set":
            try:
                lat = float(query.get("lat", [0])[0])
                lon = float(query.get("lon", [0])[0])
                set_location(lat, lon)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))

        elif path == "/api/clear":
            stop_simulation()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # подавляем лишний лог запросов
        pass


def main():
    print("=" * 60)
    print("   mkusha - Подмена геопозиции iPhone (PC Edition)")
    print("   Работает БЕЗ Apple ID, БЕЗ паролей, БЕЗ Sideloadly!")
    print("=" * 60)
    print()
    log(f"Запускаю сервер на http://localhost:{PORT}")
    
    # Открываем браузер автоматически через 1 секунду
    threading.Thread(target=lambda: (time.sleep(1), webbrowser.open(f"http://localhost:{PORT}")), daemon=True).start()

    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        log("Сервер готов! Открываю интерактивную карту в браузере...")
        log("Для выхода нажмите Ctrl+C")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            stop_simulation()
            log("Завершение работы.")


if __name__ == "__main__":
    main()
