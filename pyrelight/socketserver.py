# Inspired by https://realpython.com/python-sockets/

import pathlib
import selectors
import socket
import types


BUFSIZE = 1024


def listen(pathname, respond):
    try:
        pathlib.Path(pathname).unlink()
    except FileNotFoundError:
        pass
    sel = selectors.DefaultSelector()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.bind(pathname)
        sock.listen()
        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ, data=None)
        while True:
            for key, mask in sel.select(timeout=None):
                if key.data is None:
                    accept(sel, key.fileobj)
                else:
                    service(sel, key, mask, respond)


def accept(sel, sock):
    conn, _ = sock.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(inb=bytes(), outb=bytes())
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)


def service(sel, key, mask, respond):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(BUFSIZE)
        if recv_data:
            data.inb += recv_data
        else:
            sel.unregister(sock)
            sock.close()
    process(data, respond)
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


def process(data, respond):
    while True:
        try:
            idx = data.inb.index(b"\n")
        except ValueError:
            return
        msg = data.inb[:idx].decode()
        response = respond(msg).encode()
        data.inb = data.inb[idx + 1 :]
        data.outb += response + b"\n"
