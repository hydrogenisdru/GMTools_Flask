import stomp
import datetime


class MyListener(object):
    def on_error(self, headers, message):
        print('received an error %s' % message)

    def on_message(self, headers, message):
        print('received a message %s' % message)


class SimpleMqAdaptor:
    def __init__(self, ip_address, port=61613):
        self.conn = stomp.Connection10([(ip_address, port)])
        self.conn.set_listener('MyListener', MyListener())
        self.conn.start()
        self.conn.connect()

    def stop(self):
        self.conn.disconnect()
        self.conn.stop()

    def subscribe(self, topic):
        self.conn.subscribe(destination=topic, id=1, ack='auto')

    def send(self, message, destination):
        self.conn.send(body=message, destination=destination)

    def get_listener(self):
        if self.conn.get_listener('MyListener'):
            return self.conn.get_listener('MyListener')
        else:
            return None
