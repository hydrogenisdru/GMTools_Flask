from gmCmdPro_pb2 import *

msg = dict()
msg[GmOnlineNtf] = 10108

msg[PullSystemMailNtf] = 10109

msg[GmNoticeNtf] = 10110

msg[KickPlayerNtf] = 10111

msg[PullAnnouncementNtf] = 10113

msg[UpdatePatchNtf] = 10114

msg[PullActivityConfigNtf] = 10115


class Server2ServerProtocolProvider:
    def __init__(self, msg_dict=msg):
        self.msg_dict = msg_dict

    def parse(self, id, data):
        if id == 10108:
            return GmOnlineNtf().ParseFromString(data)

        if id == 10109:
            return PullSystemMailNtf().ParseFromString(data)

        if id == 10110:
            return GmNoticeNtf().ParseFromString(data)

        if id == 10111:
            return KickPlayerNtf().ParseFromString(data)

        if id == 10113:
            return PullAnnouncementNtf().ParseFromString(data)

        if id == 10114:
            return UpdatePatchNtf().ParseFromString(data)

        if id == 10115:
            return PullActivityConfigNtf().ParseFromString(data)
