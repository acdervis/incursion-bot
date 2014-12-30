import xlrd


def processConstellations():
    book = xlrd.open_workbook('constellations.xlsx')
    sheet = book.sheet_by_name('result')

    incursion_map = {}

    for rowidx in range(1, sheet.nrows):
        constellation = int(sheet.cell(rowidx, 0).value)
        staging = int(sheet.cell(rowidx, 1).value)
        if sheet.cell(rowidx, 2).value != '':
            vanguard = map(int, sheet.cell(rowidx, 2).value.split(','))
        else: vanguard = []
        if sheet.cell(rowidx, 3).value != '':
            assault = map(int, sheet.cell(rowidx, 3).value.split(','))
        else: assault = []
        if sheet.cell(rowidx, 4).value != '':
            headquarters = map(int, sheet.cell(rowidx, 4).value.split(','))
        else: headquarters = []

        incursion_map[constellation] = {
                'staging': staging,
                'vanguard': vanguard,
                'assault': assault,
                'headquarters': headquarters,
            }

    return incursion_map