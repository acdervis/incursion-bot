import requests
from settings import HEADERS, URL, SHEETS
from classes import *
from string import Template

template_incursioninformation = Template(
    "${id}) Constellation: $name\nStatus: $state, Influence: $influence\n$sysdata\nBest Pockets;\n$pockets\n\n"
)

def getIncursions():

    response = requests.get(URL+'/incursions/', headers=HEADERS)
    response.raise_for_status()

    incursions = []

    for item in response.json()['items']:
        print item['constellation']['name']
        new_const = Constellation(
                ID=item['constellation']['id'],
                name=item['constellation']['name'],
            )
        new_const.setSystems()
        new_const.buildClusters()
        new_const.setIncData()
        new_inc = Incursion(
            constellation=new_const,
            influence=item['influence'],
            state=item['state'],
            hasboss=item['hasBoss'],
        )
        new_inc.setSystemTypes()
        incursions.append(new_inc)

    return incursions


def user():
    incursions = getIncursions()

    for i, incursion in enumerate(incursions):
        d = {
            'id': i,
            'name': incursion.constellation.name,
            'state': incursion.state,
            'influence': incursion.influence,
            'sysdata': incursion.getSystemTypes(),
            'pockets': incursion.getBestClusters(),
        }

        print template_incursioninformation.substitute(d)

user()
print "Done!"