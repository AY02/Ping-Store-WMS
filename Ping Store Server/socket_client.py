import socket, argparse

HOST_DEFAULT = '192.168.1.137'
PORT_DEFAULT = 10000
COMMANDS = {
    'quit_client': '!quit_client',
}

def send_message(cli, message):
    print(f'Invio il messaggio: ||{message}||...')
    cli.send(message.encode('utf-8'))
    print('Messaggio inviato')

def main(host, port, message=None):
    cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connessione a {host}:{port}...')
    cli.connect((host, port))
    print('Connessione effettuata')
    if message is not None: send_message(cli, message)
    while True:
        message = input('Inserisci cosa mandare al server --> ')
        if message == COMMANDS['quit_client']:
            print('Chiudo il socket...')
            cli.close()
            break
        send_message(cli, message)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Questo è un client tcp minimale che permette di inviare stringhe ad un server.')
    parser.add_argument('-i', '--host', help='Host della macchina del server')
    parser.add_argument('-p', '--port', help='Porta del servizio erogato dal server')
    parser.add_argument('-m', '--message', help='Inserisci il messaggio che vuoi inviare')

    args = parser.parse_args()
    host = args.host
    port = args.port

    if not host:
        host = HOST_DEFAULT
    if not port:
        port = PORT_DEFAULT
    else:
        port = int(port)
    
    main(host, port, args.message)
