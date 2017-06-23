import binascii


@staticmethod
def encode(msg_id, data):
    hex_id = '{0:04x}'.format(msg_id)
    buf = binascii.unhexlify(hex_id) + data
    return buf


# @staticmethod
# def decode(buf):
