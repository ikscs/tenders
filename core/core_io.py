import datetime
import pandas as pd
from sqlalchemy import create_engine
import traceback

try:
    from core.credentials import DB
except Exception:
    from credentials import DB

LOG_FNAME = "tender_log.txt"
engine_str = f"mysql+pymysql://{DB['user']}:{DB['password']}@{DB['host']}/{DB['database']}"

def add_record(table, id_klient, tender, path = None):
    if path == None:
        engine = create_engine(engine_str)
    else:
        engine = create_engine('sqlite:///' + path, echo=False)

    try:
        df = pd.DataFrame.from_dict({'id_klient': [id_klient], 'date': [datetime.datetime.now()], 'tender': [tender]})
        df.to_sql(table, con=engine, if_exists='append', index=False, dtype=None)
#        df.to_sql(table, con=engine, if_exists='replace', index=False, dtype=None)
    except Exception as err:
        log_error(str(err))
        return 0
    return 1

def load_table(table, columns, path = None):
    if path == None:
        engine = create_engine(engine_str)
    else:
        engine = create_engine('sqlite:///' + path, echo=False)

    try:
        df = pd.read_sql(f'SELECT {columns} from {table}', con=engine, parse_dates=['date'])
        result = df.values.tolist()
    except Exception as err:
        log_error(str(err))
        result = []
    return result

def log_error(s):
     _log(s, is_error = True)

def log_info(s):
     _log(s, is_error = False)

def _log(s, is_error):
    with open(LOG_FNAME, 'a', encoding='utf-8') as f:
        f.write('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n')
        f.write(s + '\n')
        if is_error:
            traceback.print_exc(file=f)
