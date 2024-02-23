# Documentation
## Table of Contents
- [Setup](https://github.com/Jatzelberger/HTRtools#setup)
- [Usage](https://github.com/Jatzelberger/HTRtools#usage)
- [Tools](https://github.com/Jatzelberger/HTRtools#tools)
   - [PageXML](https://github.com/Jatzelberger/HTRtools#pagexml)
      - [pagefix](https://github.com/Jatzelberger/HTRtools#pagefix)
      - [pagesearch](https://github.com/Jatzelberger/HTRtools#pagesearch)
      - [regionstats](https://github.com/Jatzelberger/HTRtools#regionstats)
    - [Parser](https://github.com/Jatzelberger/HTRtools#parser)
      - [csv2txt](https://github.com/Jatzelberger/HTRtools#csv2txt)
      - [img2png](https://github.com/Jatzelberger/HTRtools#img2png)
      - [ods2json](https://github.com/Jatzelberger/HTRtools#ods2json)
      - [pdf2png](https://github.com/Jatzelberger/HTRtools#pdf2png)
    - [Manipulation](https://github.com/Jatzelberger/HTRtools#manipulation)
      - [imageresize](https://github.com/Jatzelberger/HTRtools#imageresize)
      - [suffixedit](https://github.com/Jatzelberger/HTRtools#suffixedit)

## Setup
Tested with Python 3.12.1
### Download
```shell
git pull https://github.com/Jatzelberger/HTRtools
```
### Install Dependencies
```shell
pip3 install -r HTRtools/requirements.txt
```
Content:
```
beautifulsoup4~=4.12.2
click~=8.1.7
lxml~=5.1.0
odspy~=0.1
pandas~=2.1.3
pillow~=10.2.0
PyMuPDF~=1.23.6
PyMuPDFb~=1.23.6
```

## Usage
```shell
python3 HTRtools [OPTIONS] COMMAND [ARGS]...
```
```shell
python3 HTRtools -h
```

## Tools
### PageXML
#### pagefix
```
Usage: HTRtools pagefix [OPTIONS] INPUT_DIR [OUTPUT_DIR]

  Fix invalid PageXML documents.

  If OUTPUT_DIR is not set, script will overwrite old xml files.

  Recommended options: -cfrt

Options:
  -h, --help             Show this message and exit.
  -f, --image_filename   Changes imageFilename attribute of Page element from
                         absolute to relative.
  -m, --merge_regions    Merges TextRegion elements with same coordinates.
  -r, --reading_order    Adding or updating ReadingOrder element.
  -t, --region_type      Adding or fixing type attribute to Page element.
  -c, --negative_coords  Sets all negative coordinates of TextLine elements to
                         0.
  -l, --line_order       Fixing TextLine element order by their y coordinates.
```

#### pagesearch
```
Usage: HTRtools pagesearch [OPTIONS] INPUT_DIR SEARCH_FILE

  Search for characters in set of PageXML files.

  Creates a directory with content based on rules specified in
  './config/pagesearch.cfg'.

  INPUT_DIR should be a directory containing PageXML files and matching
  images.

  SEARCH_FILE examples can be found in './examples/' folder.

Options:
  -h, --help              Show this message and exit.
  -c, --console           Prints output to console (without file copy).
  -r, --recursive         Recursive search in input directory.
  -o, --output DIRECTORY  Target directory for copied images and output
                          results.csv file. Ignored if -c/--console is set.
  --config FILE           Use custom config.cfg file.  [default: /home/janik/S
                          eafile/zpd/github/HTRtools/config/pagesearch.cfg]
```
#### regionstats
```
Usage: HTRtools regionstats [OPTIONS] XML_FILES [OUTPUT_DIRECTORY]

  Outputs stats of one or multiple PageXML files.

  XML_FILES can either be a directory containing multiple .xml files or a
  single .xml file.

  Creates a stats.csv file in OUTPUT_DIRECTORY or prints stats to console if
  OUTPUT_DIRECTORY is not specified.

Options:
  -h, --help  Show this message and exit.
```
### Parser
#### csv2txt
```
Usage: HTRtools csv2txt [OPTIONS] INPUT_CSV OUTPUT_TXT

  Extracts a column from a .csv file into a .txt file.

  OUTPUT_TXT of format '/path/to/file.txt'.

  Made for pagesearch script.

Options:
  -h, --help            Show this message and exit.
  -c, --column INTEGER  Column to extract.  [default: 0]
  -s, --skip            Skip empty cells, else insert blank line.
```

#### img2png
```
Usage: HTRtools img2png [OPTIONS] INPUT_DIR OUTPUT_DIR

  Converts any image file formats to PNG file.

Options:
  -h, --help                Show this message and exit.
  -i, --input_suffix TEXT   Input file suffix.  [default: .jpg]
  -o, --output_suffix TEXT  Output file suffix between filename and ".png".
  -s, --size INTEGER        Set height of output images in pixels. Defaults to
                            input height.
  -r, --recursive           Walks INPUT_DIR recursively.
  -n, --number              number filenames.

```

#### ods2json
```
Usage: HTRtools ods2json [OPTIONS] INPUT_ODS OUTPUT_JSON

  Extracts mapping data from .ods file to PAGETools compatible json format.

  PAGETools: https://github.com/uniwue-zpd/PAGETools

  OUTPUT_TXT of format '/path/to/file.json'.

Options:
  -h, --help              Show this message and exit.
  -p, --disable_prettify  Disable pretty printing.
  -i, --indent INTEGER    Pretty printing indentation. Ignored if -p is set.
                          [default: 4]
```

#### pdf2png
```
Usage: HTRtools pdf2png [OPTIONS] INPUT_PDF OUTPUT_DIR

  Converts PDF file to PNG images, numerated by page number.

Options:
  -h, --help                Show this message and exit.
  -o, --output_suffix TEXT  Output file suffix between filename and ".png".
  -s, --size INTEGER        Set height of output images in pixels. Defaults to
                            original height.
  -d, --dpi INTEGER         DPI for PDF scanning.  [default: 300]
```

### Manipulation
#### imageresize
```
Usage: HTRtools imageresize [OPTIONS] INPUT_DIR [OUTPUT_DIR]

  Resizes images.

  Overwrites original images if OUTPUT_DIR is not set.

Options:
  -h, --help                Show this message and exit.
  -i, --input_regex TEXT    Input filename regular expression (example:
                            *.orig.png).  [default: *]
  -o, --output_suffix TEXT  Replaces all suffixes after first dot. Only with
                            OUTPUT argument set.
  -s, --size INTEGER        Set height of output images in pixels.  [required]
```

#### suffixedit
```
Usage: HTRtools suffixedit [OPTIONS] DIRECTORY OLD_SUFFIX NEW_SUFFIX

Options:
  -h, --help            Show this message and exit.
  -b, --blacklist TEXT  Blacklist suffixes, multiple items are allowed.
  -r, --recursive       Walk through subdirectories recursively.
```