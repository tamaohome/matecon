import pytest

from matecon.io.excel_reader import BookNode, WorkbookReader
from matecon.models.excel_file import ExcelFile
from matecon.models.templates import MATERIAL_HEADER

MATERIAL_XLSX_1 = "sample_data/material_data_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/material_data_2.xlsx"
MATERIAL_TXT_1 = "sample_data/material_data_1.txt"


def test_incorrect_node_creation():
    """`BookNode` を直接生成した場合のエラー"""
    with pytest.raises(TypeError, match="BookNode は直接生成できません"):
        excel_file = ExcelFile(MATERIAL_XLSX_1)
        BookNode(excel_file, MATERIAL_HEADER)


def test_load_booknode():
    """`BookNode` の読み込み"""
    excel_file = ExcelFile(MATERIAL_XLSX_1)
    reader = WorkbookReader(excel_file, MATERIAL_HEADER)
    book = reader.load_booknode()
    assert book.name == "material_data_1"
    assert book.header == MATERIAL_HEADER

    assert len(book) == 2
    assert book[0].name == "横桁"
    assert book[1].name == "排水装置"
