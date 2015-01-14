import incursion


def process(data):

    print type(data)
    if type(data) == type(None):
        return "NoneType"

    print data

    if data['text'].split()[0] == '!inc':
        if len(data['text'].split()) >= 2:
            print data['text'].split()[1]
        else:
            text = ""
            incursions = incursion.getIncursions(short=True)
            for inc in incursions:
                text += inc.constellation.name + ', '
            return text



