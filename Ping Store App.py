import tkinter.filedialog
import tkinter as tk
import re


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
    with open(filename, mode='w', encoding='utf-8-sig') as f:
        f.writelines(records)

def read_file(filename):
    with open(filename, mode='r', encoding='utf-8-sig') as f:
        return f.readlines()

def get_not_formatted_records(records):
    not_formatted_records = []
    splitted_records = get_splitted_records(records)
    for record in splitted_records:
        length_correct = len(record) == 12
        barcode_correct = re.search(r'^\d{13}$', record[0])
        cost_correct = re.search(r'^\d+.\d{2}$', record[6])
        price_correct = re.search(r'^\d+.\d{2}$', record[7])
        if not (
            barcode_correct and
            cost_correct and
            price_correct and
            length_correct
        ):
            not_formatted_records.append(record)
    not_formatted_records = get_merged_records(not_formatted_records)
    return not_formatted_records


def show_record_list(records):
    RECORD_LIST.grid(row=3, column=0, columnspan=3, sticky='nesw')
    for record in records:
        RECORD_LIST.insert(tk.END, record[:-1])
    VERTICAL_SCROLLBAR.grid(row=3, column=3, sticky='nesw')
    HORIZONTAL_SCROLLBAR.grid(row=4, column=0, columnspan=3, sticky='nesw')
    LOG_LABEL.config(text=f'Log: {len(records)} records found')

def remove_record_list():
    RECORD_LIST.delete(0, tk.END)
    RECORD_LIST.grid_remove()
    VERTICAL_SCROLLBAR.grid_remove()
    HORIZONTAL_SCROLLBAR.grid_remove()
    RECORD_LIST.grid_forget()
    VERTICAL_SCROLLBAR.grid_forget()
    HORIZONTAL_SCROLLBAR.grid_forget()
    LOG_LABEL.config(text='Log: ')

def show_duplicates():
    if RECORD_LIST.winfo_ismapped(): remove_record_list()
    records = read_file(DEFAULT_FILENAME)
    repeated_records = get_repeated_records(records)
    if not repeated_records:
        LOG_LABEL.config(text='Log: Duplicates not found')
        return
    repeated_records.sort()
    show_record_list(repeated_records)

def delete_duplicates():
    if RECORD_LIST.winfo_ismapped(): remove_record_list()
    records = read_file(DEFAULT_FILENAME)
    repeated_records = get_repeated_records(records)
    if not repeated_records:
        LOG_LABEL.config(text='Log: Duplicates not found')
        return
    unique_records = get_unique_records(records)
    write_file(DEFAULT_FILENAME, unique_records)
    LOG_LABEL.config(text='Log: Duplicates deleted successfully')

def save_duplicates():
    if RECORD_LIST.winfo_ismapped(): remove_record_list()
    records = read_file(DEFAULT_FILENAME)
    repeated_records = get_repeated_records(records)
    if not repeated_records:
        LOG_LABEL.config(text='Log: Duplicates not found')
        return
    repeated_records.sort()
    write_file(DUPLICATES_FILENAME, repeated_records)
    LOG_LABEL.config(text='Log: Duplicates saved successfully')

def append_records():
    if RECORD_LIST.winfo_ismapped(): remove_record_list()
    new_records_file = tk.filedialog.askopenfilename()
    if not new_records_file: return
    new_records = read_file(new_records_file)
    if not new_records:
        LOG_LABEL.config(text='Log: New records not found')
        return
    records = read_file(DEFAULT_FILENAME)
    records.extend(new_records)
    write_file(DEFAULT_FILENAME, records)
    LOG_LABEL.config(text=f'Log: {new_records_file}')

def show_bad_formatted_records():
    if RECORD_LIST.winfo_ismapped(): remove_record_list()
    records = read_file(DEFAULT_FILENAME)
    not_formatted_records = get_not_formatted_records(records)
    if not not_formatted_records:
        LOG_LABEL.config(text='Log: All records are formatted correctly')
        return
    show_record_list(not_formatted_records)


DEFAULT_FILENAME = 'import.csv'
DUPLICATES_FILENAME = 'duplicates.csv'

ROOT = tk.Tk()

BUTTONS = {
    'Show Duplicates': tk.Button(
        ROOT,
        text='Show Duplicates',
        command=show_duplicates,
    ),
    'Save Duplicates': tk.Button(
        ROOT,
        text='Save Duplicates',
        command=save_duplicates,
    ),
    'Delete Duplicates': tk.Button(
        ROOT,
        text='Delete Duplicates',
        command=delete_duplicates,
    ),
    'Append Records': tk.Button(
        ROOT,
        text='Append Records',
        command=append_records,
    ),
    'Show Badly Formatted Records': tk.Button(
        ROOT,
        text='Show Badly Formatted Records',
        command=show_bad_formatted_records,
    ),
}

RECORD_LIST = tk.Listbox(ROOT)
VERTICAL_SCROLLBAR = tk.Scrollbar(ROOT, orient='vertical')
HORIZONTAL_SCROLLBAR = tk.Scrollbar(ROOT, orient='horizontal')

LOG_LABEL = tk.Label(ROOT, text='Log: ', anchor='w')

def main():

    ROOT.title('Ping Store App')

    tk.Grid.columnconfigure(ROOT, 0, weight=1)
    tk.Grid.columnconfigure(ROOT, 1, weight=1)
    tk.Grid.columnconfigure(ROOT, 2, weight=1)
    tk.Grid.rowconfigure(ROOT, 3, weight=1)

    BUTTONS['Show Duplicates'].grid(row=0, column=0, sticky='nesw')
    BUTTONS['Save Duplicates'].grid(row=0, column=1, sticky='nesw')
    BUTTONS['Delete Duplicates'].grid(row=1, column=0, sticky='nesw')
    BUTTONS['Append Records'].grid(row=1, column=1, sticky='nesw')
    BUTTONS['Show Badly Formatted Records'].grid(row=0, column=2, sticky='nesw')

    RECORD_LIST.config(yscrollcommand=VERTICAL_SCROLLBAR.set)
    VERTICAL_SCROLLBAR.config(command=RECORD_LIST.yview)
    RECORD_LIST.config(xscrollcommand=HORIZONTAL_SCROLLBAR.set)
    HORIZONTAL_SCROLLBAR.config(command=RECORD_LIST.xview)

    LOG_LABEL.grid(row=2, column=0, columnspan=3, sticky='nesw')

    ROOT.mainloop()

if __name__ == '__main__':
    main()
