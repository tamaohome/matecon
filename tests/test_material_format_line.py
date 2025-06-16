# -*- coding: utf-8 -*-

import pytest
from pprint import pprint

from matecon.material import Material

from helpers import load_txt_sample

MATERIAL_XLSX = "sample_data/MATERIAL_SAMPLE.xlsx"
MATERIAL_TXT = "sample_data/MATERIAL_SAMPLE.txt"
TXT_SAMPLE = load_txt_sample(MATERIAL_TXT)


def test_material_format_block_line():
    """BLOCKノードの員数"""
    mate = Material(MATERIAL_XLSX)

    node1 = mate.nodes[5]
    node2 = mate.nodes[12]

    print()
    print(node1.format_line)
    print(node2.format_line)

    assert node1.format_line == "     中間横桁本体                 6"
    assert node2.format_line == "     中間横桁仕口                12"


def test_material_format_lines():
    mate = Material(MATERIAL_XLSX)
    lines = mate.format_lines
    pprint(lines)
    assert lines == TXT_SAMPLE
