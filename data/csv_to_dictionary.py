import csv
import pprint

header = []
data = []
with open('TPB & RAK Cellar 2020-03-31.csv', mode='r') as csv_file:
    reader = csv.reader(csv_file)
    row_number = 0

    for row in reader:
        item = 0
        beer = {}

        if row_number == 0:
            header = row
        else:
            while item < len(row):
                # Remove any leading/trailing spaces
                if isinstance(header[item], str):
                    header[item] = header[item].strip()

                if header[item] not in ['ignore_bottle_date', 'is_cold', 'sell']:
                    if header[item] in ['year', 'qty']:
                        if '?' in row[item]:
                            if len(row[item]) == 1:
                                row[item] = 0
                            else:
                                row[item] = row[item].replace('?', '')
                        # print(row, item, row[item])
                        try:
                            beer[header[item]] = int(row[item])
                        except ValueError:
                            if beer['producer'] != '':
                                beer[header[item]] = int("20" + row[item].split('-')[1])
                    elif header[item] == 'for_trade':
                        # Convert to bool
                        beer[header[item]] = True if row[item] else False
                    else:
                        beer[header[item]] = row[item]
                item += 1

            if beer['producer'] != '':
                data.append(beer)

        row_number += 1

    # data = {rows[0]: rows[1] for rows in reader}

pprint.pprint(data)
print(len(data), "unique rows")
