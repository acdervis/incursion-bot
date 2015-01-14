import incursion
import json

def process(data):

    print type(data)
    if type(data) == type(None):
        return "NoneType"

    print data

    if data['text'].split()[0] == '!inc':
        text = ""
        if len(data['text'].split()) >= 2:
            print data['text'].split()[1]
        else:
            incursions = incursion.getIncursions(short=True)
            for inc in incursions:
                text += inc.constellation.name + ', '

        d = {'text': text}
        return json.dumps(d)
