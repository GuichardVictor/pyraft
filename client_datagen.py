import sys
import argparse
import random
import urllib.request

def build_log():    
    word_url = "http://www.mieliestronk.com/corncob_lowercase.txt"

    response = urllib.request.urlopen(word_url)
    long_txt = response.read().decode()
    words = long_txt.splitlines()

    return words

LOGS = build_log()

def generate(log_size):
    client_log_size = random.randint(log_size // 2, log_size * 2)

    return random.choices(LOGS, k=client_log_size)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate Client Command list')
    parser.add_argument('--nb_client', type=int, default=1,
                        help='the number of client file to generate')
    parser.add_argument('--mean_log_size', type=int, default=5,
                        help='the mean size of a client log')
    parser.add_argument('--filename', type=str, default='client_log',
                        help='filename without extension to use (filename)_(client_num).log')

    args = parser.parse_args()

    nb_client = args.nb_client
    log_size = args.mean_log_size
    filename = args.filename

    for i in range(nb_client):
        
        client_log = generate(log_size)

        with open(f'{filename}_{i+1}.log', 'w') as f:
            f.write('\n'.join(client_log))