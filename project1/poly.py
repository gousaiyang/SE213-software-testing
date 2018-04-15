import sys
import socket
import logging
import threading

welcome_text = '''Welcome to my Polynomial Pretty Print service!

Example:
Input coefficients (high to low degree, space delimited): 3 -2 6.7 0 1 -0.3
The polynomial is: 3x^5-2x^4+6.7x^3+x-0.3

'''

def is_int(x):
    return int(x) == x

def try_write(fout, content):
    try:
        fout.write(content)
    except:
        pass

def welcome(fout):
    try_write(fout, welcome_text)

def bye(fout):
    try_write(fout, 'Bye!\n')

def read_coeff(fin, fout):
    try:
        fout.write('Input coefficients: ')
        fout.flush()
    except:
        return None

    try:
        data = fin.readline().strip()
        assert data
    except:
        bye(fout)
        return None

    try:
        coeffs = [float(_) for _ in data.split(' ') if _]
        lc = len(coeffs)
        assert lc > 0
    except:
        try_write(fout, 'Invalid coefficient list. Space delimited real numbers expected.\n')
        return None

    if lc > 1 and coeffs[0] == 0:
        try_write(fout, 'The highest degree of a non-constant polynomial cannot be zero.\n')
        return None

    return [(int(c) if is_int(c) else c) for c in coeffs]

def pretty_print(coeffs, fout):
    try_write(fout, 'The polynomial is: ')

    degree = len(coeffs) - 1
    first_done = False

    if degree == 0:
        try_write(fout, str(coeffs[0]) + '\n')
        return

    for coeff in coeffs:
        if coeff == 0:
            degree -= 1
            continue

        sign = ''
        if coeff < 0 or first_done:
            sign = '+' if coeff > 0 else '-'

        value = str(abs(coeff))
        if value == '1' and degree > 0:
            value = ''

        if degree >= 2:
            exp = 'x^' + str(degree)
        elif degree == 1:
            exp = 'x'
        else:
            exp = ''

        try_write(fout, sign + value + exp)

        first_done = True
        degree -= 1

    try_write(fout, '\n')

def serve(fin, fout):
    welcome(fout)

    coeffs = read_coeff(fin, fout)

    if not coeffs:
        return

    pretty_print(coeffs, fout)

    bye(fout)

def serve_console():
    serve(sys.stdin, sys.stdout)

def handle_client(conn, clientaddr):
    try:
        with conn.makefile('r') as fin, conn.makefile('w') as fout:
            serve(fin, fout)
    except:
        logging.exception('Some error happened.')
    finally:
        conn.close()
        logging.info('Connection from %s closed.', clientaddr)

def serve_socket(port, addr=None, use_ipv6=False):
    logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)

    try:
        if use_ipv6:
            addr = addr or '::'
            logging.info('Serving on [%s]:%d', addr, port)
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            addr = addr or '0.0.0.0'
            logging.info('Serving on %s:%d', addr, port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.bind((addr, port))
        s.listen()

        while True:
            conn, clientaddr = s.accept()
            conn.settimeout(60)
            logging.info('Connection from %s accepted.', clientaddr)

            thread = threading.Thread(target=handle_client, args=(conn, clientaddr))
            thread.setDaemon(True)
            thread.start()

    except KeyboardInterrupt:
        logging.critical('Ctrl+C received, shutting down server...')
        sys.exit(0)
    except:
        logging.exception('Some error happened.')
        sys.exit(-1)

if __name__ == '__main__':
    # serve_console()
    serve_socket(1234)
