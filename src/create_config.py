#!/usr/bin/env python3
"""
This script can be used to create a ROUGE XML config
file for evaluating your models.

"""
import argparse, os, re
from collections import defaultdict
import logging
from lxml import etree
import local_util as u # for u.eprint()

LOG = logging.getLogger()

doc_pattern=re.compile('(D[0-9]{4})-([A-Z])\.[A-Z]\.100\.[A-Z]\.[A-Z0-9]')
#                       "D1032-A.M.100.A.9"


def find_filenames(dir):
    """
    Given a directory, find the files that fit the TAC/DUC filename
    pattern.

    :param dir:
    :rtype: defaultdict[list]
    """
    docsets = defaultdict(list)

    print('find_filenames(): dir="{}"'.format(dir))
    for idx, path in enumerate( os.listdir(dir) ):
        # prints and such to try and figure this thing out (added by jgreve)
        #if idx < 10:
        #    print('idx={}, path={} doc_pattern={}'.format(idx, path, doc_pattern) )
        path_match = re.match(doc_pattern, path)
        #if idx < 10:
        #    print('    path_match={}'.format(path_match))
        #    if path_match:
        #        print('    path_match.groups={}'.format(path_match.groups()))
        if path_match is not None:
            docset_id, a_or_b = path_match.groups()
            full_id = path_match.group(0)[:-2]
            if a_or_b.lower() == 'a':
                docsets[full_id].append(path)

    u.eprint('found {} docsets out of {} total files in dir="{}")'.format(len(docsets), 1+idx, dir) ) # jgreve
    return docsets

def create_xml(mydir, modeldir):
    """
    Given a directory of system output files and a directory

    :param mydir:
    :param modeldir:
    :rtype: etree.Element
    """
    print('Scanning for model files...')
    models = find_filenames(modeldir)

    print('Scanning for system output files...')
    system = find_filenames(mydir)

    model_docset_ids = set(models.keys())
    system_docset_ids = set(system.keys())

    docset_union = model_docset_ids | system_docset_ids
    docset_intersection = model_docset_ids & system_docset_ids

    #if docset_union - docset_intersection:
    diffs = docset_union - docset_intersection
    if diffs:
        LOG.warning('Docset IDs differ between model and eval sets, diffs={}.'.format(diffs))
        

    # -------------------------------------------
    # Initialize XML
    # -------------------------------------------

    # Make the root element
    root = etree.Element('ROUGE_EVAL', attrib={'version':'1.5.5'})


    # For each docset, it will be a new "eval" element
    for docset_id in sorted(docset_intersection):

        peer_paths = system[docset_id]
        model_paths = models[docset_id]

        # Set up preamble
        eval_elt = etree.SubElement(root, 'EVAL', attrib={'ID':docset_id})
        make_text_subelement(eval_elt, 'PEER-ROOT', mydir)
        make_text_subelement(eval_elt, 'MODEL-ROOT', modeldir)
        etree.SubElement(eval_elt, 'INPUT-FORMAT', TYPE='SPL')

        # Add peer and model elements.
        add_peers(eval_elt, 'PEERS', 'P', peer_paths)
        add_peers(eval_elt, 'MODELS', 'M', model_paths)


    return root

def add_peers(parent, peer_elt_name, peer_tag, paths):
    """
    Convenience function to create an element with a list of path
    elements inside. e.g.:

        <MODELS>
            <M ID="C">D1045-A.M.100.H.C</M>
            <M ID="E">D1045-A.M.100.H.E</M>
            <M ID="F">D1045-A.M.100.H.F</M>
            <M ID="H">D1045-A.M.100.H.H</M>
        </MODELS>

    :rtype: list[eTree.SubElement]
    """
    peer_elt = etree.SubElement(parent, peer_elt_name)
    for path in paths:
        make_text_subelement(peer_elt, peer_tag, path, {'ID':path.split('.')[-1]})

def make_text_subelement(parent, name, text, attribs=None):
    """
    Convenience function to make a subelement that also contains a text node.

    e.g.:

    <M ID="D">D1046-A.M.100.H.D</M>

    :rtype: etree.SubElement
    """
    attribs = attribs if attribs is not None else {}
    elt = etree.SubElement(parent, name, **attribs)
    elt.text = text
    return elt

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('MYDATA_DIR', help="The directory containing your system's outputs.")
    p.add_argument('MODELDATA_DIR', help='The directory containing the model summaries.')
    p.add_argument('CONFIG_OUT', help='Output filename for the generated config.')

    args = p.parse_args()

    xml = create_xml(args.MYDATA_DIR, args.MODELDATA_DIR)

    print('Opening "{}" for writing...'.format(args.CONFIG_OUT))
    with open(args.CONFIG_OUT, 'w') as xml_out_f:
        xml_out_f.write(etree.tostring(xml, pretty_print=True).decode('utf-8'))
    print('Success.')
