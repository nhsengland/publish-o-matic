from scrape import main as main_scrape
from functools import partial
from publish.lib import digital_nhs_helpers
from datasets.ccgois_indicators.scrape import SCRAPER_NAME

GROUP = "ccgois"
PUBLISHER = "hscic"


def entrypoints():
    """
        scrapes the CCG Outcomes Indicator Set from
        https://indicators.hscic.gov.uk/webview/
    """

    # creates a function that uploads to S3 with this scraper
    transform = partial(
        digital_nhs_helpers.upload_resource_from_file,
        SCRAPER_NAME  # scraper name
    )

    # creates a function that uploads to S3 with this scraper, publisher, and group
    load = partial(
        digital_nhs_helpers.load_dataset_to_ckan,
        SCRAPER_NAME,  # scraper name
        PUBLISHER,  # publisher
        GROUP  # group
    )
    return {
        'scrape': main_scrape,
        'transform': transform,
        'load': load
    }
