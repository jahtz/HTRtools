from pathlib import Path
import json

import click

from pagexml import PageXML, ElementType
from helper.geometry import Polygon


DEFAULT_MAPPING = Path(__file__).parent.parent.parent.joinpath('configs', 'coco_mapping.json')


def replace_dots(orig: str) -> str:
    """ Replaces all dots in a filename except the last one """
    parts = orig.split('.')
    return f'{"_".join(parts[:-1])}.{parts[-1]}'


def coco2page(coco_fp: Path, out_dir: Path, mapping: dict, creator: str, dots: bool):
    """
    Parses Coco annotations to valid PageXML files, using pagexml library

    :param coco_fp: path to coco file
    :param out_dir: directory for generated PageXML files, same as coco file if not set
    :param mapping: dictionary containing mapping from coco annotations to PageXML regions and elements
    :param creator: creator saved in metadata
    :param dots: Remove dots in PageXML file names and all filename attributes. Replace them with underscores
    :return: None
    """
    click.echo('Loading COCO File.')
    with open(coco_fp, 'r') as f:
        stream = json.load(f)
    
    categories = {category['id']: category['name'] for category in stream['categories']}

    images = {}
    for image in stream['images']:
        images[image['id']] = {
            'file': replace_dots(image['file_name']) if dots else image['file_name'],
            'width': image['width'],
            'height': image['height'],
            'regions': []
        }

    for region in stream['annotations']:
        if region['image_id'] in images:
            images[region['image_id']]['regions'].append({
                'id': region['id'],
                'category': categories[region['category_id']],
                'bbox': [] if len(region['bbox']) < 1 else region['bbox'],
                'coords': [] if len(region['segmentation']) < 1 else region['segmentation'][0]
            })
        else:
            click.echo(f'! Region {region["id"]} does not match any image file')
    click.echo('Done.')

    with click.progressbar(images.values(), label='Building PageXML', show_pos=True, item_show_func=lambda x: x['file'] if x is not None else "", show_eta=True, show_percent=True) as data:
        for i, file in enumerate(data):
            
            pxml = PageXML.new(creator=creator)

            p = pxml.create_page(**{
                'imageFilename': file['file'],
                'width': str(file['width']),
                'height': str(file['height']), 
            })

            for rid, region in enumerate(file['regions']):
                attributes = {} if region['category'] not in mapping else mapping[region['category']]['attributes']
                attributes['id'] = f'r_{rid}'
                r = p.create_element(
                    etype=ElementType.UnknownRegion if region['category'] not in mapping else ElementType(mapping[region['category']]['type']),
                    **attributes
                )
                if len(region['coords']) > 0:
                    coords = Polygon.from_coco(region['coords'])
                    r.create_element(ElementType.Coords, points=coords.to_page_coords())
                elif len(region['bbox']) > 0:
                    bbox = Polygon.from_bbox(region['bbox'])
                    r.create_element(ElementType.Coords, points=bbox.to_page_coords())
            pxml.to_xml(out_dir.joinpath('.'.join(file['file'].split('.')[:-1]) + '.xml'))


@click.command('coco2page', short_help='Converts COCO annotations to PageXML files.')
@click.help_option('-h', '--help')
@click.argument(
    'coco_file',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True    
)
@click.option(
    '-o', '--output',
    help='Output directory for generated PageXML files. Writes to the same directory as the COCO file if not set.',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    required=False,
)
@click.option(
    '-m', '--mapping',
    help='JSON file containing mapping from COCO categories to PageXML regions and elements.',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=False,
    default=DEFAULT_MAPPING,
    show_default=False
)
@click.option(
    '-c', '--creator',
    help='Creator of the generated PageXML files.',
    type=click.STRING,
    required=False,
    default='ZPD Wuerzburg'
)
@click.option(
    '-d', '--dots',
    help='Remove dots in PageXML file names and all filename attributes. Replace them with underscores.',
    type=click.BOOL,
    is_flag=True,
    required=False,
    default=False
)
def coco2page_cli(coco_file: str, output: str | None, mapping: str | None, creator: str | None, dots: bool):
    """
    Converts COCO annotations to PageXML files.
    """
    coco_fp = Path(coco_file)
    out_dir = coco_fp.parent if output is None else Path(output)
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
    mapping_fp = DEFAULT_MAPPING if mapping is None else Path(mapping)

    with open(mapping_fp, 'r') as f:
        mapping = dict(json.load(f))

    coco2page(coco_fp, out_dir, mapping, creator, dots)
