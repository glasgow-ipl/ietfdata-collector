from imapclient import IMAPClient

server = IMAPClient("imap.ietf.org", use_uid=True, ssl=False)
server.login("anonymous", "csp@csperkins.org")
for (flags, delimiter, name) in server.list_folders():
    if flags == ():
        folder = server.select_folder(name, readonly=True)
        print('{:6d} messages in {}'.format(folder[b'EXISTS'], name))
        for msg_id in server.search():
            msg = server.fetch(msg_id, ["RFC822"])[msg_id]
            print(msg)
            print("")


