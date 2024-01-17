from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST = 'localhost'
PORT = 8000
STATS_PORT = 8001
DATA_FILE = 'server_data.json'

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Lese die Anzahl der Aufrufe aus der Datei
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)
                aufrufe = data['aufrufe']

            # Aktualisiere die Anzahl der Aufrufe und speichere sie in der Datei
            data['aufrufe'] += 1
            with open(DATA_FILE, 'w') as file:
                json.dump(data, file)

            # Erstelle die HTML-Antwort mit der aktuellen Anzahl der Aufrufe
            with open('server.html','rb') as file:
                html = file.read()

            self.wfile.write(html)

            # Lese das Histogramm aus der Datei
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)
                histogramm = data['histogramm']

            # Aktualisiere das Histogramm basierend auf dem User-Agent des anfragenden Browsers
            user_agent = self.headers.get('User-Agent')
            histogramm[user_agent] = histogramm.get(user_agent, 0) + 1
            with open(DATA_FILE, 'w') as file:
                json.dump(data, file)

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('404 Not Found'.encode())

class StatsRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Lese das Histogramm aus der Datei
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)
                histogramm = data['histogramm']

            # Sende das Histogramm als JSON-Antwort
            self.wfile.write(json.dumps(histogramm).encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('404 Not Found'.encode())

def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Server läuft auf http://{HOST}:{PORT}')

    stats_server_address = (HOST, STATS_PORT)
    stats_httpd = HTTPServer(stats_server_address, StatsRequestHandler)
    print(f'Statistik-Server läuft auf http://{HOST}:{STATS_PORT}')

    # Initialisiere die Daten-Datei, falls sie nicht vorhanden ist
    try:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {
            'aufrufe': 0,
            'histogramm': {}
        }
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file)

    # Starte den Server und den Statistik-Server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print('Server gestoppt.')

    try:
        stats_httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    stats_httpd.server_close()
    print('Statistik-Server gestoppt.')

if __name__ == '__main__':
    run_server()
