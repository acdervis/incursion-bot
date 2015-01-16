import requests
from settings import HEADERS, URL
from classes import *
from string import Template

template_incursioninformation = Template(
    "Constellation: $name\nStatus: $state, Influence: $influence\n$sysdata\nBest Pockets;\n$pockets\n"
)


def getIncursionList():
    response = requests.get(URL+'/incursions/', headers=HEADERS)
    response.raise_for_status()

    incursions = []

    for item in response.json()['items']:
        incursions.append(item['constellation']['name'])
    return incursions


def getIncursion(const_name):

    response = requests.get(URL+'/incursions/', headers=HEADERS)
    response.raise_for_status()

    for item in response.json()['items']:
        if const_name == item['constellation']['name']:
            new_const = Constellation(
                ID=item['constellation']['id'],
                name=item['constellation']['name'],
            )
            new_const.setSystems()
            new_const.setIncData()
            new_inc = Incursion(
                constellation=new_const,
                influence=item['influence'],
                state=item['state'],
                hasboss=item['hasBoss'],
            )
            new_inc.setSystemTypes()
            new_inc.constellation.buildClusters()
            return new_inc
    return 0

def getIncursions(short=False):

    response = requests.get(URL+'/incursions/', headers=HEADERS)
    response.raise_for_status()

    incursions = []

    for item in response.json()['items']:
        new_const = Constellation(
                ID=item['constellation']['id'],
                name=item['constellation']['name'],
            )
        if not short:
            new_const.setSystems()
            new_const.setIncData()
        new_inc = Incursion(
            constellation=new_const,
            influence=item['influence'],
            state=item['state'],
            hasboss=item['hasBoss'],
        )
        if not short:
            new_inc.setSystemTypes()
            new_inc.constellation.buildClusters()
        incursions.append(new_inc)

    return incursions