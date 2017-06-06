import Server2ServerProtocolProvider

@staticmethod
def encode(msg_id, data):
    buf = bytearray(2 + data.__len__)
    buf.append(buffer(msg_id))
    buf.append(data)
    return buf

# def decode(buf):
#     id = buf