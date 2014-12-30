import requests
from settings import HEADERS, URL, SHEETS
import xlrd
from operator import itemgetter
import copy

def getIncursions():

    response = requests.get(URL+'/incursions/', headers=HEADERS)
    response.raise_for_status()

    incursions = {}
    for i, item in enumerate(response.json()['items']):
        influence = item['influence']
        status = item['state']
        constellation = item['constellation']['id']
        name = item['constellation']['name']
        incursions[constellation] = {
            'id': i,
            'influence': influence,
            'status': status,
            'name': name
        }

    return incursions


def buildClusters(constellation):
    sheet = xlrd.open_workbook(SHEETS['SYSTEMJUMPS']).sheet_by_name('Sheet1')
    const_systems = getConstellationSystems(constellation)
    jumps = trimJumps(sheet, constellation)
    clusters = [[[sys], [jump[1] for jump in jumps if jump[0] == sys]] for sys in const_systems]

    while True:
        for cluster in clusters:
            stop = True
            for dest in cluster[1]:
                if dest in const_systems:
                    current = cluster[0] + [dest]
                    if sorted(current) not in [sorted(clust[0]) for clust in clusters]:
                        destinations = list({jump[1] for jump in jumps if jump[0] in current
                                             and jump[1] not in current})
                        clusters.append([current, destinations])
                        stop = False
        if stop:
            break
    return clusters


def processClusters(constellation, clusters):

    const_data = trimSystems(constellation)
    data_exists = False
    for sys in const_data.itervalues():
        if sys['type'] is not None:
            data_exists = True

    temp = copy.deepcopy(clusters)
    for cluster in clusters:
        novanguard = True
        for system in cluster[0]:
            if const_data[system]['type'] == 'vanguard':
                novanguard = False

        if data_exists:
            if novanguard:
                temp.remove(cluster)

    winners = sorted(temp, key=lambda cluster: len(cluster[1]))

    for winner in winners:
        for loser in winners:
            if len(loser[0]) < len(winner[0]) and len(winner[1]) <= len(loser[1]):
                if is_subset(loser[0], winner[0]):
                    winners.remove(loser)

    winners_full = winners[:5]
    for i, winner in enumerate(winners_full):
        for j, system in enumerate(winner[0]):
            winners_full[i][0][j] = {system: const_data[system]}


    return winners_full


def is_subset(list_one, list_two):
    return set(list_one) < set(list_two)


def trimSystems(constellation):
    sys_sheet = xlrd.open_workbook(SHEETS['SYSTEMDATA']).sheet_by_name('Sheet1')
    systems = {}
    inc_sheet = xlrd.open_workbook(SHEETS['INCURSIONDATA']).sheet_by_name('Sheet1')

    for rowidx in range(1, sys_sheet.nrows):
        const = int(sys_sheet.cell(rowidx, 1).value)
        if const == constellation:
            sysid = int(sys_sheet.cell(rowidx, 2).value)
            name = sys_sheet.cell(rowidx, 3).value
            sec = float(sys_sheet.cell(rowidx, 21).value)
            systype = None

            systems[sysid] = {
                'name': name,
                'sec': sec,
                'type': systype,
            }

    for rowid in range(1, inc_sheet.nrows):
        const = int(inc_sheet.cell(rowid, 0).value)
        if const == constellation:
            for colid in range(1, inc_sheet.ncols):
                if inc_sheet.cell(rowid, colid).value != "":
                    for sys in map(int, map(float, str(inc_sheet.cell(rowid, colid).value).split(','))):
                        systems[sys]['type'] = inc_sheet.cell(0, colid).value
            return systems
    return systems


def trimJumps(sheet, constellation):
    jumps = []

    for rowidx in range(1, sheet.nrows):
        fromcons = int(sheet.cell(rowidx, 1).value)
        if fromcons == constellation:
            fromsys = int(sheet.cell(rowidx, 2).value)
            tosys = int(sheet.cell(rowidx, 3).value)

            if [fromsys, tosys] not in jumps:
                jumps.append([fromsys, tosys])
            if [tosys, fromsys] not in jumps:
                jumps.append([tosys, fromsys])

    return jumps


def getConstellationSystems(constellation):
    sheet = xlrd.open_workbook(SHEETS['SYSTEMDATA']).sheet_by_name('Sheet1')

    systems = []
    for rowidx in range(1, sheet.nrows):
        if int(sheet.cell(rowidx, 1).value) == constellation:
            systems.append(int(sheet.cell(rowidx, 2).value))

    return systems


def incursions():
    incursions = getIncursions()
    for incursion in incursions:
        clusters = buildClusters(incursion)
        systems = trimSystems(incursion)
        incursions[incursion]['pockets'] = processClusters(incursion, clusters)
        winners = ''
        for cluster in incursions[incursion]['pockets']:
            winners += formatPockets(cluster)

        print '{id}) Constellation: {name}\nStatus: {status}, Influence: {influence}\nSystems: Staging: {staging}\
            VG: {vanguards}, AS: {assaults}, HQ: {hq}\nBest Pockets;\n{pockets}'.format(
            id=incursions[incursion]['id'],
            name=incursions[incursion]['name'],
            status=incursions[incursion]['status'],
            influence=incursions[incursion]['influence'],
            staging=''.join([systems[sys]['name'] for sys in systems if systems[sys]['type'] == 'staging']),
            vanguards=', '.join([systems[sys]['name'] for sys in systems if systems[sys]['type'] == 'vanguard']),
            assaults=', '.join([systems[sys]['name'] for sys in systems if systems[sys]['type'] == 'assault']),
            hq=', '.join([systems[sys]['name'] for sys in systems if systems[sys]['type'] == 'headquarters']),
            pockets=winners
        )

def formatPockets(pocket):

    line = ''
    for sys in pocket[0]:
        sys = sys.values()[0]
        t = ', '
        if sys['type'] == 'vanguard':
            t = '(VG), '
        elif sys['type'] == 'assault':
            t = '(AS), '
        elif sys['type'] == 'staging':
            t = '(ST), '
        elif sys['type'] == 'headquarters':
            t = '(HQ), '
        line += sys['name'] + t
    line += 'Entrances: ' + str(len(pocket[1])) + '\n'
    return line


incursions()

# clusters = buildClusters(20000252)
# processClusters(20000252, clusters)

#getIncursions()

