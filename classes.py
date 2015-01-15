import xlrd
from settings import SHEETS

SYS_SHEET = xlrd.open_workbook(SHEETS['SYSTEMDATA']).sheet_by_name('Sheet1')
JUMP_SHEET = xlrd.open_workbook(SHEETS['SYSTEMJUMPS']).sheet_by_name('Sheet1')
INC_SHEET = xlrd.open_workbook(SHEETS['INCURSIONDATA']).sheet_by_name('Sheet1')


def is_subset(list_one, list_two):
    return set(list_one) < set(list_two)


class Incursion():

    def getSystemTypes(self):
        if not self.has_data():
            return 'No data about VG/AS/HQ.'
        s = ''
        s += ' ST: ' + ', '.join([x.name for x in self.staging])
        s += ' VG: ' + ', '.join([x.name for x in self.vanguards])
        s += ' AS: ' + ', '.join([x.name for x in self.assaults])
        s += ' HQ: ' + ', '.join([x.name for x in self.headquarters])
        return s

    def getBestClusters(self):
        return self.constellation.getBestClusters()

    def setSystemTypes(self):
        if self.constellation is None:
            msg = "Constellation for Incursion not set."
            raise Exception(msg)
        if not self.has_data():
            return

        self.staging = self.constellation.staging()
        self.vanguards = self.constellation.vanguards()
        self.assaults = self.constellation.assaults()
        self.headquarters = self.constellation.headquarters()

    def has_data(self):
        for sys in self.constellation.systems:
            if sys.type != "":
                return True
        return False

    def __init__(self, constellation=None, influence=0, hasboss=False, state="Established"):
        self.influence = influence
        self.hasboss = hasboss
        self.state = state
        self.constellation = constellation
        self.typedata = False
        self.staging = []
        self.vanguards = []
        self.assaults = []
        self.headquarters = []


class Constellation():

    def buildClusters(self):
        self.has_systems()

        self.clusters = []
        for sys in self.systems:
            new_cluster = Cluster(systems=[sys])
            new_cluster.setConnections()
            self.clusters.append(new_cluster)

        while True:
            added = False
            for cluster in self.clusters:
                for sys in cluster.connections:
                    if sys.constellation == self.ID:
                        new_set = cluster.systems+[sys]
                        stop = False
                        for pocket in self.clusters:
                            if sorted([x.ID for x in new_set]) == sorted([x.ID for x in pocket.systems]):
                                stop = True
                        if stop:
                            break
                        new_cluster = Cluster(systems=new_set)
                        new_cluster.setConnections()
                        self.clusters.append(new_cluster)
                        added = True
            if not added:
                break

    def getBestClusters(self, highseconly=False, preferred='vanguard'):
        winners = []

        for cluster in self.clusters:
            if highseconly and "L" in [x.sectype for x in cluster.systems]:
                continue
            if preferred not in [x.type for x in cluster.systems] and self.hasincdata:
                continue
            winners.append(cluster)

        sorted(winners, key=lambda x: x.conn_count)
        for winner in winners:
            for loser in winners:
                if loser.conn_count >= winner.conn_count and len(loser.systems) < len(winner.systems):
                    if is_subset([x.ID for x in loser.systems], [x.ID for x in winner.systems]):
                        winners.remove(loser)

        result = ''
        for winner in winners[:5]:
            line = ''
            for i, sys in enumerate(winner.systems):
                t = ', '
                if sys.type == 'vanguard':
                    t = '(VG), '
                elif sys.type == 'assault':
                    t = '(AS), '
                elif sys.type == 'staging':
                    t = '(ST), '
                elif sys.type == 'headquarters':
                    t = '(HQ), '
                line += sys.name + t
            result += line + 'Entrances: ' + ', '.join([x.name for x in winner.connections]) + ' Count: %i' % winner.conn_count + '\n'

        return result

    def setSystems(self):
        sheet = SYS_SHEET
        l = []
        for rowidx in range(1, sheet.nrows):
            if int(float(sheet.cell(rowidx, 1).value)) == self.ID:
                new_sys = System(ID=int(float(sheet.cell(rowidx, 2).value)), constellation=self.ID)
                new_sys.initData(sheet, rowid=rowidx)
                new_sys.initConnections(sheet=JUMP_SHEET)
                new_sys.setIncData()
                l.append(new_sys)
        self.systems = l

    def has_systems(self):
        if not self.systems:
            self.setSystems()

    def staging(self):
        self.has_systems()
        l = []
        for system in self.systems:
            if system.type == 'staging':
                l.append(system)
        return l

    def vanguards(self):
        self.has_systems()
        l = []
        for system in self.systems:
            if system.type == 'vanguard':
                l.append(system)
        return l

    def assaults(self):
        self.has_systems()
        l = []
        for system in self.systems:
            if system.type == 'assault':
                l.append(system)
        return l

    def headquarters(self):
        self.has_systems()
        l = []
        for system in self.systems:
            if system.type == 'headquarters':
                l.append(system)
        return l

    def constCluster(self):
        self.has_systems()

        new_cluster = Cluster(systems=self.systems)
        new_cluster.setConnections()
        return new_cluster

    def setIncData(self):
        sheet = INC_SHEET
        for rowidx in range(1, sheet.nrows):
            if int(sheet.cell(rowidx, 0).value) == self.ID:
                if (
                        (str(sheet.cell(rowidx, 1).value) != "") and
                        (str(sheet.cell(rowidx, 2).value) != "") and
                        (str(sheet.cell(rowidx, 3).value) != "") and
                        (str(sheet.cell(rowidx, 4).value) != "")
                ):
                    self.hasincdata = True
                    self.has_systems()
                    for sys in self.systems:
                        sys.setIncData(rowid=rowidx)

    def __init__(self, ID=0, name="", region=0, systems=None, connections=None):
        self.ID = ID
        self.name = name
        if systems is None:
            systems = []
        self.systems = systems
        self.region = region
        self.clusters = None
        if connections is None:
            connections = []
        self.connections = connections
        self.hasincdata = False
        self.const_cluster = self.constCluster()


class System():

    def initData(self, sheet, rowid=0):
        if rowid != 0 and int(sheet.cell(rowid, 2).value) == self.ID:
            self.name = sheet.cell(rowid, 3).value
            self.security = float(sheet.cell(rowid, 21).value)
            self.constellation = int(sheet.cell(rowid, 1).value)
            self.setSecurity()
        else:
            for rowidx in range(1, sheet.nrows):
                if self.ID == int(sheet.cell(rowidx, 2).value):
                    self.name = sheet.cell(rowidx, 3).value
                    self.security = float(sheet.cell(rowidx, 21).value)
                    self.constellation = int(sheet.cell(rowidx, 1).value)
                    self.setSecurity()

    def initConnections(self, sheet, rowid=0):
        self.connections = []
        if rowid != 0 and int(sheet.cell(rowid, 2).value) == self.ID:
            new_sys = System(ID=int(sheet.cell(rowid, 3).value))
            new_sys.initData(SYS_SHEET)
            self.connections.append(new_sys)
        else:
            for rowidx in range(1, sheet.nrows):
                if self.ID == int(sheet.cell(rowidx, 2).value):
                    new_sys = System(ID=int(sheet.cell(rowidx, 3).value))
                    new_sys.initData(SYS_SHEET)
                    self.connections.append(new_sys)

    def setIncData(self, rowid=0):
        sheet = INC_SHEET
        for rowidx in range(1, sheet.nrows):
            if self.constellation == int(sheet.cell(rowidx, 0).value):
                for colidx in range(1, sheet.ncols):
                    if sheet.cell(rowidx, colidx).value != "":
                        if self.ID in map(int, map(float, str(sheet.cell(rowidx, colidx).value).split(','))):
                            self.type = sheet.cell(0, colidx).value
                            return

    def has_connections(self):
        if not self.connections:
            self.initConnections(JUMP_SHEET)

    def setSecurity(self):
        if self.security >= 0.5:
            self.sectype = "H"
        elif self.security <= 0.0:
            self.sectype = "N"
        else:
            self.sectype = "L"

    def is_nullsec(self):
        return self.sectype == "N"

    def is_highsec(self):
        return self.sectype == "H"

    def is_lowsec(self):
        return self.sectype == "L"

    def __init__(self, ID=0, name="", security=None, constellation=0, type="", connections=None):
        self.ID = ID
        self.name = name
        self.security = security
        if security is not None:
            self.setSecurity()
        else:
            self.sectype = None
        self.constellation = constellation
        self.type = type
        if connections is None:
            connections = []
        self.connections = connections


class Cluster():

    def setConnections(self):
        self.connections = []
        for conn in [x for y in self.systems for x in y.connections]:
            if conn.ID not in [x.ID for x in self.systems]:
                if conn.ID not in [x.ID for x in self.connections]:
                    self.connections.append(conn)
        self.conn_count = len(self.connections)

    def __init__(self, systems=None, connections=None):
        if systems is None:
            systems = []
        self.systems = systems
        if connections is None:
            connections = []
        self.connections = connections
        self.conn_count = 0
