"""
Load the ODS datasets into a CKAN instance
"""
import hashlib
import os
import sys

import dc
import ffs
import slugify

DATA_DIR = None

def datasets():
    input_file = DATA_DIR/'dataset.metadata.json'
    metadata = input_file.json_load()
    for dataset in metadata:
        directory = DATA_DIR / dataset['name']
        yield directory, input_file, dataset

def get_local_filename(dataset_dir, url):
    x = os.path.join(DATA_DIR, hashlib.sha224(url).hexdigest())
    return x

def load_ods():
    for directory, metadata_file, metadata in datasets():
        print 'Processing', metadata['title'], metadata['name']
        try:
            dc.Dataset.create_or_update(
                name=metadata['name'],
                title=metadata['title'],
                state='active',
                license_id='uk-ogl',
                notes=metadata['notes'],
                origin=metadata['origin'],
                tags=dc.tags(*metadata['tags']),
                resources=metadata["resources"],
                owner_org='hscic',
                frequency=metadata['frequency'],
                extras=[
                    dict(key='coverage_start_date', value=metadata['coverage_start_date']),
                    dict(key='coverage_end_date', value=metadata['coverage_end_date']),
                 #   dict(key='publication_date', value=metadata['publication_date'])
                ]
            )
        except:
            print "Failed to process", metadata['name']
    return

def group_ods():
    for _, _, metadata in datasets():
        dataset_name = metadata['name']
        dataset = dc.ckan.action.package_show(id=dataset_name)

        if [g for g in dataset['groups'] if g['name'].lower() == 'ods']:
            print 'Already in group', g
        else:
            dc.ckan.action.member_create(
                id='ods',
                object=dataset['name'],
                object_type='package',
                capacity='member'
            )
    return

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    dc.ensure_publisher('hscic')
    dc.ensure_group('ods')
    load_ods()
    group_ods()
    return 0

if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))
