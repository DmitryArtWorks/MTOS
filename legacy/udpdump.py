# обработка буфера сетевых кадров должна идти быстрее, чем формируются сами кадры по сети

import socket  # we use the socket module that comes with python3
import struct
import pickle 
import numpy

MCAST_GRP = '239.192.43.78'
MCAST_PORT = 43789
IS_ALL_GROUPS = True

data = []

if __name__ == '__main__':
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if IS_ALL_GROUPS:
            # on this port, receive all multicast groups
            sock.bind(('', MCAST_PORT))
        else:
            # on this port listen ONLY to MCAST_GRP
            sock.bind((MCAST_GRP, MCAST_PORT))

        mreq = struct.pack("4sl",socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            rec_bytes = sock.recv(1197) # 4131 - кол-во байт в одном пакете
            msg = bytearray(rec_bytes)
                    
            scan = {}
            i020 = struct.unpack('>I', msg[8:12])
            i040_041 = struct.unpack('>HHII', msg[12:24]) # интерпретация байтов в слово какое-нибудь, в си - юнион, HHII - относительно сразу нескольких чисел, i020 и.тд. описание полей в астерикс формате
            i051 = struct.unpack('>B', msg[31:32])
            i051_data = struct.unpack('>'+'B'*64*i051[0], msg[32:(32+64*i051[0])]) # смещение в байтах 
            
            scan['ranges'] = numpy.array(list(i051_data))[:1024]       # одно зондирование                       
            scan['azimuth'] = (i040_041[0]+i040_041[0])/2 # angle in samples # код угла с которого пришло зондирование
            scan['scan_time'] = i020[0] # ms
            print(scan['azimuth'])

            
            data.append(scan.copy())
            
    except Exception as exc:
        print("Exception occured: ", exc)
        with open('D:\\test.pkl', 'wb') as f:
            pickle.dump(data, f)
        print('dump file created on exception ')

    except KeyboardInterrupt:
        with open('D:\\test.pkl', 'wb') as f:
            pickle.dump(data, f)
        print('dump file created on Ctrl+C event ')