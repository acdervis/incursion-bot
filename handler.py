import incursion
import json
from flask import Response


def process(data):

    print type(data)
    if type(data) == type(None):
        return "NoneType"

    print data

    if data == '!inc':
        constellations = []
        incursions = incursion.getIncursions(short=True)
        for inc in incursions:
            constellations.append(inc.constellation.name)

        constellations.sort()
        d = {'text': ', '.join(constellations)}
        response = Response(json.dumps(d), mimetype='text/json')

        print response.get_data()
        return response
    else:
        if data.split()[0] == '!inc':
            arg = data.split()[1]
            incursions = incursion.getIncursions()
            found = False
            for inc in incursions:
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
            if found:
                response = Response(json.dumps(d), mimetype='text/json')
            else:
                return "Constellation not found under active incursions."
        else:
            return "Bad request."

