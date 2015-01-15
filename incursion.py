import requests
from settings import HEADERS, URL, SHEETS
from classes import *
from string import Template

template_incursioninformation = Template(
    "Constellation: $name\nStatus: $state, Influence: $influence\n$sysdata\nBest Pockets;\n$pockets\n"
)

mail_war = (
    "<font size=\"12\" color=\"#bfffffff\"></font><font size=\"24\" color=\"#ffff0000\"><b>We are currently AT war, be "
    "careful and ask for help if you don't have a valet</b><br><br></font>"
)

mail_body = Template(
    (
        "<font size=\"12\" color=\"#bfffffff\">New focus is in the </font><font size=\"12\" color=\"#ffffa600\">"
        "<a href=\"showinfo:4//${constid}\">${constname}</a></font><font size=\"12\" color=\"#bfffffff\"> constellation "
        "in the </font><font size=\"12\" color=\"#ffffa600\"><a href=\"showinfo:3//${regionid}\">${regionname}</a></font>"
        "<font size=\"12\" color=\"#bfffffff\"> region (see </font><font size=\"12\" color=\"#ffffa600\">"
        "<a href=\"http://evemaps.dotlan.net/map/${regionname}#kills\">dotlan</a></font><font size=\"12\" color=\"#bfffffff\"> "
        "for more information).<br><br></font>{systems}<font size=\"12\" color=\"#ff00ff00\">Recommended station:</font>"
        "<font size=\"12\" color=\"#bfffffff\"> </font><font size=\"12\" color=\"#ffffa600\">{station}"
    )
)

mail_base = (
    "<a href=\"showinfo:2497//60014140\">Zemalu IX - Moon 2 - Thukker Mix Factory</a></font>"
    "<font size=\"12\" color=\"#bfffffff\"> [Run here it only needs 1 picket]<br><br></font>"
    "<font size=\"12\" color=\"#ff00ff00\">Picket Systems:</font><font size=\"12\" color=\"#bfffffff\"> </font>"
    "<font size=\"12\" color=\"#ffffa600\"><a href=\"showinfo:5//30000052\">Maspah</a></font>"
    "<font size=\"12\" color=\"#bfffffff\"> (1j warning) <br><br>Please read through the </font>"
    "<font size=\"12\" color=\"#ffffa600\"><a href=\"http://wiki.eveuniversity.org/Incursions_checklist\">"
    "Incursions checklist</a></font><font size=\"12\" color=\"#bfffffff\"> so you are familiar with our practices and "
    "safeguards. Also look over to </font><font size=\"12\" color=\"#ffffa600\"><a href=\"http://wiki.eveuniversity.org/"
    "Roles_in_Incursions\">Roles in Incursions</a></font><font size=\"12\" color=\"#bfffffff\"> see how you can help "
    "out more.<br><br>Fly safe and remember to take the necessary precautions while </font>"
    "<font size=\"12\" color=\"#ffffa600\"><a href=\"http://wiki.eveuniversity.org/How_to_find_Incursions#"
    "Moving_between_Incursions\">Moving between Incursions</a></font><font size=\"12\" color=\"#bfffffff\">. "
    "Assume that war targets are always around, don't get lulled into a false sense of security.</font>"
)

def strSystems(incursion):
    if not incursion.has_data():
        return ''

    r = ''
    for system in incursion.staging:
        r += (
            "<font size=\"12\" color=\"#ff007fff\">Scout system: </font><font size=\"12\" color=\"#ffffa600\">"
            "<a href=\"showinfo:5//%i\">%s</a></font><font size=\"12\" color=\"#ff007fff\"> </font>"
            "<font size=\"12\" color=\"#bfffffff\"> <br></font>"
        ) % (system.id, system.name)
    r += '<font size=\"12\" color=\"#ff007fff\">Vanguard systems: </font>'
    for system in incursion.vanguards:
        r += (
            "<font size=\"12\" color=\"#ffffa600\"><a href=\"showinfo:5//%i\">%s</a></font>"
            "<font size=\"12\" color=\"#ff007fff\">, </font>"
        ) % (system.id, system.name)
    r += '<font size=\"12\" color=\"#bfffffff\"> <br></font><font size=\"12\" color=\"#ff007fff\">Assault system: </font>'
    for system in incursion.assaults:
        r += (
            "<font size=\"12\" color=\"#ffffa600\"><a href=\"showinfo:5//%i\">%s</a></font>"
            "<font size=\"12\" color=\"#ff007fff\">, </font>"
        ) % (system.id, system.name)
    r += '<font size=\"12\" color=\"#bfffffff\"> <br></font><font size=\"12\" color=\"#ff007fff\">Headquarter system: </font>'
    for system in incursion.headquarters:
        r += (
            "<font size=\"12\" color=\"#ffffa600\"><a href=\"showinfo:5//%i\">%s</a></font>"
        ) % (system.id, system.name)
    r += '"<font size=\"12\" color=\"#ff007fff\"> <br><br></font>'
    return r



def getIncursions(short=False):

    response = requests.get(URL+'/incursions/', headers=HEADERS)
    response.raise_for_status()

    incursions = []

    for item in response.json()['items']:
        print item['constellation']['name']
        new_const = Constellation(
                ID=item['constellation']['id'],
                name=item['constellation']['name'],
            )
        if not short:
            new_const.setSystems()
            new_const.buildClusters()
            new_const.setIncData()
        new_inc = Incursion(
            constellation=new_const,
            influence=item['influence'],
            state=item['state'],
            hasboss=item['hasBoss'],
        )
        if not short:
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
