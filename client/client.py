import xmlrpc.client

if __name__ == '__main__':
    proxy = xmlrpc.client.ServerProxy('http://localhost:9000')
    print(proxy.submit_countingwords("[http://localhost:8000/fitxer1, http://localhost:8000/fitxer2]"))


