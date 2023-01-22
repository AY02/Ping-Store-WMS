import os, socket, argparse
import shutil, psutil
import pyautogui as pag
from _thread import *

pag.PAUSE = 1

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST_DEFAULT = socket.gethostbyname(socket.gethostname())
PORT_DEFAULT = 10000

CHUNK_SIZE = 8192
BUFFER_SIZE = 1024

DEFAULT_FILENAME = 'import.csv'
BACKUP_FILENAME = 'backup.csv'
ADD_FILENAME = 'add.csv'
EDIT_FILENAME = 'edit.csv'
DUPLICATES_FILENAME = 'duplicates.csv'

N_THREAD = 0

LOGS = {
    'success': '!success',
    'failure': '!failure',
    'not_found': '!not_found',
    'ping': '!ping',
}

COMMANDS = {

    'quit_server': '!quit_server',

    'add': '!add',
    'edit': '!edit',
    'find': '!find',
    'remove': '!remove',

    'show_duplicate': '!show_duplicate',
    'delete_duplicate': '!delete_duplicate',
    'backup': '!backup',
    'update_database': '!update_database',

    'show_edit': '!show_edit',
    'show_add': '!show_add',
    'delete_edit': '!delete_edit',
    'delete_add': '!delete_add',

    'add_database': '!_add_database',
    'edit_main_server': '!_edit_main_server',
    'get_database_file': '!get_database_file',

}

def get_process(name):
    for proc in psutil.process_iter():
        if proc.name() == name:
            return proc
    return None

def get_merged_record(record):
    return ';'.join(record)

def get_merged_records(records):
    return [get_merged_record(record) for record in records]

def get_splitted_record(record):
    return record.split(';')

def get_splitted_records(records):
    return [get_splitted_record(record) for record in records]

def get_repeated_records(records):
    records = get_splitted_records(records)
    barcodes_count = {}
    for record in records:
        if record[0] in barcodes_count.keys():
            barcodes_count[record[0]] += 1
        else:
            barcodes_count[record[0]] = 1
    repeated_records = []
    for record in records:
        if barcodes_count[record[0]] > 1:
            repeated_records.append(record)
    repeated_records = get_merged_records(repeated_records)
    return repeated_records

def get_unique_records(records):
    records = get_splitted_records(records)
    unique_records = {}
    for record in records:
        if record[0] not in unique_records.keys():
            unique_records[record[0]] = record
        else:
            if float(unique_records[record[0]][7]) < float(record[7]):
                unique_records[record[0]] = record
    unique_records = get_merged_records(unique_records.values())
    return unique_records

def write_file(filename, records):
    with open(filename, mode='w', encoding='utf-8') as f:
        f.writelines(records)

def get_record_by_barcode(records, barcode):
    for record in records:
        if barcode == get_splitted_record(record)[0]:
            return record
    return None

def append_record_to_file(filename, record):
    print(f'Inserimento record su {filename}...')
    with open(filename, mode='a+', encoding='utf-8') as f:
        f.write(record)
    print('Record inserito')

def read_file(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        return f.readlines()

def quit_server():
    print('Chiusura del socket...')
    SOCKET.close()
    print('Socket chiuso')
    os._exit(0)

def on_add(conn, message):
    record = message[5:] + '\n'
    append_record_to_file(DEFAULT_FILENAME, record)
    append_record_to_file(ADD_FILENAME, record)
    conn.send(LOGS['success'].encode('utf-8'))

def on_edit(conn, message):
    barcode, new_record = message.split(' ', 2)[1:]
    records = read_file(DEFAULT_FILENAME)
    print(f'Modifica del record {barcode}...')
    for i in range(len(records)):
        if barcode == get_splitted_record(records[i])[0]:
            records[i] = new_record
            break
    write_file(DEFAULT_FILENAME, records)
    append_record_to_file(EDIT_FILENAME, new_record)
    print('Modifica effettuata')
    conn.send(LOGS['success'].encode('utf-8'))

def on_find(conn, message):
    barcode = message[6:]
    records = read_file(DEFAULT_FILENAME)
    print(f'Ricerca del record {barcode}...')
    record = get_record_by_barcode(records, barcode)
    if record:
        print(f'Record trovato: {record[:-1]}')
        print('Invio del record...')
        conn.send(record.encode('utf-8'))
        print('Record inviato')
    else:
        print('Record non trovato')
        conn.send(LOGS['not_found'].encode('utf-8'))

def on_delete(conn, message):
    barcode = message[8:]
    records = read_file(DEFAULT_FILENAME)
    print(f'Ricerca del record {barcode}...')
    record = get_record_by_barcode(records, barcode)
    if record:
        print(f'Record trovato: {record[:-1]}')
        print(f'Cancellazione del record {barcode}...')
        for i in range(len(records)):
            if barcode == get_splitted_record(records[i])[0]:
                records.pop(i)
                break
        write_file(DEFAULT_FILENAME, records)
        print('Record cancellato')
        conn.send(LOGS['success'].encode('utf-8'))
    else:
        print('Record non trovato')
        conn.send(LOGS['not_found'].encode('utf-8'))

def on_show_duplicate(conn):
    records = read_file(DEFAULT_FILENAME)
    print('Ricerca dei duplicati...')
    repeated_records = get_repeated_records(records)
    if repeated_records:
        repeated_records.sort()
        print(f'Duplicati trovati: {repeated_records}')
        write_file(DUPLICATES_FILENAME, repeated_records)
        print('Invio i duplicati...')
        for repeated_record in repeated_records:
            conn.send(repeated_record.encode('utf-8'))
            conn.recv(BUFFER_SIZE)
        print('Duplicati inviati')
        conn.send(LOGS['success'].encode('utf-8'))
    else:
        print('Non ci sono duplicati')
        conn.send(LOGS['not_found'].encode('utf-8'))

def on_delete_duplicate(conn):
    records = read_file(DEFAULT_FILENAME)
    print('Ricerca dei duplicati...')
    repeated_records = get_repeated_records(records)
    if repeated_records:
        repeated_records.sort()
        print(f'Duplicati trovati: {repeated_records}')
        print('Eliminazione dei duplicati...')
        unique_records = get_unique_records(records)
        write_file(DEFAULT_FILENAME, unique_records)
        print('Duplicati eliminati')
        conn.send(LOGS['success'].encode('utf-8'))
    else:
        print('Non ci sono duplicati')
        conn.send(LOGS['not_found'].encode('utf-8'))

def on_backup(conn):
    print('Backup in corso...')
    shutil.copyfile(DEFAULT_FILENAME, BACKUP_FILENAME)
    print('Backup eseguito')
    conn.send(LOGS['success'].encode('utf-8'))

def on_update_database(conn):
    print('Aggiornamento del database...')
    process_name = 'menu.exe'
    process = get_process(process_name)
    if process: killProcess(process.pid)
    pag.press('winleft')
    pag.write('magaworld')
    pag.press('enter')
    pag.click(850, 600)
    pag.click(210, 680)
    pag.click(400, 670)
    print('Database aggiornato')
    conn.send(LOGS['success'].encode('utf-8'))

def on_get_database_file(conn):
    print(f'Invio del file {DEFAULT_FILENAME} ...')
    with open(DEFAULT_FILENAME, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk: break
            conn.send(chunk)
            conn.recv(BUFFER_SIZE)
    print('File inviato')
    conn.send(LOGS['success'].encode('utf-8'))

def multi_thread_conn(conn, addr):
    global N_THREAD
    while True:
        try:
            message = conn.recv(2048)
        except ConnectionResetError:
            print('Sessione scaduta')
            break
        if not message: break
        message = message.decode('utf-8')
        print(f'N_THREADS: {N_THREAD} -{addr}: {message.strip()}')
        if message == COMMANDS['quit_server']: quit_server()
        if message.startswith(COMMANDS['add']): on_add(conn, message)
        if message.startswith(COMMANDS['edit']): on_edit(conn, message)
        if message.startswith(COMMANDS['find']): on_find(conn, message)
        if message.startswith(COMMANDS['remove']): on_delete(conn, message)
        if message == COMMANDS['show_duplicate']: on_show_duplicate(conn)
        if message == COMMANDS['delete_duplicate']: on_delete_duplicate(conn)
        if message == COMMANDS['backup']: on_backup(conn)
        if message == COMMANDS['update_database']: on_update_database(conn)
        if message == COMMANDS['get_database_file']: on_get_database_file(conn)
    
    print('Chiusura connessione...')
    conn.close()
    print('Connessione chiusa')

    print('Chiusura thread')
    N_THREAD -= 1
    return

def main(host, port):
    global N_THREAD
    SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SOCKET.bind((host, port))
    print(f'In ascolto {host}:{port}...')
    SOCKET.listen(5)
    while True:
        conn, addr = SOCKET.accept()
        print(f'Connessione effettuata da {addr}')
        print('Creazione thread...')
        start_new_thread(multi_thread_conn, (conn, addr))
        N_THREAD += 1
        print(f'Thread {N_THREAD} creato')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ping Store Server basato sui socket TCP.')
    parser.add_argument('-i', '--host', help='Host della macchina che stai usando attualmente.')
    parser.add_argument('-p', '--port', help='Porta su cui vuoi mettere in ascolto la macchina.')

    args = parser.parse_args()
    host = args.host
    port = args.port

    if not host:
        host = HOST_DEFAULT
    if not port:
        port = PORT_DEFAULT
    else:
        port = int(port)
    
    main(host, port)
