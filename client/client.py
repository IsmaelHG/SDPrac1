import xmlrpc.client

if __name__ == '__main__':
    proxy = xmlrpc.client.ServerProxy('http://localhost:9000')
    print(proxy.add_worker())
    print(proxy.add_worker())
    print(proxy.add_worker())
    print(proxy.add_worker())
    print(proxy.list_workers())

