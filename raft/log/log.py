import json


class Log:
    def __init__(self, entry, term, client_rank):
        self.entry = entry
        self.term = term
        self.client_rank = client_rank


class LogManager:
    def __init__(self, rank):
        self.log = []
        self.rank = rank

    def append_entries(self, entries):
        for entry in entries:
            self.log.append(entry)


    def insert_entries(self, entries, index):
        entries.reverse()
        for entry in entries:
            self.log.insert(index, entry)
        self.log = self.log[:(index + len(entries))]

    def commit(self, srcIndex, tgtIndex):
        if srcIndex == tgtIndex:
            return
        filename = str(self.rank) + ".log"
        with open(filename, 'a+') as f:
            write_str = ""
            for index in range(srcIndex, tgtIndex):
                cur_log = self.log[index]
                write_str += str(cur_log.client_rank) + ',' + str(cur_log.term) + ',' + str(cur_log.entry) + '\n'
            f.write(write_str)


    def append_entry(self, entry):
        self.log.append(entry)

    def last_log_index(self):
        return len(self.log) - 1
        #return max(0, len(self.log) -1)

    def last_log_term(self):
        return 0 if not len(self.log) else self.log[len(self.log) -1].term

    def append_client_entry(self, entry, term, client_rank):
        self.log.append(Log(entry, term, client_rank))

    def next_index(self):
        return len(self.log)

    def is_out_of_bound(self, index):
        return index < 0 or index >= len(self.log)

    def term_at_index(self, index):
        return 0 if self.is_out_of_bound(index) else self.log[index].term
    
    def entries_from_index(self, index):
        return self.log[index:]
    
    def entry_from_index(self, index):
        return [] if self.is_out_of_bound(index) else [self.log[index]]