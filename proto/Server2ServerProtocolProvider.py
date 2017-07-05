from gmCmdPro_pb2 import *

msg = dict()
msg[GmOnlineNtf] = 10108

msg[PullSystemMailNtf] = 10109

msg[GmNoticeNtf] = 10110

msg[KickPlayerNtf] = 10111

msg[PullActivityConfigNtf] = 10112

msg[PullAnnouncementNtf] = 10113

# msg[S2SPayFeedBackAck] = 10114
#
# msg[S2SPayFeedBackNtf] = 10115
#
# msg[S2SPayFeedBackReq] = 10116

msg[UpdatePatchNtf] = 10117


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

        if id == 10112:
            return PullActivityConfigNtf().ParseFromString(data)

        if id == 10113:
            return PullAnnouncementNtf().ParseFromString(data)

        # if id == 10114:
        #     return S2SPayFeedBackAck().ParseFromString(data)
        #
        # if id == 10115:
        #     return S2SPayFeedBackNtf().ParseFromString(data)
        #
        # if id == 10116:
        #     return S2SPayFeedBackReq().ParseFromString(data)

        if id == 10117:
            return UpdatePatchNtf().ParseFromString(data)
