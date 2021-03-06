import socket
import sys
import _thread

HOST = sys.argv[1] 
PORT = 5000  


def server(udp):
    print(f"Starting UDP Server on port {PORT}")
    while True:
        msg, cliente = udp.recvfrom(1024)
        msg_decoded = msg.decode('utf-8')
        
        namehost = msg_decoded.split(",")[0]
        msghost = msg_decoded.split(",")[1]

        print(f"\t" + namehost + " <- " + msghost)
        

def client():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    orig = ("", PORT)
    dest = (HOST, PORT)
    udp.bind(orig)
    _thread.start_new_thread(server, (udp,))
    print("Type q to exit")
    message = None
    
    from time import sleep
    sleep(0.2)

    name = None
    name = input("Informe nome do Host: ")
    message = "conectar," + name
    udp.sendto(message.encode("utf-8"), dest)

    while message != "q":
        if sys.version_info.major == 3:
            message = input("-> ")
        else:
            message = raw_input("-> ")

        message = "enviarMensagem," + name + "," + message
        udp.sendto(message.encode("utf-8"), dest)
    udp.close()


if __name__ == "__main__":
    client()
