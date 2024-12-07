import socketserver  # we use the socketsever module that comes with python3
import struct
import pickle 
import numpy


data = []

class UDPDump(socketserver.DatagramRequestHandler):
    
    def handle(self):
        rec_bytes = self.rfile.read(4131)
        msg = bytearray(rec_bytes)
                
        scan = {}
        i020 = struct.unpack('>I',msg[8:12])
        i040_041 = struct.unpack('>HHII',msg[12:24])
        i051 = struct.unpack('>B',msg[31:32])
        i051_data = struct.unpack('>'+'B'*64*i051[0],msg[32:(32+64*i051[0])])
        
        scan['ranges'] = numpy.array(list(i051_data))[:1024]  # Тип ДАННЫХ "СЛОВАРЬ". ПРОГУГЛИТЬ                            
        scan['azimuth'] = (i040_041[0]+i040_041[0])/2 # angle in samples
        scan['scan_time'] = i020[0] # ms
        print(scan['azimuth'])
        data.append(scan.copy())

# this is the main entrypoint
if __name__ == '__main__':
    try:
        # we specify the address and port we want to listen on
        listen_addr = ('0.0.0.0', 43789)

        # with allowing to reuse the address we dont get into problems running it consecutively sometimes
        socketserver.UDPServer.allow_reuse_address = True 

        # register our class
        serverUDP = socketserver.UDPServer(listen_addr, UDPDump)
        serverUDP.serve_forever()
        
    except:
        with open('data.pkl', 'wb') as f:
            pickle.dump(data, f)
        print('dump file created on interruption ')