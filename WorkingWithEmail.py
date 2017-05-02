import imaplib, re, email.parser, json, shutil
import email

#listResponsePattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
#def parseListResponse(line):
#    flags, delimiter, mailbox_name = listResponsePattern.match(line).groups()
#    mailbox_name = mailbox_name.strip('')
#    return (flags, delimiter, mailbox_name)


def check_theme_of_msg(msg_id, theme):
    typ, msg_data = connection.fetch(msg_id, '(BODY.PEEK[HEADER])')
    header = email.message_from_bytes(msg_data[0][1])
    return theme in header


def get_WordOfTheDay_from_msg(msg_id):
    word_transcr_wordclass_search_pattern = re.compile(
        r'(\w+)\s+\\(.+)\\\s+(\w+)\s+')  # for mail resended (r'\w+\. \d+, \d+\s+(\w+)\s+\\(.+)\\\s+(\w+)\s+(.+)\s+Quotes')
    definition_search_pattern = re.compile(r'(\d\. [\w;. ]+)')
    typ, msg_data = connection.fetch(msg_id, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])
    if msg.get_content_maintype() == 'multipart':
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                plaintext = part.get_payload(decode=True)
                plaintext = plaintext.decode('utf-8')
                search_res = word_transcr_wordclass_search_pattern.findall(plaintext)
                if (len(search_res) == 0) or (len(search_res) > 1):
                    print(len(search_res))
                    print('Smth went wrong with msg №' + msg_id)
                    return
                else:
                    word, transcription, word_class = search_res[0]
                definition = definition_search_pattern.findall(plaintext)
    print('Get the word from msg №' + msg_id)
    return word, transcription, word_class, definition

with imaplib.IMAP4_SSL('imap.gmail.com', 993) as connection:  #Зачем надо imap?
    connection.login('Sl.aleksandr28@gmail.com', 'Vfkaehbjy365!')
    #try:
     #   typ, data = connection.list()
    #except:
    #    pass
    #for line in data:
    #    line = line.decode('utf-8')
    #    flags, delimiter, mailbox_name = parseListResponse(line)

    typ, data = connection.select('INBOX') #[Gmail]/&BBIEMAQ2BD0EPgQ1-
    typ, msg_ids = connection.search(None, '(UNSEEN)', '(FROM "doctor@dictionary.com" SUBJECT "Word of the Day")') #SUBJECT 'Word of the Day'
    msg_ids = msg_ids[0].decode('utf-8').split(' ')
    words = []
    word_dict = dict()
    if msg_ids == ['']:
        print('No new messages')
    else:
        print(len(msg_ids), ' new messages')

        for id in msg_ids:
            res = get_WordOfTheDay_from_msg(id)
            word_dict[res[0]] = {'pronunciation': res[1], 'word class': res[2], 'definition(s)': res[3]}
            words.append(res)

shutil.copy('C:/Users/Alex1_000/PycharmProjects/WebData/Bioinformatics1/WordsOfTheDay.', 'C:/Users/Alex1_000/PycharmProjects/WebData/Bioinformatics1/WordsOfTheDayBackUp')
with open('WordsOfTheDay', 'r') as file:

    old_words = json.load(file)

with open('WordsOfTheDay', 'w') as file:
    word_dict.update(old_words)
    json.dump(word_dict, file)
