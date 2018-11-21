import socket, select
import struct
import os

class Server(object):
    def __init__(self):
        self.startup()
        
        CONNECTION_LIST = []
        PORT = 11001
            
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", PORT))
        server_socket.listen(10)
    
        CONNECTION_LIST.append(server_socket)
        print "Server bootup"
    
        while 1:
            read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
    
            for sock in read_sockets:
                if sock == server_socket:
                    sockfd, addr = server_socket.accept()
                    CONNECTION_LIST.append(sockfd)
                    print "Client connected"
                    
                else:
                    try:
                        data_raw = sock.recv(32)
                        self.write_handlers(data_raw)
                    except Exception as e:
                        print e
                        print "Client is offline"
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue
        server_socket.close()
    
    def startup(self):
        ROOT_PATH = '/sys/class/PWM/PWM'
        self.handlers = []
        cc = 0
        while cc < 4:
            fd_pr = os.open(ROOT_PATH + str(cc) + '/PERIOD', os.O_WRONLY)
            os.write(fd_pr, '4000')
            os.close(fd_pr)

            self.handlers.append(os.open(ROOT_PATH + str(cc) + '/DUTY', os.O_WRONLY))
            self.handlers.append(os.open(ROOT_PATH + str(cc) + '/ENABLE', os.O_WRONLY))
            os.write(self.handlers[(2*cc)], '0')
            cc = cc + 1
    
    def write_handlers(self, datapack):
        data_parse = struct.unpack('dddd', datapack)
        cc = 0
        while cc < 4:
            velVal = int(data_parse[cc] / 16 * 4000)
            dirVal = '0'
            if velVal > 0:
                dirVal = '3'
            if velVal < 0:
                dirVal = '2'
                velVal = -1*velVal
            if velVal == 0:
                dirVal = '0'

            os.write(self.handlers[(2*cc) + 1], dirVal)
            os.write(self.handlers[(2*cc)], str(velVal))

            cc = cc + 1

if __name__ == "__main__":
    s = Server()