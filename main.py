import subprocess

import bibtexparser
import requests
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter
from tqdm import tqdm
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', default='fulldb.bib')
    parser.add_argument('--output_path', default='fulldb_cleaned_noarxiv.bib')
    parser.add_argument('--aux_path', default='neufu_paper.aux')
    parser.add_argument('--checkciteslua_path', default='checkcites.lua')
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path
    aux_path = args.aux_path
    checkciteslua_path = args.checkciteslua_path

    output = subprocess.getoutput(
        f"texlua {checkciteslua_path}  {aux_path} --unused")
    outputs = output.split('\n')
    unused = [a[3:] for a in outputs if a.startswith("=> ")]

    with open(input_path, 'r') as bibtex_file:
        bib_content = bibtex_file.readlines()

    # remove entries that cannot be processed by the library
    bib_content = [line for line in bib_content if 'month' not in line]
    bib_out = ''.join(bib_content)

    with open(output_path, 'w') as f:
        f.write(bib_out)

    with open(output_path) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    arxiv_paper_idx = [idx for idx, item in enumerate(bib_database.entries) if
                       'eprinttype' in item.keys() and 'arxiv' in item['eprinttype']]
    for idx in tqdm(arxiv_paper_idx):
        bib_item: dict = bib_database.entries[idx]
        if bib_item['ID'] in unused:
            continue
        if 'journal' in bib_item.keys() and 'arXiv' in bib_item['journal']:
            arxiv_id = bib_item['journal'].split(':')[1].split(' ')[0]
        elif 'eprint' in bib_item.keys():
            arxiv_id = bib_item['eprint']
        else:
            raise ValueError("paper:{} not interpretable. \nGet journal:{}\nGet eprint:{} with type:{}"
                             .format(bib_item['journal'], bib_item['eprint'], ['eprinttype']))

        URL = 'http://api.semanticscholar.org/v1/paper/arXiv:' + arxiv_id
        r = requests.get(url=URL)
        data = r.json()
        if 'error' in data.keys():
            print("Paper:{} not found!".format(bib_item['title']))
            continue
        else:
            bib_item['year'] = str(data['year'])
            bib_item['doi'] = str(data['doi'])
            bib_item['journal'] = data['venue']
            bib_item.pop('archiveprefix', None)
            if 'pages' in data.keys():
                bib_item['pages'] = str(data['pages'])

    db = BibDatabase()
    db.entries = []
    for bib_item in bib_database.entries:
        if bib_item['ID'] not in unused:
            if 'abstract' in bib_item.keys():
                bib_item.pop('abstract')
            db.entries.append(bib_item)

    writer = BibTexWriter()
    with open(output_path, 'w') as bibfile:
        bibfile.write(writer.write(db))


if __name__ == '__main__':
    main()
