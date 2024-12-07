import socketserver

# Настройки для UDP-сервера
UDP_IP = "239.192.43.78"
UDP_PORT = 43789
BUFFER_SIZE = 1024  # Размер буфера для чтения данных
NUM_PACKETS = 10000  # Максимальное количество пакетов для приема

# Обработчик запросов
class UDPRequestHandler(socketserver.BaseRequestHandler):
    packet_count = 0  # Счетчик принятых пакетов

    def handle(self):
        if UDPRequestHandler.packet_count < NUM_PACKETS:
            data = self.request[0].strip()
            socket = self.request[1]
            print(f"Received packet from {self.client_address}")

            # Запись данных в файл
            with open('udp_dump.txt', 'ab') as file:
                file.write(data)

            # Увеличение счетчика пакетов
            UDPRequestHandler.packet_count += 1
        else:
            print("Достигнуто максимальное количество пакетов. Сервер завершает работу.")
            self.server.shutdown()

# Создание и запуск сервера
class UDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

if __name__ == "__main__":
    with UDPServer((UDP_IP, UDP_PORT), UDPRequestHandler) as server:
        print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")
        server.serve_forever()
