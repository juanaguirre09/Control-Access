# adafruit_fingerprint.py
# MicroPython port básico del Adafruit_Fingerprint Arduino Library para AS608

import time
from machine import UART

# Al inicio, junto a tus constantes:
PACKET_COMMAND = 0x01
PACKET_DATA    = 0x02
FINGERPRINT_OK = 0x00
DOWN_CHAR      = 0x09




class AdafruitFingerprint:
    def __init__(self, uart: UART, password: int = 0x0000):
        self.uart = uart
        self.password = password

    def _send_packet(self, packet_type: int, payload: bytes):
        # Cabecera
        pkt = bytearray(b'\xEF\x01')              # Start code
        pkt += b'\xFF\xFF\xFF\xFF'                # Address (default)
        pkt += bytes([packet_type])               # Packet type
        length = len(payload) + 2
        pkt += bytes([length >> 8, length & 0xFF]) # Length hi, lo
        pkt += payload                            # Payload
        checksum = packet_type + (length >> 8) + (length & 0xFF) + sum(payload)
        checksum &= 0xFFFF
        pkt += bytes([checksum >> 8, checksum & 0xFF])
        self.uart.write(pkt)

    def _read_packet(self, timeout=5000):
        deadline = time.ticks_ms() + timeout
        # Leer encabezado de 9 bytes
        header = b''
        while time.ticks_ms() < deadline and len(header) < 9:
            c = self.uart.read(1)
            if c:
                header += c
        if len(header) < 9 or header[6] != 0x07:
            return None
        length = (header[7] << 8) | header[8]
        # Leer payload + checksum
        body = b''
        while time.ticks_ms() < deadline and len(body) < length:
            c = self.uart.read(1)
            if c:
                body += c
        if len(body) < length:
            return None
        return body

    def verify_password(self) -> bool:
        # Comando 0x13 + contraseña de 4 bytes (32 bits)
        pw_bytes = self.password.to_bytes(4, 'big')   # e.g. b'\x00\x00\x00\x00'
        payload  = b'\x13' + pw_bytes                 # [CMD_VERIFYPW | PW3 | PW2 | PW1 | PW0]
        self._send_packet(0x01, payload)
        resp = self._read_packet()
        return bool(resp and resp[0] == 0x00)

    def get_image(self) -> int:
        # Comando 0x01
        self._send_packet(0x01, b'\x01')
        resp = self._read_packet()
        return resp[0] if resp else -1

    def image2Tz(self, slot: int) -> int:
        # Comando 0x02
        self._send_packet(0x01, b'\x02' + bytes([slot]))
        resp = self._read_packet()
        return resp[0] if resp else -1

    def create_model(self) -> int:
        # Comando 0x05
        self._send_packet(0x01, b'\x05')
        resp = self._read_packet()
        return resp[0] if resp else -1

    def store_model(self, location: int, buffer_id: int = 1) -> int:
        """
        Guarda la plantilla que hay en buffer_id (1 o 2) en la posición 'location'.
        payload = [0x06, buffer_id, pageID_H, pageID_L]
        """
        payload = bytes([0x06,
                         buffer_id,
                         (location >> 8) & 0xFF,
                         location & 0xFF])
        self._send_packet(0x01, payload)
        resp = self._read_packet()
        return resp[0] if resp else -1


    def search(self, start_page: int = 0, page_num: int = 10) -> int:
        # Comando 0x04: busca en [start_page, start_page+page_num)
        payload = b'\x04' + bytes([1,
                                   (start_page >> 8) & 0xFF,
                                   start_page & 0xFF,
                                   (page_num >> 8) & 0xFF,
                                   page_num & 0xFF])
        self._send_packet(0x01, payload)
        resp = self._read_packet()
        if resp and resp[0] == 0x00:
            self.finger_id   = (resp[1] << 8) | resp[2]
            self.confidence = (resp[3] << 8) | resp[4]
        return resp[0] if resp else -1

    def delete_model(self, location: int) -> int:
        """
        Borra la plantilla en la ranura `location`.
        CMD = 0x0C, payload = [0x0C, P1, P2]
        """
        # construye y envía el paquete
        payload = bytes([0x0C, (location >> 8) & 0xFF, location & 0xFF])
        self._send_packet(0x01, payload)
        resp = self._read_packet()
        return resp[0] if resp else -1

    def empty_library(self) -> int:
        """
        Borra TODAS las plantillas de la base de datos.
        CMD = 0x0D, payload = [0x0D]
        """
        self._send_packet(0x01, b'\x0D')
        resp = self._read_packet()
        return resp[0] if resp else -1
    
    # Dentro de tu clase AdafruitFingerprint:
    def download_char(self, buffer_id: int, char_data: bytes) -> bool:
        # 1) instrucción DOWNLOAD_CHAR + buffer
        self._send_packet(PACKET_COMMAND, bytes([DOWN_CHAR, buffer_id]))
        resp = self._read_packet()
        if not resp or resp[0] != FINGERPRINT_OK:
            return False

        # 2) enviar todos los chunks de hasta 128 bytes
        for i in range(0, len(char_data), 128):
            chunk = char_data[i : i + 128]
            self._send_packet(PACKET_DATA, chunk)

        # 3) fin de datos
        self._send_packet(PACKET_DATA, b"")

        # 4) ACK final
        resp = self._read_packet()
        return bool(resp and resp[0] == FINGERPRINT_OK)
