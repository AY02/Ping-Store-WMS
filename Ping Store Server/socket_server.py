import os
import socket, argparse
from collections import Counter
import json
import shutil
import pyautogui as pag
import psutil
from _thread import *

pag.PAUSE = 1

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST_DEFAULT = socket.gethostbyname(socket.gethostname())
PORT_DEFAULT = 10000

FILENAME_DEFAULT = 'import.csv'
BACKUP_FILENAME = 'backup.csv'
UPDATE_FILENAME = 'update.csv'
MESSAGE = ''
N_THREAD = 0
COMMANDS = {

    'quit_server': '!quit_server',

    'success': '!success',
    'failure': '!failure',

    'add': '!add',
    'edit': '!edit',
    'find': '!find',
    'delete': '!delete',

    'show_duplicate': '!show_duplicate',
    'delete_duplicate': '!delete_duplicate',
    'backup': '!backup',
    'update_database': '!update_database',

    'ping': '!ping',

}

def get_process(name):
    for proc in psutil.process_iter():
        if proc.name() == name:
            return proc
    return None

def find_process(name):
    for proc in psutil.process_iter():
        if proc.name() == name:
            return True
    return False

def get_barcode(record):
	return record.split(';')[0].strip()

def get_price(record):
    if record.split(';')[7] == '':
        return 0.00
    return float(record.split(';')[7].strip())

def get_barcodes(records):
	return [get_barcode(record) for record in records]

def get_repeated_barcodes(barcodes):
	return [barcode for barcode, n in Counter(barcodes).items() if n > 1]

def get_unique_barcodes(barcodes):
	seen_barcodes = []
	for barcode in barcodes:
		if barcode not in seen_barcodes:
			seen_barcodes.append(barcode)
	return seen_barcodes

def get_repeated_records(records):
	barcodes = get_barcodes(records)
	repeated_barcodes = get_repeated_barcodes(barcodes)
	repeated_records = [records[i] for i in range(len(records)) if barcodes[i] in repeated_barcodes]
	return repeated_records

def get_max_price(records):
	max_price = 0
	for record in records:
		if get_price(record) > max_price:
			max_price = get_price(record)
	return max_price

def get_unique_records(records):
	repeated_records = get_repeated_records(records)
	repeated_barcodes = get_barcodes(repeated_records)
	unique_barcodes = get_unique_barcodes(repeated_barcodes)
	unique_records = []
	for unique_barcode in unique_barcodes:
		tmp_records = [record for record in repeated_records if get_barcode(record) == unique_barcode]
		max_price = get_max_price(tmp_records)
		for tmp_record in tmp_records:
			if get_price(tmp_record) == max_price:
				unique_records.append(tmp_record)
				break
	return unique_records

def get_record_by_barcode(records, barcode):
    for record in records:
        if barcode == get_barcode(record):
            return record
    return None

def find_record(records, barcode):
    for record in records:
        if barcode == get_barcode(record):
            return True
    return False

def multi_thread_conn(conn, addr):
    global SOCKET, MESSAGE, N_THREAD
    while True:
        MESSAGE = conn.recv(2048)
        if not MESSAGE: break
        MESSAGE = MESSAGE.decode('utf-8')
        print(f'N_THREADS: {N_THREAD} -{addr}: {MESSAGE}')
        if MESSAGE == COMMANDS['quit_server']:
            print('Chiusura del socket...')
            SOCKET.close()
            print('Socket chiuso')
            os._exit(0)
        if MESSAGE.startswith(COMMANDS['add']):
            print(f'Inserimento record su {FILENAME_DEFAULT}...')
            with open(FILENAME_DEFAULT, mode='a+', encoding='utf-8') as f:
                f.write(MESSAGE[5:]+'\n')
            print('Record inserito')
            print(f'Inserimento record su {UPDATE_FILENAME}...')
            with open(UPDATE_FILENAME, mode='a+', encoding='utf-8') as f:
                f.write(MESSAGE[5:]+'\n')
            print('Record inserito')
            conn.send(COMMANDS['success'].encode('utf-8'))
        if MESSAGE.startswith(COMMANDS['edit']):
            fields = MESSAGE.split(' ', 2)
            barcode = fields[1]
            new_record = fields[2]
            with open(FILENAME_DEFAULT, mode='r', encoding='utf-8') as f:
                records = f.readlines()
            print(f'Ricerca del record {barcode}...')
            found = find_record(records, barcode)
            if found:
                print('Record trovato')
                print(f'Modifica del record {barcode}...')
                for i in range(len(records)):
                    if barcode == get_barcode(records[i]):
                        records[i] = new_record
                        break
                with open(FILENAME_DEFAULT, mode='w', encoding='utf-8') as f:
                    f.writelines(records)
                print('Modifica effettuata')
                conn.send(COMMANDS['success'].encode('utf-8'))
            else:
                print('Record non trovato')
                conn.send('Record not found'.encode('utf-8'))
        if MESSAGE.startswith(COMMANDS['find']):
            barcode = MESSAGE[6:]
            with open(FILENAME_DEFAULT, mode='r', encoding='utf-8') as f:
                records = f.readlines()
            print(f'Ricerca del record {barcode}...')
            found = find_record(records, barcode)
            if found:
                found_record = get_record_by_barcode(records, barcode)
                print(f'Record trovato: {found_record[:-1]}')
                conn.send(found_record.encode('utf-8'))
            else:
                print('Record non trovato')
                conn.send('Record not found'.encode('utf-8'))
        if MESSAGE.startswith(COMMANDS['delete']+' '):
            barcode = MESSAGE[8:]
            with open(FILENAME_DEFAULT, mode='r', encoding='utf-8') as f:
                records = f.readlines()
            print(f'Ricerca del record {barcode}...')
            found = find_record(records, barcode)
            if found:
                print('Record trovato')
                print(f'Cancellazione del record {barcode}...')
                for i in range(len(records)):
                    if barcode == get_barcode(records[i]):
                        records.pop(i)
                        break
                with open(FILENAME_DEFAULT, mode='w', encoding='utf-8') as f:
                    f.writelines(records)
                print('Record cancellato')
                conn.send(COMMANDS['success'].encode('utf-8'))
            else:
                print('Record non trovato')
                conn.send('Record not found'.encode('utf-8'))
        if MESSAGE == COMMANDS['show_duplicate']:
            with open(FILENAME_DEFAULT, mode='r', encoding='utf-8') as f:
                records = f.readlines()
            print('Ricerca dei duplicati...')
            repeated_records = get_repeated_records(records)
            if repeated_records:
                repeated_records.sort()
                print(f'Duplicati trovati: {repeated_records}')
                conn.send(json.dumps(repeated_records).encode('utf-8'))
            else:
                print('Non ci sono duplicati')
                conn.send(json.dumps(['No results found']).encode('utf-8'))
        if MESSAGE == COMMANDS['delete_duplicate']:
            with open(FILENAME_DEFAULT, mode='r', encoding='utf-8') as f:
                records = f.readlines()
            print('Ricerca dei duplicati...')
            repeated_records = get_repeated_records(records)
            if repeated_records:
                repeated_records.sort()
                print(f'Duplicati trovati: {repeated_records}')
                print('Eliminazione dei duplicati...')
                barcodes = get_barcodes(repeated_records)
                unique_barcodes = get_unique_barcodes(barcodes)
                unique_records = get_unique_records(records)
                with open(FILENAME_DEFAULT, 'w', encoding='utf-8') as f:
                    for unique_record in unique_records:
                        f.write(unique_record)
                    barcodes_seen = get_barcodes(unique_records)
                    for record in records:
                        barcode = get_barcode(record)
                        if barcode not in barcodes_seen:
                            barcodes_seen.append(barcode)
                            f.write(record)
                print('Duplicati eliminati')
                conn.send(COMMANDS['success'].encode('utf-8'))
            else:
                print('Non ci sono duplicati')
                conn.send('No results found'.encode('utf-8'))
        if MESSAGE == COMMANDS['backup']:
            print('Backup in corso...')
            shutil.copyfile(FILENAME_DEFAULT, BACKUP_FILENAME)
            print('Backup eseguito')
            conn.send(COMMANDS['success'].encode('utf-8'))
        if MESSAGE == COMMANDS['update_database']:
            print('Aggiornamento del database...')
            process_name = 'menu.exe'
            found = find_process(process_name)
            if found:
                process = get_process(process_name)
                killProcess(process.pid)
            pag.press('winleft')
            pag.write('magaworld')
            pag.press('enter')
            pag.click(850, 600)
            pag.click(211, 680)
            pag.click(400, 669)
            print('Database aggiornato')
            conn.send(COMMANDS['success'].encode('utf-8'))
    
    print('Chiusura connessione...')
    conn.close()
    print('Connessione chiusa')

    print('Chiusura thread')
    N_THREAD -= 1
    return

def main(host, port):
    global SOCKET, MESSAGE, N_THREAD
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

    parser = argparse.ArgumentParser(description='Questo è un socket server tcp minimale.')
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
