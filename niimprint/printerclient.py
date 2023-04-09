import niimbotpacket
import socket
import struct
import time
import enum

class InfoEnum(enum.IntEnum):
    DENSITY = 1
    PRINTSPEED = 2
    LABELTYPE = 3
    LANGUAGETYPE = 6
    AUTOSHUTDOWNTIME = 7
    DEVICETYPE = 8
    SOFTVERSION = 9
    BATTERY = 10
    DEVICESERIAL = 11
    HARDVERSION = 12

class RequestCodeEnum(enum.IntEnum):
    GET_INFO = 64
    GET_RFID = 26
    HEARTBEAT = 220
    SET_LABEL_TYPE = 35
    SET_LABEL_DENSITY = 33
    START_PRINT = 1
    END_PRINT = 243
    START_PAGE_PRINT = 3
    END_PAGE_PRINT = 227
    ALLOW_PRINT_CLEAR = 32
    SET_DIMENSION = 19
    SET_QUANTITY = 21
    GET_PRINT_STATUS = 163

_packet_to_int = lambda x: int.from_bytes(x.data, 'big')

# TODO REMOVE MAGIC NUMBER
class PrinterClient:
    def __init__(self, address):
        self._sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self._sock.connect((address, 1))
        self._packetbuf = bytearray()

    def _recv(self):
        packets = []
        self._packetbuf.extend(self._sock.recv(1024))
        while len(self._packetbuf) > 4:
            pkt_len = self._packetbuf[3] + 7
            if len(self._packetbuf) >= pkt_len:
                packet = niimbotpacket.NiimbotPacket.from_bytes(self._packetbuf[:pkt_len])
                # print('recv:',packet)
                packets.append(packet)
                del self._packetbuf[:pkt_len]
        return packets

    def _send(self, packet):
        # print('send:',packet)
        self._sock.send(packet.to_bytes())

    def _transceive(self, reqcode, data, respoffset=1):
        respcode = respoffset + reqcode
        self._send(niimbotpacket.NiimbotPacket(reqcode, data))
        resp = None
        for _ in range(6):
            for packet in self._recv():
                if packet.type == 219:
                    raise ValueError
                elif packet.type == 0:
                    raise NotImplementedError
                elif packet.type == respcode:
                    resp = packet
            if resp:
                return resp
            time.sleep(0.1)
        return resp

    def get_info(self, key):
        if packet := self._transceive(RequestCodeEnum.GET_INFO, bytes((key,)), key):
            match key:
                case InfoEnum.DEVICESERIAL:
                    return packet.data.hex()
                case InfoEnum.SOFTVERSION:
                    return _packet_to_int(packet) / 100
                case InfoEnum.HARDVERSION:
                    return _packet_to_int(packet) / 100
                case _:
                    return _packet_to_int(packet)
        else:
            return None

    def get_rfid(self):
        packet = self._transceive(RequestCodeEnum.GET_RFID, b'\x01')
        data = packet.data

        if data[0] == 0:
            return None
        uuid = data[0:8].hex()
        idx = 8

        barcode_len = data[idx]
        idx += 1
        barcode = data[idx:idx+barcode_len].decode()

        idx += barcode_len
        serial_len = data[idx]
        idx += 1
        serial = data[idx:idx+serial_len].decode()

        idx += serial_len
        total_len, used_len, type_ = struct.unpack('>HHB', data[idx:])
        return {
            'uuid': uuid,
            'barcode': barcode,
            'serial': serial,
            'used_len': used_len,
            'total_len': total_len,
            'type': type_
        }

    def heartbeat(self):
        packet = self._transceive(RequestCodeEnum.HEARTBEAT, b'\x01')
        closingstate = None
        powerlevel = None
        paperstate = None
        rfidreadstate = None

        match len(packet.data):
            case 20:
                paperstate = packet.data[18]
                rfidreadstate = packet.data[19]
            case 13:
                closingstate = packet.data[9]
                powerlevel = packet.data[10]
                paperstate = packet.data[11]
                rfidreadstate = packet.data[12]
            case 19:
                closingstate = packet.data[15]
                powerlevel = packet.data[16]
                paperstate = packet.data[17]
                rfidreadstate = packet.data[18]
            case 10:
                closingstate = packet.data[8]
                powerlevel = packet.data[9]
                rfidreadstate = packet.data[8]
            case 9:
                closingstate = packet.data[8]

        return {
            'closingstate': closingstate,
            'powerlevel': powerlevel,
            'paperstate': paperstate,
            'rfidreadstate': rfidreadstate
        }

    def set_label_type(self, n):
        assert 1 <= n <= 3
        packet = self._transceive(RequestCodeEnum.SET_LABEL_TYPE, bytes((n,)), 16)
        return bool(packet.data[0])

    def set_label_density(self, n):
        assert 1 <= n <= 3
        packet = self._transceive(RequestCodeEnum.SET_LABEL_DENSITY, bytes((n,)), 16)
        return bool(packet.data[0])

    def start_print(self):
        packet = self._transceive(RequestCodeEnum.START_PRINT, b'\x01')
        return bool(packet.data[0])

    def end_print(self):
        packet = self._transceive(RequestCodeEnum.END_PRINT, b'\x01')
        return bool(packet.data[0])

    def start_page_print(self):
        packet = self._transceive(RequestCodeEnum.START_PAGE_PRINT, b'\x01')
        return bool(packet.data[0])

    def end_page_print(self):
        packet = self._transceive(RequestCodeEnum.END_PAGE_PRINT, b'\x01')
        return bool(packet.data[0])

    def allow_print_clear(self):
        packet = self._transceive(RequestCodeEnum.ALLOW_PRINT_CLEAR, b'\x01', 16)
        return bool(packet.data[0])

    def set_dimension(self, w, h):
        packet = self._transceive(RequestCodeEnum.SET_DIMENSION, struct.pack('>HH', w, h))
        return bool(packet.data[0])

    def set_quantity(self, n):
        packet = self._transceive(RequestCodeEnum.SET_QUANTITY, struct.pack('>H', n))
        return bool(packet.data[0])

    def get_print_status(self):
        packet = self._transceive(RequestCodeEnum.GET_PRINT_STATUS, b'\x01', 16)
        page, progress1, progress2 = struct.unpack('>HBB', packet.data)
        return {'page': page, 'progress1': progress1, 'progress2': progress2}
