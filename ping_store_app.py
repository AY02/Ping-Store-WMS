#import os
#os.environ['TCL_LIBRARY'] = '/home/ayang/.local/share/uv/python/cpython-3.14.2-linux-x86_64-gnu/lib/tcl9.0'
#os.environ['TK_LIBRARY'] = '/home/ayang/.local/share/uv/python/cpython-3.11.3-linux-x86_64-gnu/lib/tk9.0'


# Properties:
# - The program uses only CSV files
# - The program works on a copy of the CSV and never on the original
# - The CSV loading only happens at the start
# - Validation logic is handled at the CSV file'ERROR' level
# - Duplication logic is handled at the Database object level
# - Header CSV: Barcode, description, quantity, department, stock, supplier, cost, price 1, price 2, price 3, notes and images
# - Changes to the original CSV are not applied to the runtime copy
# - Until you confirm the applied changes, the original CSV remains unchanged
# Example 1: If you add a product to the original CSV, it is not inserted into the database at runtime
# Example 2: If you remove duplicates with the program but do not confirm the changes, then the original CSV is not changed


from dataclasses import dataclass, field
from typing import ClassVar, Final, Iterable, Iterator, Optional
import tkinter as tk
from tkinter import StringVar, filedialog, messagebox, ttk
from pathlib import Path
from enum import IntEnum, IntFlag, auto
from collections import defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re, csv, shutil, json


class ProductIndex(IntEnum):
    BARCODE = 0
    DESCRIPTION = 1
    QUANTITY = 2
    DEPARTMENT = 3
    STOCK = 4
    SUPPLIER = 5
    COST = 6
    PRICE1 = 7
    PRICE2 = 8
    PRICE3 = 9
    NOTES = 10
    IMAGES = 11

HEADERS_IT = {
    ProductIndex.BARCODE: 'BARCODE',
    ProductIndex.DESCRIPTION: 'DESCRIZIONE',
    ProductIndex.QUANTITY: 'QUANTITA\'',
    ProductIndex.DEPARTMENT: 'REPARTO',
    ProductIndex.STOCK: 'SCORTA',
    ProductIndex.SUPPLIER: 'FORNITORE',
    ProductIndex.COST: 'COSTO',
    ProductIndex.PRICE1: 'PREZZO 1',
    ProductIndex.PRICE2: 'PREZZO 2',
    ProductIndex.PRICE3: 'PREZZO 3',
    ProductIndex.NOTES: 'NOTE',
    ProductIndex.IMAGES: 'IMMAGINI'
}

IT_ERROR_STR = 'ERRORE'

FIELD_COUNT = len(ProductIndex)
STD_DELIMITER = ';'

class ValidationError(IntFlag):
    FIELD_COUNT = auto()
    BARCODE = auto()
    DESCRIPTION = auto()
    QUANTITY = auto()
    DEPARTMENT = auto()
    STOCK = auto()
    SUPPLIER = auto()
    COST = auto()
    PRICE1 = auto()
    PRICE2 = auto()
    PRICE3 = auto()
    NOTES = auto()
    IMAGES = auto()

ERR_MESSAGES = {
    ValidationError.FIELD_COUNT: f'Errato n. campi (attesi {FIELD_COUNT})',
    ValidationError.BARCODE: f'{HEADERS_IT[ProductIndex.BARCODE]}: Serve numerico 13 cifre',
    ValidationError.DESCRIPTION: f'{HEADERS_IT[ProductIndex.DESCRIPTION]}: Mancante oppure vietati {STD_DELIMITER} e a capo',
    ValidationError.QUANTITY: f'{HEADERS_IT[ProductIndex.QUANTITY]}: Serve intero positivo',
    ValidationError.DEPARTMENT: f'{HEADERS_IT[ProductIndex.DEPARTMENT]}: Vietati {STD_DELIMITER} e a capo',
    ValidationError.STOCK: f'{HEADERS_IT[ProductIndex.STOCK]}: Serve intero positivo',
    ValidationError.SUPPLIER: f'{HEADERS_IT[ProductIndex.SUPPLIER]}: Mancante oppure vietati {STD_DELIMITER} e a capo',
    ValidationError.COST: f'{HEADERS_IT[ProductIndex.COST]}: Serve formato N.XX',
    ValidationError.PRICE1: f'{HEADERS_IT[ProductIndex.PRICE1]}: Serve formato N.XX',
    ValidationError.PRICE2: f'{HEADERS_IT[ProductIndex.PRICE2]}: Serve formato N.XX',
    ValidationError.PRICE3: f'{HEADERS_IT[ProductIndex.PRICE3]}: Serve formato N.XX',
    ValidationError.NOTES: f'{HEADERS_IT[ProductIndex.NOTES]}: Vietati {STD_DELIMITER} e a capo',
    ValidationError.IMAGES :f'{HEADERS_IT[ProductIndex.IMAGES]}: Vietati {STD_DELIMITER} e a capo'
}

RE_BARCODE = re.compile(r'\d{13}')
RE_NO_SEMICOLON_ENDLINE = re.compile(fr'[^{STD_DELIMITER}\n]+')
RE_NO_SEMICOLON_ENDLINE_OPT = re.compile(fr'[^{STD_DELIMITER}\n]*')
RE_UNSIGNED_INT = re.compile(r'0|[1-9]\d*')
RE_PRICE = re.compile(r'0\.\d{2}|[1-9]\d*\.\d{2}')
RE_PRICE_OPT = re.compile(r'(0\.\d{2}|[1-9]\d*\.\d{2})?')


@dataclass
class PriceInterval:
    min_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    max_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    target_price: Decimal = field(default_factory=lambda: Decimal('0.00'))

    def __post_init__(self):
        self.min_cost = self.min_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.max_cost = self.max_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.target_price = self.target_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def is_set(self) -> bool:
        return any([
            self.min_cost,
            self.max_cost,
            self.target_price
        ])
    
    def is_valid(self) -> bool:
        return all([
            self.min_cost >= Decimal('0.00'),
            self.min_cost <= self.max_cost,
            self.target_price > self.max_cost
        ])


@dataclass
class Database:

    _instance: ClassVar[Optional['Database']] = None
    _initialized: ClassVar[bool] = False

    CONFIG_FILENAME: ClassVar[Final[str]] = 'config.json'

    PRODUCTS_BACKUP_FILENAME: ClassVar[Final[str]] = 'import_backup.csv'
    PRODUCTS_FILENAME: ClassVar[Final[str]] = 'import.csv'
    DUPLICATES_FILENAME: ClassVar[Final[str]] = 'duplicati.csv'
    INVALID_PRODUCTS_FILENAME: ClassVar[Final[str]] = 'prodotti_invalidi.csv'

    raw_rows: list[list[str]] = field(init=False)
    idx_valid_rows: list[int] = field(init=False)
    idx_invalid_rows: list[int] = field(init=False)
    idx_duplicate_rows: dict[str, list[int]] = field(init=False)

    intervals: list[PriceInterval] = field(init=False)

    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __post_init__(self) -> None:
        if self._initialized:
            return
        self.intervals = [PriceInterval() for _ in range(10)]
        self._load_intervals()
        self._load_from_csv()
        Database._initialized = True

    def set_interval(self, idx: int, min_cost: str | float | Decimal, max_cost: str | float | Decimal, target_price: str | float | Decimal) -> bool:
        if not (0 <= idx < len(self.intervals)): return False
        try:
            min_cost = Decimal(str(min_cost))
            max_cost = Decimal(str(max_cost))
            target_price = Decimal(str(target_price))
        except (ValueError, InvalidOperation): return False
        new_interval = PriceInterval(min_cost, max_cost, target_price)
        # Interval reset
        if not new_interval.is_set():
            self.intervals[idx] = new_interval
            return True
        if not new_interval.is_valid(): return False
        self.intervals[idx] = new_interval
        return True

    def apply_intervals_to_external_file(self, filename: str) -> int:
        count = 0
        if not Path(filename).exists(): return count
        active_intervals = [i for i in self.intervals if i.is_set()]
        if not active_intervals: return count
        rows = list(Database.read_csv(filename))
        for row in rows:
            try:
                cost_val = Decimal(row[ProductIndex.COST])
                # First match wins
                for interval in active_intervals:
                    if interval.min_cost <= cost_val <= interval.max_cost:
                        new_price_str = f'{interval.target_price:.2f}'
                        if row[ProductIndex.PRICE1] != new_price_str:
                            row[ProductIndex.PRICE1] = new_price_str
                            count += 1
                        break
            except (ValueError, InvalidOperation, IndexError):
                continue
        if count > 0: Database.write_csv(filename, rows)
        return count

    """It works on the main database
    def apply_intervals(self) -> int:
        count = 0
        active_intervals = [i for i in self.intervals if i.is_set()]
        if not active_intervals or not self.idx_valid_rows:
            return count
        for row_idx in self.idx_valid_rows:
            row = self.raw_rows[row_idx]
            cost_val = Decimal(row[ProductIndex.COST])
            # First match wins
            for interval in active_intervals:
                if interval.min_cost <= cost_val <= interval.max_cost:
                    new_price_str = f'{interval.target_price:.2f}'
                    if row[ProductIndex.PRICE1] != new_price_str:
                        row[ProductIndex.PRICE1] = new_price_str
                        count += 1
                    break
        return count"""

    def export_intervals(self) -> None:
        data = []
        for interval in self.intervals:
            if interval.is_set():
                data.append({
                    'min_cost': str(interval.min_cost),
                    'max_cost': str(interval.max_cost),
                    'target_price': str(interval.target_price)
                })
        with open(self.CONFIG_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get_invalid_rows(self) -> Iterator[list[str]]:
        for i in self.idx_invalid_rows:
            yield self.raw_rows[i]

    def get_duplicate_rows(self) -> Iterator[list[str]]:
        for indices in self.idx_duplicate_rows.values():
            for i in indices: yield self.raw_rows[i]

    def export_invalid_rows(self) -> None:
        Database.write_csv(self.INVALID_PRODUCTS_FILENAME, self.get_invalid_rows())

    def export_duplicate_rows(self) -> None:
        Database.write_csv(self.DUPLICATES_FILENAME, self.get_duplicate_rows())

    def remove_invalid_rows(self) -> None:
        if not self.idx_invalid_rows:
            return
        to_remove = set(self.idx_invalid_rows)
        self.raw_rows = [
            row for i, row in enumerate(self.raw_rows)
            if i not in to_remove
        ]
        self._index_all()

    def remove_duplicates(self) -> None:
        """Keep the most recent products, i.e., the products that were inserted last."""
        if not self.idx_duplicate_rows:
            return
        to_remove = set()
        for indices in self.idx_duplicate_rows.values():
            indices.pop()
            to_remove.update(indices)
        self.raw_rows = [
            row for i, row in enumerate(self.raw_rows)
            if i not in to_remove
        ]
        self._index_all()

    def confirm_changes(self) -> None:
        if Path(self.PRODUCTS_FILENAME).exists():
            shutil.copy(self.PRODUCTS_FILENAME, self.PRODUCTS_BACKUP_FILENAME)
        Database.write_csv(self.PRODUCTS_FILENAME, self.raw_rows)

    def append_from_csv(self, filename_to_append: str) -> None:
        raw_rows = Database.read_csv(filename_to_append)
        start = len(self.raw_rows)
        self.raw_rows.extend(raw_rows)
        if len(self.raw_rows) > start:
            self._index_all()

    def attempt_revalidation(self):
        if not self.idx_invalid_rows: return
        for i in self.idx_invalid_rows:
            self.raw_rows[i] = Database.fix_single_row(self.raw_rows[i])
        self._index_all()
        
    @staticmethod
    def fix_invalids_in_external_file(filename: str) -> int:
        if not Path(filename).exists(): return 0
        raw_rows = list(Database.read_csv(filename))
        fixed_count = 0
        for i, raw_row in enumerate(raw_rows):
            if Database.is_raw_row_valid(raw_row) == 0:
                continue
            raw_rows[i] = Database._fix_single_row(raw_row)
            fixed_count += 1
        if fixed_count > 0: Database.write_csv(filename, raw_rows)
        return fixed_count

    @staticmethod
    def get_invalids_from_external_file(filename: str) -> list[list[str]]:
        if not Path(filename).exists(): return []
        raw_rows = list(Database.read_csv(filename))
        invalid_rows = []
        for raw_row in raw_rows:
            if Database.is_raw_row_valid(raw_row) != 0:
                invalid_rows.append(raw_row)
        return invalid_rows

    @staticmethod
    def remove_invalids_from_external_file(filename: str) -> int:
        if not Path(filename).exists(): return 0
        raw_rows = list(Database.read_csv(filename))
        start = len(raw_rows)
        valid_rows = [raw_row for raw_row in raw_rows if Database.is_raw_row_valid(raw_row) == 0]
        deleted_count = start - len(valid_rows)
        if deleted_count > 0: Database.write_csv(filename, valid_rows)
        return deleted_count

    @staticmethod
    def read_csv(filename: str) -> Iterator[list[str]]:
        if not Path(filename).exists():
            return
        with open(filename, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=STD_DELIMITER)
            for raw_row in reader: yield raw_row

    @staticmethod
    def write_csv(filename: str, raw_rows: Iterable[list[str]]) -> None:
        Database._save_csv(filename, raw_rows, mode='w')

    @staticmethod
    def append_csv(filename: str, raw_rows: Iterable[list[str]]) -> None:
        Database._save_csv(filename, raw_rows, mode='a')

    @staticmethod
    def _save_csv(filename: str, raw_rows: Iterable[list[str]], mode: str) -> None:
        with open(filename, mode=mode, encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=STD_DELIMITER)
            writer.writerows(raw_rows)

    @staticmethod
    def fix_single_row(invalid_row: list[str]) -> list[str]:
        integer_fields = {ProductIndex.BARCODE, ProductIndex.QUANTITY, ProductIndex.STOCK}
        price_fields = {ProductIndex.COST, ProductIndex.PRICE1, ProductIndex.PRICE2, ProductIndex.PRICE3}
        re_not_digit = re.compile(r'[^\d]')
        re_not_price_char = re.compile(r'[^\d.]')
        re_is_float = re.compile(r'^(\d+\.?\d*|\.\d+)$')
        # Normalization of the number of fields
        if len(invalid_row) > FIELD_COUNT:
            invalid_row = invalid_row[:FIELD_COUNT]
        elif len(invalid_row) < FIELD_COUNT:
            invalid_row.extend([''] * (FIELD_COUNT - len(invalid_row)))
        cleaned_row = []
        for idx, val in enumerate(invalid_row):
            val = val.strip().replace('\n', '').replace(STD_DELIMITER, '') # Removal of illegal characters
            if idx in integer_fields:
                val = re_not_digit.sub('', val) # Remove everything that isn't a digit
            elif idx in price_fields:
                val = val.replace(',', '.') # Forces the use of dot as the decimal separator
                val = re_not_price_char.sub('', val) # Remove everything that isn't a digit or a dot
                # Forces format N.XX
                if re_is_float.match(val):
                    val = f'{Decimal(val):.2f}'
            elif idx == ProductIndex.SUPPLIER:
                val = val.upper()
            cleaned_row.append(val)
        # Using default cost
        if not cleaned_row[ProductIndex.COST]:
            cleaned_row[ProductIndex.COST] = '0.01'
        # Default price = cost * 2
        if not cleaned_row[ProductIndex.PRICE1]:
            try:
                cost_decimal = Decimal(cleaned_row[ProductIndex.COST])
                new_price = cost_decimal * 2
                cleaned_row[ProductIndex.PRICE1] = f'{new_price:.2f}'
            except (InvalidOperation, ValueError):
                pass
        # Using default messages for required fields
        if not cleaned_row[ProductIndex.DESCRIPTION]:
            cleaned_row[ProductIndex.DESCRIPTION] = 'DESCRIZIONE MANCANTE'
        if not cleaned_row[ProductIndex.SUPPLIER]:
            cleaned_row[ProductIndex.SUPPLIER] = 'FORNITORE MANCANTE'
        return cleaned_row

    @staticmethod
    def is_raw_row_valid(raw_row: list[str]) -> IntFlag:
        if len(raw_row) != FIELD_COUNT:
            return ValidationError.FIELD_COUNT
        errors = ValidationError(0)
        if not RE_BARCODE.fullmatch(raw_row[ProductIndex.BARCODE]):
            errors |= ValidationError.BARCODE
        if not RE_NO_SEMICOLON_ENDLINE.fullmatch(raw_row[ProductIndex.DESCRIPTION]):
            errors |= ValidationError.DESCRIPTION
        if not RE_UNSIGNED_INT.fullmatch(raw_row[ProductIndex.QUANTITY]):
            errors |= ValidationError.QUANTITY
        if not RE_NO_SEMICOLON_ENDLINE_OPT.fullmatch(raw_row[ProductIndex.DEPARTMENT]):
            errors |= ValidationError.DEPARTMENT
        if not RE_UNSIGNED_INT.fullmatch(raw_row[ProductIndex.STOCK]):
            errors |= ValidationError.STOCK
        if not RE_NO_SEMICOLON_ENDLINE.fullmatch(raw_row[ProductIndex.SUPPLIER]):
            errors |= ValidationError.SUPPLIER
        if not RE_PRICE.fullmatch(raw_row[ProductIndex.COST]):
            errors |= ValidationError.COST
        if not RE_PRICE.fullmatch(raw_row[ProductIndex.PRICE1]):
            errors |= ValidationError.PRICE1
        if not RE_PRICE_OPT.fullmatch(raw_row[ProductIndex.PRICE2]):
            errors |= ValidationError.PRICE2
        if not RE_PRICE_OPT.fullmatch(raw_row[ProductIndex.PRICE3]):
            errors |= ValidationError.PRICE3
        if not RE_NO_SEMICOLON_ENDLINE_OPT.fullmatch(raw_row[ProductIndex.NOTES]):
            errors |= ValidationError.NOTES
        if not RE_NO_SEMICOLON_ENDLINE_OPT.fullmatch(raw_row[ProductIndex.IMAGES]):
            errors |= ValidationError.IMAGES
        return errors

    @staticmethod
    def get_error_message(row: list[str]) -> str:
        flags = Database.is_raw_row_valid(row)
        if flags == 0:
            return 'Valido'
        if ValidationError.FIELD_COUNT in flags:
            return ERR_MESSAGES[ValidationError.FIELD_COUNT]
        messages = []
        for error_enum in ValidationError:
            if error_enum in flags and error_enum in ERR_MESSAGES:
                full_msg = ERR_MESSAGES[error_enum]
                messages.append(full_msg)
        return ' | '.join(messages)

    def _load_intervals(self) -> None:
        if not Path(self.CONFIG_FILENAME).exists():
            return
        with open(self.CONFIG_FILENAME, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, item in enumerate(data):
            min_c = item.get('min_cost', '0.00')
            max_c = item.get('max_cost', '0.00')
            target = item.get('target_price', '0.00')
            self.set_interval(i, min_c, max_c, target)

    def _load_from_csv(self) -> None:
        self.raw_rows = list(Database.read_csv(Database.PRODUCTS_FILENAME))
        self._index_all()

    def _index_all(self) -> None:
        idx_valid_rows: list[int] = []
        idx_invalid_rows: list[int] = []
        idx_occurrences: defaultdict[str, list[int]] = defaultdict(list)
        for i, raw_row in enumerate(self.raw_rows):
            if Database.is_raw_row_valid(raw_row) == 0:
                idx_valid_rows.append(i)
            else:
                idx_invalid_rows.append(i)
            idx_occurrences[raw_row[ProductIndex.BARCODE]].append(i)
        self.idx_valid_rows = idx_valid_rows
        self.idx_invalid_rows = idx_invalid_rows
        self.idx_duplicate_rows = {k: v for k, v in idx_occurrences.items() if len(v) > 1}


class PingStoreApp:
    def __init__(self):

        self.db = Database()

        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.root.title('Ping Store App')

        self.log_var = StringVar(value='Log: Pronto.')

        self._setup_grid()
        self._build_ui()
    
    def run(self):
        self.root.mainloop()

    def on_close(self):
        if messagebox.askokcancel('Esci', 'Vuoi uscire? Le modifiche non salvate andranno perse.'):
            self.root.destroy()

    def show_duplicates(self):
        rows = list(self.db.get_duplicate_rows())
        self._open_viewer('Duplicati', rows)
        self._log(f'Visualizzati {len(rows)} duplicati.')

    def save_duplicates(self):
        self.db.export_duplicate_rows()
        self._log(f'Duplicati salvati su {Database.DUPLICATES_FILENAME}')

    def delete_duplicates(self):
        start = len(self.db.raw_rows)
        self.db.remove_duplicates()
        diff = start - len(self.db.raw_rows)
        self._log(f'Rimossi {diff} duplicati.')

    def show_invalids(self):
        err_rows = []
        for row in self.db.get_invalid_rows():
            err_msg = self.db.get_error_message(row)
            err_rows.append(row + [err_msg])
        self._open_viewer('Prodotti Invalidi', err_rows, extra_col=IT_ERROR_STR)
        self._log(f'Visualizzati {len(err_rows)} invalidi.')

    def save_invalids(self):
        self.db.export_invalid_rows()
        self._log(f'Invalidi salvati su {Database.INVALID_PRODUCTS_FILENAME}')

    def delete_invalids(self):
        start = len(self.db.raw_rows)
        self.db.remove_invalid_rows()
        diff = start - len(self.db.raw_rows)
        self._log(f'Rimossi {diff} record invalidi.')

    def show_intervals(self):
        active = [f'[{i}] {x.min_cost}-{x.max_cost}->{x.target_price}' for i, x in enumerate(self.db.intervals) if x.is_set()]
        msg = ', '.join(active) if active else 'Nessun intervallo attivo'
        self._log(f'Intervalli: {msg}')

    def apply_intervals(self) -> None:
        f = filedialog.askopenfilename(
            title='Seleziona CSV esterno per applicare intervalli',
            filetypes=[('CSV', '*.csv')]
        )
        if not f:
            self._log('Operazione annullata.')
            return
        count = self.db.apply_intervals_to_external_file(f)
        self._log(f'Aggiornati {count} prezzi nel file esterno.')
        messagebox.showinfo(
            'Completato', 
            f'File elaborato: {Path(f).name}. Prezzi aggiornati: {count}'
        )

    def show_invalids_external(self):
        f = filedialog.askopenfilename(
            title='Seleziona CSV per visualizzare errori',
            filetypes=[('CSV', '*.csv')]
        )
        if not f: return
        invalid_rows = Database.get_invalids_from_external_file(f)
        if not invalid_rows:
            messagebox.showinfo('Risultato', 'Il file è valido! Nessun errore trovato.')
        else:
            self._open_viewer(f'Errori in {Path(f).name}', invalid_rows, extra_col=IT_ERROR_STR)
            self._log(f'Trovate {len(invalid_rows)} righe invalide nel file esterno.')

    def fix_invalids_external(self):
        f = filedialog.askopenfilename(
            title='Seleziona CSV da correggere',
            filetypes=[('CSV', '*.csv')]
        )
        if not f: return
        count = Database.fix_invalids_in_external_file(f)
        if count > 0:
            messagebox.showinfo('Completato', f'Correzione applicata a {count} righe. File aggiornato.')
            self._log(f'File esterno corretto: {count} modifiche.')
        else:
            messagebox.showinfo('Info', 'Nessuna correzione necessaria.')
            self._log('Nessuna modifica al file esterno.')

    def delete_invalids_external(self):
        f = filedialog.askopenfilename(
            title='Seleziona CSV da cui eliminare errori',
            filetypes=[('CSV', '*.csv')]
        )
        if not f: return
        count = Database.remove_invalids_from_external_file(f)
        if count > 0:
            messagebox.showinfo('Completato', f'Eliminate {count} righe invalide. File aggiornato.')
            self._log(f'File esterno pulito: eliminate {count} righe.')
        else:
            messagebox.showinfo('Info', 'Nessuna riga invalida trovata.')
            self._log('Nessuna eliminazione sul file esterno.')

    def open_interval_editor(self):
        top = tk.Toplevel(self.root)
        top.title('Modifica Intervalli')
        
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)
        top.rowconfigure(2, weight=1)

        lst = tk.Listbox(top)
        lst.grid(row=0, column=0, columnspan=2, sticky='nsew')
        
        sb = tk.Scrollbar(top, command=lst.yview)
        sb.grid(row=0, column=2, sticky='ns')
        lst.config(yscrollcommand=sb.set)

        def reload_list():
            lst.delete(0, tk.END)
            for i, interval in enumerate(self.db.intervals):
                st = 'ATTIVO' if interval.is_set() else 'VUOTO'
                lst.insert(tk.END, f'{i}: {st} | {interval.min_cost} - {interval.max_cost} -> {interval.target_price}')
        reload_list()

        f_in = tk.Frame(top)
        f_in.grid(row=1, column=0, columnspan=2, sticky='nsew')
        
        for i in range(3):
            f_in.columnconfigure(i, weight=1)
        f_in.rowconfigure(0, weight=1)
        f_in.rowconfigure(1, weight=1)

        tk.Label(f_in, text='Min Cost').grid(row=0, column=0, sticky='nsew')
        tk.Label(f_in, text='Max Cost').grid(row=0, column=1, sticky='nsew')
        tk.Label(f_in, text='Target Price').grid(row=0, column=2, sticky='nsew')

        v_min = tk.Entry(f_in); v_min.grid(row=1, column=0, sticky='nsew')
        v_max = tk.Entry(f_in); v_max.grid(row=1, column=1, sticky='nsew')
        v_tgt = tk.Entry(f_in); v_tgt.grid(row=1, column=2, sticky='nsew')

        def on_sel(e):
            if not lst.curselection():
                return
            idx = lst.curselection()[0]
            it = self.db.intervals[idx]
            v_min.delete(0, tk.END); v_min.insert(0, str(it.min_cost))
            v_max.delete(0, tk.END); v_max.insert(0, str(it.max_cost))
            v_tgt.delete(0, tk.END); v_tgt.insert(0, str(it.target_price))
        lst.bind('<<ListboxSelect>>', on_sel)

        def save():
            if not lst.curselection():
                return
            idx = lst.curselection()[0]
            if self.db.set_interval(idx, v_min.get(), v_max.get(), v_tgt.get()):
                self.db.export_intervals()
                reload_list()
            else:
                messagebox.showerror('Errore', 'Dati non validi (X<=Y, Z>Y)')

        tk.Button(top, text='SALVA', command=save, bg='lightgreen').grid(row=2, column=0, columnspan=2, sticky='nsew')

    def fix_invalids(self) -> None:
        self.db.attempt_revalidation()
        self._log('Tentativo di correzione completato.')

    def append_csv(self) -> None:
        f = filedialog.askopenfilename(
            title='Seleziona file CSV da importare',
            filetypes=[('CSV', '*.csv')]
        )
        if not f:
            self._log(f'Importazione annullata.')
        start = len(self.db.raw_rows)
        self.db.append_from_csv(f)
        diff = len(self.db.raw_rows) - start
        self._log(f'Importati {diff} record.')

    def confirm_changes(self) -> None:
        self.db.confirm_changes()
        self.db.export_intervals()
        self._log('Modifiche confermate e salvate su file.')

    def _setup_grid(self) -> None:
        for col in range(3):
            self.root.grid_columnconfigure(col, weight=1)
        for row in range(6):
            self.root.grid_rowconfigure(row, weight=1)

    def _build_ui(self) -> None:
        matrix = [
            [
                ('Mostra duplicati', self.show_duplicates), 
                ('Salva duplicati', self.save_duplicates), 
                ('Elimina duplicati', self.delete_duplicates)
            ],
            [
                ('Mostra invalidi', self.show_invalids), 
                ('Salva invalidi', self.save_invalids), 
                ('Elimina invalidi', self.delete_invalids)
            ],
            [
                ('Mostra intervalli', self.show_intervals), 
                ('Modifica intervalli', self.open_interval_editor), 
                ('Applica intervalli', self.apply_intervals)
            ],
            [
                ('Mostra invalidi CSV esterno', self.show_invalids_external),
                ('Correggi invalidi CSV esterno', self.fix_invalids_external),
                ('Elimina invalidi CSV esterno', self.delete_invalids_external)
            ],
            [
                ('Correggi invalidi', self.fix_invalids), 
                ('Appendi CSV', self.append_csv), 
                ('Conferma modifiche', self.confirm_changes)
            ]
        ]
        for i, row_data in enumerate(matrix):
            for j, (text, command) in enumerate(row_data):
                btn = tk.Button(self.root, text=text, command=command)
                btn.grid(row=i, column=j, sticky='nsew')
        lbl_log = tk.Label(self.root, textvariable=self.log_var, anchor='w')
        lbl_log.grid(row=5, column=0, columnspan=3, sticky='nsew')

    def _log(self, message: str) -> None:
        self.log_var.set(f'Log: {message}')
        self.root.update_idletasks()

    def _open_viewer(self, title: str, raw_rows: list[list[str]], extra_col: Optional[str] = None) -> None:
        if not raw_rows:
            self._log('Nessun dato da mostrare.')
            return
        
        win = tk.Toplevel(self.root)
        win.title(title)
        
        win.columnconfigure(0, weight=1)
        win.rowconfigure(0, weight=1)

        cols = list(HEADERS_IT.values())
        if extra_col:
            cols.append(extra_col)
        tree = ttk.Treeview(win, columns=cols, show='headings')
        
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c)

        vsb = ttk.Scrollbar(win, orient='vertical', command=tree.yview)
        hsb = ttk.Scrollbar(win, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        for raw_row in raw_rows:
            output = raw_row + [''] * (len(cols) - len(raw_rows))
            tree.insert('', tk.END, values=output[:len(cols)])


def main():
    app = PingStoreApp()
    app.run()

if __name__ == '__main__':
    main()