import random
import socket
import sys
import _thread
import json
import os
from time import sleep

PORT = 12345

node = {
    "id": None,
    "ip": sys.argv[1],
    "id_antecessor": None,
    "ip_antecessor": None,
    "id_sucessor": None,
    "ip_sucessor": None
}

#--"Telas"--
def informacoesDoNo():
    informacoes_do_no = f"""
            ID:             {node['id']}
            IP:             {node["ip"]}
            ID_SUCESSOR:    {node['id_sucessor']}
            IP_SUCESSOR:    {node['ip_sucessor']}
            ID_ANTECESSOR:  {node['id_antecessor']}
            IP_ANTECESSOR:  {node['ip_antecessor']}
    """
    print(informacoes_do_no)

def menu():
    print("---------------------:---------------------")
    print("| 1 |  Iniciar nova rede P2P              |")
    print("| 2 |  Entrar em uma rede P2P             |")
    print("| 3 |  Sair da rede P2P                   |")
    print("| 4 |  Mostrar informacoes do No          |")
    print("| 5 |  Sair da aplicacao                  |")
    print("---------------------:---------------------")

#--Thread--
def servidor(udp):
    print(f"Starting UDP Server on port {PORT}")
    while True:
        msg, cliente = udp.recvfrom(1024)
        msg_decoded = msg
        data_converted = json.loads(msg_decoded)

        codigo = data_converted['codigo']
        if   codigo == 0:
            joinResp(udp, cliente)

        elif codigo == 1:
            identificador   = data_converted['identificador'] 
            id_sucessor     = data_converted['id_sucessor']
            ip_sucessor     = data_converted['ip_sucessor']   
            id_antecessor   = data_converted['id_antecessor']
            ip_antecessor   = data_converted['ip_antecessor']  

            if(ip_sucessor == node['ip']):
                node['ip_antecessor'] = ip_antecessor
                node['id_antecessor'] = id_antecessor
            elif ip_antecessor == node['ip']:
                node['ip_sucessor'] = ip_sucessor
                node['id_sucessor'] = id_sucessor
            
            leaveResp(udp, cliente)

        elif codigo == 2:            
            identificador   = data_converted['identificador']       
            ip_origem_busca = data_converted['ip_origem_busca']     
            id_busca        = data_converted['id_busca']            

            if id_busca < node['id'] and id_busca > node['id_antecessor']:          
                lookupResp(udp, ip_origem_busca, id_busca)
            else:
                if node['id'] <= node['id_antecessor'] and (id_busca > node['id_antecessor'] or id_busca < node['id']):
                    lookupResp(udp, ip_origem_busca, id_busca)
                else:
                    lookup(udp, node['ip_sucessor'], ip_origem_busca, id_busca)

        elif codigo == 3:
            id_novo_sucessor = data_converted['id_novo_sucessor']
            ip_novo_sucessor = data_converted['ip_novo_sucessor']
            identificador    = data_converted['identificador']

            if identificador == 1:
                node['id_antecessor'] = id_novo_sucessor
                node['ip_antecessor'] = ip_novo_sucessor

            elif identificador == 2:
                node['id_sucessor']   = id_novo_sucessor
                node['ip_sucessor']   = ip_novo_sucessor
            
            updateResp(udp, ip_novo_sucessor)

        elif codigo == 64:  #Join
            id_sucessor     = data_converted['id_sucessor']
            ip_sucessor     = data_converted['ip_sucessor']
            id_antecessor   = data_converted['id_antecessor']
            ip_antecessor   = data_converted['ip_antecessor']

            node['id_antecessor']   = id_antecessor
            node['ip_antecessor']   = ip_antecessor
            node['id_sucessor']     = id_sucessor
            node['ip_sucessor']     = ip_sucessor
            
            print("Você entrou na Rede!")
            update(udp, node['ip_sucessor']     , 1)
            update(udp, node['ip_antecessor']   , 2)

        elif codigo == 65:  #Leave
            identificador = data_converted['identificador']
            if identificador == node['id_sucessor']:
                print("Você saiu da Rede!")

        elif codigo == 66:  #Lookup
            id_busca    = data_converted['id_busca']     
            id_origem   = data_converted['id_origem']   
            ip_origem   = data_converted['ip_origem']   
            id_sucessor = data_converted['id_sucessor'] 
            ip_sucessor = data_converted['ip_sucessor']

            join(udp, ip_origem)
        
        elif codigo == 67:  #Update
            id_origem_mensagem = data_converted['id_origem_mensagem']
            if id_origem_mensagem ==  node['id_sucessor']:
                print("Update realiado!")
  
#--Funções Msg--
def join(udp, ip):
    mensagem = {}
    mensagem['codigo']     = 0
    mensagem['id']         = node["id"]

    print("--> Join: \t", ip)
    sendMsg(udp, ip, mensagem)
    
def joinResp(udp, ip):
    mensagem = {}
    mensagem['codigo']          = 64
    mensagem['id_sucessor']     = node['id']
    mensagem['ip_sucessor']     = node['ip']
    mensagem['id_antecessor']   = node['id_antecessor']
    mensagem['ip_antecessor']   = node['ip_antecessor']

    print("<-- Join\t", ip[0])
    msg_json = json.dumps(mensagem)
    udp.sendto(msg_json.encode('utf-8'), ip)

def leave(udp):
    mensagem = {}
    mensagem['codigo']          = 1
    mensagem['identificador']   = node['id']
    mensagem['id_sucessor']     = node['id_sucessor']
    mensagem['ip_sucessor']     = node['ip_sucessor']
    mensagem['id_antecessor']   = node['id_antecessor']
    mensagem['ip_antecessor']   = node['ip_antecessor']

    print("--> Leave \t", node['ip_sucessor'])
    print("--> Leave \t", node['ip_antecessor'])
    sendMsg(udp, node['ip_sucessor'], mensagem);
    sendMsg(udp, node['ip_antecessor'], mensagem);

def leaveResp(udp, ip):
    mensagem = {}
    mensagem['codigo']          = 65
    mensagem['identificador']   = node['id']

    print("<-- Leave \t", ip[0])
    msg_json = json.dumps(mensagem)
    udp.sendto(msg_json.encode('utf-8'), ip)    

def lookup(udp, ip, ip_origem, id_busca):
    mensagem = {}
    mensagem['codigo']          = 2
    mensagem['identificador']   = node['id']
    mensagem['ip_origem_busca'] = ip_origem
    mensagem['id_busca']        = id_busca
    
    print("--> Lookup \t", ip)
    sendMsg(udp, ip, mensagem)
    
def lookupResp(udp, ip, id_busca):
    mensagem = {}
    mensagem['codigo']       = 66
    mensagem['id_busca']     = id_busca
    mensagem['id_origem']    = node['id']
    mensagem['ip_origem']    = node['ip']
    mensagem['id_sucessor']  = node['id_sucessor']
    mensagem['ip_sucessor']  = node['ip_sucessor']
    
    print("<-- Lookup \t", ip)
    sendMsg(udp, ip, mensagem)

def update(udp, ip, x):          
    mensagem = {}
    mensagem['codigo']              = 3
    mensagem['id_novo_sucessor']    = node['id'] 
    mensagem['ip_novo_sucessor']    = node['ip']

    if x == 1:
        mensagem['identificador']   = 1
    elif x == 2:
        mensagem['identificador']   = 2
        
    print("--> Update \t", ip)
    sendMsg(udp, ip, mensagem)

def updateResp(udp, ip):
    mensagem = {}
    mensagem['codigo']              = 67
    mensagem['id_origem_mensagem']  = node['id']
   
    print("<-- Update \t", ip)
    sendMsg(udp, ip, mensagem)

def sendMsg(udp, ip, mensagem):
    dest = (ip, PORT)
    msg_json = json.dumps(mensagem)
    udp.sendto(msg_json.encode('utf-8'), dest)


def main():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("", PORT))    
    _thread.start_new_thread(servidor, (udp,))
    sleep(2)
    
    node['id'] = random.randrange(1, 1000)
    #node['id'] = input("Informe id: ")
     
    opc = None
    while opc != "5":
        os.system('clear') or None
        menu()
        opc = input("Informe uma opcao: \n")

        if opc == "1":      #Criar nova rede
            node['id_antecessor']   = node['id']
            node['id_sucessor']     = node['id']
            node['ip_antecessor']   = node['ip']
            node['ip_sucessor']     = node['ip']

            print("Rede criada!")

        elif opc == "2":    #Entra em uma rede
            ip = input("Informe o IP do Host: ")
            lookup(udp, ip, node['ip'], node['id'])
        
        elif opc == "3":    #Sair da rede
            leave(udp)    

        elif opc == "4":    #Informações
            informacoesDoNo()
        
        elif opc == "5":    #Sair
            udp.close()
            exit()
        
        sleep(1)
        input("Pressione ENTER para continuar!\n")


if __name__ == "__main__":
    main()