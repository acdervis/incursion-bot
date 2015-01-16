import incursion
import json
from flask import Response


def process(data):

    if type(data) == type(None):
        return "No text found."


    if data == '!inc':
        incursions = incursion.getIncursionList()
        incursions.sort()
        d = {'text': ', '.join(incursions)}
        response = Response(json.dumps(d), mimetype='text/json')

        return response
    else:
        if data.split()[0] == '!inc':
            arg = data.split()[1]
            inc = incursion.getIncursion(arg)
            if type(inc) is int:
                return "Incursion not found."
            if arg == inc.constellation.name:
                d = {
                    'name': inc.constellation.name,
                    'state': inc.state,
                    'influence': inc.influence,
                    'sysdata': inc.getSystemTypes(),
                    'pockets': inc.getBestClusters(),
                }
                body = {'text': incursion.template_incursioninformation.substitute(d)}
                response = Response(json.dumps(body), mimetype='text/json')
                return response
            else:
                return "Constellation not found under active incursions."
        else:
            return "Bad request."

