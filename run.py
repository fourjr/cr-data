#!/usr/bin/env python
"""
Generate data JSON from APK CSV source.
"""

import csv
import glob
import json
import os

import yaml

if __name__ == '__main__':
    TID = {}
    for i in os.listdir('csv/texts'):
        with open(f'csv/texts/{i}', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            title = reader.fieldnames
            for n, row in enumerate(reader):
                if n == 0:
                    continue
                TID[row['v']] = row['EN']

    try:
        with open('config.yml', encoding='utf-8') as f:
            config = yaml.load(f)
    except FileNotFoundError:
        config = {'id': []}

    csv_files = glob.iglob('csv/csv_*/**/*.csv', recursive=True)

    for fp in csv_files:
        fn = os.path.split(fp)[1]

        with open(fp, encoding='utf-8') as f:
            reader = csv.DictReader(f)

            title = reader.fieldnames

            data = []
            for n, row in enumerate(reader):
                if n == 0:
                    continue
                data.append({title[i][:1].lower() + title[i][1:]: row[title[i]] for i in range(len(title))})

            for n, i in enumerate(data):
                if fn in config['id']:
                    i['id'] = config['id'][fn] + n
                for j in i:
                    if isinstance(i[j], str):
                        if i[j].startswith('TID_'):
                            try:
                                i[j] = TID[i[j]]
                            except KeyError:
                                pass

                        # Typing
                        elif '.' in i[j]:
                            try:
                                i[j] = float(i[j])
                            except ValueError:
                                pass
                        else:
                            try:
                                i[j] = int(i[j])
                            except ValueError:
                                pass
                        if i[j] == 'true':
                            i[j] = True
                        elif i[j] == 'false':
                            i[j] = False

                    if i[j] == '':
                        i[j] = None

            if fn == 'maps.csv':
                # make maps look cool
                rp_data = {}
                for i in data:
                    if i['group']:
                        latest_grp = i['group']
                        rp_data[i['group']] = [i['data']]
                    else:
                        rp_data[latest_grp].append(i['data'])
                data = {i: rp_data[i] for i in sorted(rp_data.keys())}

            with open('json/' + fn.replace('.csv', '.json'), 'w+') as f:
                json.dump(data, f, indent=4)

        print(fp)

    # texts.csv
    data = {}
    for i in os.listdir('csv/texts'):
        file_path = f'csv/texts/{i}'
        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for n, row in enumerate(reader):
                if n == 0:
                    continue
                data[row['v'].replace('TID_', '')] = row['EN']

        print(file_path)

    with open('json/texts.json', 'w+') as f:
        json.dump(data, f, indent=4)
