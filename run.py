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
        config = {'id': {}, 'combine': {}}

    csv_files = glob.iglob('csv/csv_*/**/*.csv', recursive=True)

    for fp in csv_files:
        fn = os.path.split(fp)[1].replace('.csv', '')

        with open(fp, encoding='utf-8') as f:
            reader = csv.DictReader(f)

            title = reader.fieldnames

            combine = False
            set_data = True
            for i in config['combine']:
                if fn in config['combine'][i] and config['combine'][i][0] != fn:
                    combine = config['combine'][i][0]
                    if config['combine'][i][1] != fn:
                        set_data = False
                    break

            if set_data:
                data = []

            for n, row in enumerate(reader):
                if n == 0:
                    continue
                data.append({title[i][:1].lower() + title[i][1:]: row[title[i]] for i in range(len(title))})

            for n, i in enumerate(data):
                if fn in config['id']:
                    i['id'] = config['id'][fn] + n
                if combine:
                    i['category'] = fn.replace(combine, '')
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

            set_path = 1
            if combine:
                for i in config['combine']:
                    if fn in config['combine'][i]:
                        if config['combine'][i][-1] == fn:
                            set_path = 2
                        else:
                            set_path = 0
                        break

            if set_path == 1:
                save_fp = os.path.join('json', os.path.sep.join(os.path.normpath(fp).split(os.path.sep)[2:]).replace(os.path.sep, '.').replace('.csv', '.json'))
            elif set_path == 2:
                save_fp = os.path.join('json', f'{i}.json')
            else:
                continue

            with open(save_fp, 'w+') as f:
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
