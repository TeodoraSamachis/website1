import socket
import os  # pentru dimensiunea fisierului
import gzip
import json
import threading

def handle_client(clientsocket):


    print('S-a conectat un client.')
    # se proceseaza cererea si se citeste prima linie de text
    cerere = ''
    linieDeStart = ''
    while True:
        buf = clientsocket.recv(1024)
        if len(buf) < 1:
            break
        cerere = cerere + buf.decode()
        print('S-a citit mesajul: \n---------------------------\n' + cerere + '\n---------------------------')
        pozitie = cerere.find('\r\n')
        if (pozitie > -1 and linieDeStart == ''):
            linieDeStart = cerere[0:pozitie]
            print('S-a citit linia de start din cerere: ##### ' + linieDeStart + ' #####')
            break
    print('S-a terminat cititrea.')
    if linieDeStart == '':
        clientsocket.close()
        print('S-a terminat comunicarea cu clientul - nu s-a primit niciun mesaj.')

    else:
        # interpretarea sirului de caractere `linieDeStart`
        elementeLineDeStart = linieDeStart.split()
        # TODO securizare
        numeResursaCeruta = elementeLineDeStart[1]
        if numeResursaCeruta == '/':
            numeResursaCeruta = '/index.html'
        print(linieDeStart)
        if linieDeStart.startswith('POST'):
            # Parsare continut cerere
                    print("cerere post")
                    pozitie = cerere.find('\r\n\r\n')
                    continut = cerere[pozitie+4:]
                    elemente = continut.split('&')
                    cerere_dict = {}
                    for element in elemente:
                        cheie_valoare = element.split('=')
                        cerere_dict[cheie_valoare[0]] = cheie_valoare[1]

                    # Creare obiect JSON cu numele de utilizator si parola
                    username = cerere_dict['username']
                    password = cerere_dict['password']
                    obj_json = {'utilizator': username, 'parola': password}

                     # Citire lista utilizatori din fisier
                    with open('../continut/resurse/utilizatori.json', 'r') as afile:
                        lista_utilizatori = json.load(afile)

                    # Adaugare noul utilizator in lista
                    lista_utilizatori.append(obj_json)

                    # Scriere lista actualizata de utilizatori in fisier
                    with open('../continut/resurse/utilizatori.json', 'w') as afile:
                        json.dump(lista_utilizatori, afile)

                    # Trimitere raspuns
                    raspuns = 'HTTP/1.1 302 Found\r\nLocation:/index.html\r\n\r\n'
                    clientsocket.sendall(raspuns.encode())
                    clientsocket.close()
        else:
            # calea este relativa la directorul de unde a fost executat scriptul
            numeFisier = '../continut' + numeResursaCeruta
            print("Numele fisierului"+numeFisier)

            fisier = None
            try:
                # deschide fisierul pentru citire in mod binar
                fisier = open(numeFisier, 'rb')

                # tip media
                numeExtensie = numeFisier[numeFisier.rfind('.') + 1:]
                tipuriMedia = {
                    'html': 'text/html; charset=utf-8',
                    'css': 'text/css; charset=utf-',
                    'js': 'text/javascript; charset=utf-8',
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'gif': 'image/gif',
                    'ico': 'image/x-icon',
                    'xml': 'application/xml; charset=utf-8',
                    'json': 'application/json; charset=utf-8'
                }
                tipMedia = tipuriMedia.get(numeExtensie, 'text/plain; charset=utf-8')

                # se trimite raspunsul
                clientsocket.sendall('HTTP/1.1 200 OK\r\n'.encode());
                clientsocket.sendall(('Content-Length: ' + str(os.stat(numeFisier).st_size) + '\r\n').encode());
                clientsocket.sendall(('Content-Type: ' + tipMedia + '\r\n').encode());
                clientsocket.sendall('Server: My PW Server\r\n'.encode());
                clientsocket.sendall('\r\n'.encode());

                # citeste din fisier si trimite la server
                buf = fisier.read(1024)
                while (buf):
                    clientsocket.send(buf)
                    buf = fisier.read(1024)
            except IOError:
                # daca fisierul nu exista trebuie trimis un mesaj de 404 Not Found
                msg = 'Eroare! Resursa ceruta ' + numeResursaCeruta + ' nu a putut fi gasita!'
                print(msg)
                clientsocket.sendall('HTTP/1.1 404 Not Found\r\n'.encode());
                clientsocket.sendall(('Content-Length: ' + str(len(msg.encode('utf-8'))) + '\r\n').encode());
                clientsocket.sendall('Content-Type: text/plain; charset=utf-8\r\n'.encode());
                clientsocket.sendall('Server: My PW Server\r\n'.encode());
                clientsocket.sendall('\r\n'.encode());
                clientsocket.sendall(msg.encode());

            finally:
                if fisier is not None:
                    fisier.close()
            clientsocket.close()
            print('S-a terminat comunicarea cu clientul.')

def start_server():
    # creeaza un server socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # specifica ca serverul va rula pe portul 5678, accesibil de pe orice ip al serverului
    serversocket.bind(('', 5678))
    # serverul poate accepta conexiuni; specifica cati clienti pot astepta la coada
    serversocket.listen(5)
    print('#########################################################################')
    print('Serverul asculta potentiali clienti.')
    # asteapta conectarea unui client la server
    # metoda `accept` este blocanta => clientsocket, care reprezinta socket-ul corespunzator clientului conectat
    (clientsocket, address) = serversocket.accept()

    while True:
        # asteapta conexiunea clientului
        # metoda accept este blocanta
        (clientsocket, address) = serversocket.accept()

        # tratarea cererii clientului intr-un fir de executie separat
        client_thread = threading.Thread(target=handle_client, args=(clientsocket,))
        client_thread.start()

start_server()

