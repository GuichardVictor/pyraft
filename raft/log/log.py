class Log:
    ''' Representation of a log

    Args:
        entry: log content
        term: server term
        client_rank: id of client that issued this log 
    '''
    def __init__(self, entry, term, client_rank):
        self.entry = entry
        self.term = term
        self.client_rank = client_rank


class LogManager:
    ''' Manage logs of a server
    
    Args:
        rank: server id
    '''
    def __init__(self, rank):
        self.log = []
        self.rank = rank

    def append_entries(self, entries):
        for entry in entries:
            self.log.append(entry)

    def insert_entries(self, entries, index):
        ''' Insert entries at index and removes following entries '''
        entries.reverse()

        for entry in entries:
            self.log.insert(index, entry)

        self.log = self.log[:(index + len(entries))]

    def commit(self, src_index, tgt_index):
        ''' Commit logs from src_index to tgt_index file '''
        if src_index == tgt_index:
            return
        filename = f'{self.rank}.log'
        with open(filename, 'a+') as f:
            write_str = ''
            for index in range(src_index, tgt_index):
                cur_log = self.log[index]
                write_str += f'{cur_log.client_rank},{cur_log.term},{cur_log.entry}\n'
            f.write(write_str)

    def append_entry(self, entry):
        self.log.append(entry)

    def last_log_index(self):
        return len(self.log) - 1

    def last_log_term(self):
        ''' Return term of last log if exists, else returns 0 '''
        return 0 if not len(self.log) else self.log[len(self.log) -1].term

    def append_client_entry(self, entry, term, client_rank):
        self.log.append(Log(entry, term, client_rank))

    def is_out_of_bound(self, index):
        return index < 0 or index >= len(self.log)

    def term_at_index(self, index):
        ''' Return term of log at given index if exists, else returns 0 '''
        return 0 if self.is_out_of_bound(index) else self.log[index].term
    
    def entries_from_index(self, index):
        return self.log[index:]
    
    def entry_from_index(self, index):
        return [] if self.is_out_of_bound(index) else [self.log[index]]