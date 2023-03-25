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

class PrinterModel(enum.IntEnum):
    A8 = 1280
    B16 = 1792
    B203 = 2816
    B21_C2B = 771
    B21_C2B_ZX = 775
    B21_C2W = 772
    B21_C3W = 774
    B21_L2B = 769
    B21_L2W = 770
    B21_OLD = 768
    B32 = 2049
    B32_R = 2050
    B3S = 256
    B3S_ZX = 260
    D101 = 2560
    D110 = 2304
    D11 = 512
    D61 = 1536
    DT = 99
    DT_B11 = 51457
    DT_B50 = 51713
    DT_B50W = 51714
    DT_JCM_90 = 51461
    DT_S1 = 51458
    DT_S2 = 51459
    DT_S3 = 51460
    DT_T6 = 51715
    DT_T7 = 51716
    DT_T8 = 51717
    FUST = 513
    P1S = 1025
    P1 = 1024
    S6_1 = 258
    S6 = 257
    TSC = 255
    WK_GT100 = 55809
    XBY_T2 = 53249
    Z401 = 2051
    Z401_R = 2052
    ZP = 52993
    ZT_CL4NX = 57345
    ZT_CL6NX = 57601


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

    def _transceive(self, reqcode, data, respcode):
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
        if packet := self._transceive(64, bytes((key,)), 64+key):
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
        packet = self._transceive(26, b'\x01', 27)
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
        packet = self._transceive(220, b'\x01', 221)
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
        packet = self._transceive(35, bytes((n,)), 51)
        return bool(packet.data[0])

    def set_label_density(self, n):
        assert 1 <= n <= 3
        packet = self._transceive(33, bytes((n,)), 49)
        return bool(packet.data[0])

    def start_print(self):
        packet = self._transceive(1, b'\x01', 2)
        return bool(packet.data[0])

    def end_print(self):
        packet = self._transceive(243, b'\x01', 244)
        return bool(packet.data[0])

    def start_page_print(self):
        packet = self._transceive(3, b'\x01', 4)
        return bool(packet.data[0])

    def end_page_print(self):
        packet = self._transceive(227, b'\x01', 228)
        return bool(packet.data[0])

    def allow_print_clear(self):
        packet = self._transceive(32, b'\x01', 48)
        return bool(packet.data[0])

    def set_dimension(self, w, h):
        packet = self._transceive(19, struct.pack('>HH', w, h), 20)
        return bool(packet.data[0])

    def set_quantity(self, n):
        packet = self._transceive(21, struct.pack('>H', n), 22)
        return bool(packet.data[0])

    def get_print_status(self):
        packet = self._transceive(163, b'\x01', 179)
        page, progress1, progress2 = struct.unpack('>HBB', packet.data)
        return {'page': page, 'progress1': progress1, 'progress2': progress2}
