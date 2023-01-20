import tkinter.filedialog
import tkinter as tk

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

def read_file(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        return f.readlines()

def show_duplicates():
    if RECORD_LIST.winfo_ismapped():
        RECORD_LIST.grid_forget()
        VERTICAL_SCROLLBAR.grid_forget()
        HORIZONTAL_SCROLLBAR.grid_forget()
    else:
        records = read_file(DEFAULT_FILENAME)
        repeated_records = get_repeated_records(records)
        repeated_records.sort()
        
        if repeated_records:
            RECORD_LIST.grid(row=3, column=0, columnspan=2, sticky='nesw')
            for repeated_record in repeated_records:
                RECORD_LIST.insert(tk.END, repeated_record[:-1])

            VERTICAL_SCROLLBAR.grid(row=3, column=2, sticky='nesw')
            HORIZONTAL_SCROLLBAR.grid(row=4, column=0, columnspan=2, sticky='nesw')
            LOG_LABEL.config(text='Log: ')
        else:
            #LOG_LABEL.config(text='Log: Duplicates not found')
            LOG_LABEL.config(text='Log: 未找到重复项')

def delete_duplicates():
    if RECORD_LIST.winfo_ismapped():
        RECORD_LIST.grid_forget()
        VERTICAL_SCROLLBAR.grid_forget()
        HORIZONTAL_SCROLLBAR.grid_forget()
    records = read_file(DEFAULT_FILENAME)
    repeated_records = get_repeated_records(records)
    if repeated_records:
        repeated_records.sort()
        unique_records = get_unique_records(records)
        write_file(DEFAULT_FILENAME, unique_records)
        #LOG_LABEL.config(text='Log: Duplicates deleted successfully')
        LOG_LABEL.config(text='Log: 重复删除成功')
    else:
        #LOG_LABEL.config(text='Log: Duplicates not found')
        LOG_LABEL.config(text='Log: 未找到重复项')

def save_duplicates():
    if RECORD_LIST.winfo_ismapped():
        RECORD_LIST.grid_forget()
        VERTICAL_SCROLLBAR.grid_forget()
        HORIZONTAL_SCROLLBAR.grid_forget()
    records = read_file(DEFAULT_FILENAME)
    repeated_records = get_repeated_records(records)
    if repeated_records:
        repeated_records.sort()
        write_file(DUPLICATES_FILENAME, repeated_records)
        #LOG_LABEL.config(text='Log: Duplicates saved successfully')
        LOG_LABEL.config(text='Log: 重复删除成功')
    else:
        #LOG_LABEL.config(text='Log: Duplicates not found')
        LOG_LABEL.config(text='Log: 未找到重复项')

def append_records():
    if RECORD_LIST.winfo_ismapped():
        RECORD_LIST.grid_forget()
        VERTICAL_SCROLLBAR.grid_forget()
        HORIZONTAL_SCROLLBAR.grid_forget()

    new_records_file = tk.filedialog.askopenfilename()
    if new_records_file:
        new_records = read_file(new_records_file)
        if new_records:
            records = read_file(DEFAULT_FILENAME)
            records.extend(new_records)
            write_file(DEFAULT_FILENAME, records)
            LOG_LABEL.config(text=f'Log: {new_records_file}')
        else:
            #LOG_LABEL.config(text=f'Log: New records not found')
            LOG_LABEL.config(text=f'Log: 未找到新记录')


DEFAULT_FILENAME = 'import.csv'
DUPLICATES_FILENAME = 'duplicates.csv'

ROOT = tk.Tk()

BUTTONS = {
    'Show Duplicates': tk.Button(
        ROOT,
        #text='Show Duplicates',
        text='显示重复项',
        command=show_duplicates,
    ),
    'Save Duplicates': tk.Button(
        ROOT,
        #text='Save Duplicates',
        text='保存重复项',
        command=save_duplicates,
    ),
    'Delete Duplicates': tk.Button(
        ROOT,
        #text='Delete Duplicates',
        text='删除重复项',
        command=delete_duplicates,
    ),
    'Append Records': tk.Button(
        ROOT,
        #text='Append Records',
        text='添加记录',
        command=append_records,
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
    tk.Grid.rowconfigure(ROOT, 3, weight=1)

    BUTTONS['Show Duplicates'].grid(row=0, column=0, sticky='nesw')
    BUTTONS['Save Duplicates'].grid(row=0, column=1, sticky='nesw')
    BUTTONS['Delete Duplicates'].grid(row=1, column=0, sticky='nesw')
    BUTTONS['Append Records'].grid(row=1, column=1, sticky='nesw')

    RECORD_LIST.config(yscrollcommand=VERTICAL_SCROLLBAR.set)
    VERTICAL_SCROLLBAR.config(command=RECORD_LIST.yview)
    RECORD_LIST.config(xscrollcommand=HORIZONTAL_SCROLLBAR.set)
    HORIZONTAL_SCROLLBAR.config(command=RECORD_LIST.xview)

    LOG_LABEL.grid(row=2, column=0, columnspan=3, sticky='nesw')

    ROOT.mainloop()

if __name__ == '__main__':
    main()
