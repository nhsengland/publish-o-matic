"""
"Load" HQIP data from DGU.

The original version of this script was provided by @rossjones
"""
import os
import datetime
import hashlib
import sys
import urllib

import ckanapi
from ckanapi.errors import NotFound, ValidationError

from dc import ckan as catalogue
from dc import _org_existsp, Dataset
import ffs

DATA_DIR = None

SOURCE = "http://data.gov.uk"
TARGET_ORGANISATION = "healthcare-quality-improvement-partnership"

dgu =  ckanapi.RemoteCKAN(SOURCE)

def format_date(date):
    return datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")

def main(workspace):
    global DATA_DIR
    DATA_DIR = ffs.Path(workspace) / 'data'

    org = dgu.action.organization_show(id=TARGET_ORGANISATION)

    if not _org_existsp(TARGET_ORGANISATION):
        catalogue.action.organization_create(
            name=org['name'],
            title=org['title'],
            description=org['description'],
            image_url=org['image_display_url']
        )

    print "Found {0} datasets on source".format(len(org['packages']))

    for package in org['packages']:
        print 'uploading', package['title'].encode('utf8')
        dataset_dir = DATA_DIR/package['name']
        # Get the dataset from DGU
        dataset = dgu.action.package_show(id=package['name'])
        del dataset['id']

        # Set the new owning organisation
        dataset['owner_org'] = org['name']

        resources = []

        with dataset_dir:
            for resource in dataset['resources']:
                resource['name'] = resource['description']
                #if resource['format'] == "HTML":
                #    resources.append(resource)
                #    continue
                #if resource['url'].startswith('hhttps'):
                #    resource['url'] = resource['url'].replace('hhttps', 'https')

                #filename = resource['url'].split('/')[-1]
                filename = hashlib.sha224(resource['url']).hexdigest()
                datafile = dataset_dir/filename
                if datafile.is_dir or not os.path.exists(datafile):
                    #resources.append(resource)
                    continue

                resource['upload'] = open(datafile, 'r')
                resources.append(resource)

        dataset['resources'] = resources

        # Add a nice tag so we can find them all again
        dataset['tags'].append({'name': 'HQIP' })
        print 'Owner org is', org['name']
        try:
            extras = [
                    dict(key='coverage_start_date', value=format_date(dataset['temporal_coverage-from'])),
                    dict(key='coverage_end_date', value=format_date(dataset['temporal_coverage-to'])),
                    dict(key='frequency', value=dataset['update_frequency']),
                ]
            new_dataset = Dataset.create_or_update(
                name=dataset['name'],
                title=dataset['title'],
                state='active',
                visibility='private',
                licence_id='ogl',
                notes=dataset['notes'],
                url=dataset['url'],
                tags=dataset['tags'],
                resources=dataset['resources'],
                owner_org=org['name'],
                extras=extras
            )
            print "Created {}".format(dataset['name'])
        except ValueError:
            print 'skipping because error'
            continue
        except ValidationError:
            raise
            print "Failed to upload {}".format(dataset['name'])


if __name__ == '__main__':
    sys.exit(main(ffs.Path.here()))
