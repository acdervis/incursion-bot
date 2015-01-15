import incursion
import json
from flask import Response

def process(data):

    print type(data)
    if type(data) == type(None):
        return "NoneType"

    print data

    if data == '!inc':
        text = ""
        # if len(data.split()) >= 2:
        #     print data.split()[1]
        # else:
        incursions = incursion.getIncursions(short=True)
        for inc in incursions:
            text += inc.constellation.name + ', '

        d = {'text': text}
        response = Response(json.dumps(d), mimetype='text/json')

        print response.get_data()
        return response
    else:
        return "No data provided."
