import incursion
import json
from flask import Response


def process(data):

    print type(data)
    if type(data) == type(None):
        return "No text found."

    print data

    if data == '!inc':
        incursions = incursion.getIncursionList()
        incursions.sort()
        d = {'text': ', '.join(incursions)}
        response = Response(json.dumps(d), mimetype='text/json')

        print response.get_data()
        return response
    else:
        if data.split()[0] == '!inc':
            arg = data.split()[1]
            inc = incursion.getIncursion(arg)
            if arg == inc.constellation.name:
                d = {
                    'name': inc.constellation.name,
                    'state': inc.state,
                    'influence': inc.influence,
                    'sysdata': inc.getSystemTypes(),
                    'pockets': inc.getBestClusters(),
                }
                found = True
                body = {'text': incursion.template_incursioninformation.substitute(d)}
                response = Response(json.dumps(body), mimetype='text/json')
                return response
            else:
                return "Constellation not found under active incursions."
        else:
            return "Bad request."

