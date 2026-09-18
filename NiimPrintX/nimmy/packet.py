from devtools import debug


def packet_to_int(x):
    return int.from_bytes(x.data, "big")


class NiimbotPacket:
    # Connect (0xC1) is the only command whose frame is prefixed with 0x03.
    CONNECT = 0xC1

    def __init__(self, type_, data):
        self.type = type_
        self.data = data

    @classmethod
    def from_bytes(cls, pkt):
        assert pkt[:2] == b"\x55\x55"
        assert pkt[-2:] == b"\xaa\xaa"
        type_ = pkt[2]
        len_ = pkt[3]
        data = pkt[4 : 4 + len_]

        checksum = type_ ^ len_
        for i in data:
            checksum ^= i
        assert checksum == pkt[-3]

        return cls(type_, data)

    def to_bytes(self):
        checksum = self.type ^ len(self.data)
        for i in self.data:
            checksum ^= i
        packet = bytes(
            (0x55, 0x55, self.type, len(self.data), *self.data, checksum, 0xAA, 0xAA)
        )
        if self.type == self.CONNECT:
            # The Connect request is the only packet that carries a 0x03 prefix
            # before the standard 0x55 0x55 header.
            return b"\x03" + packet
        return packet

    def __repr__(self):
        return f"<NiimbotPacket type={self.type} data={self.data}>"