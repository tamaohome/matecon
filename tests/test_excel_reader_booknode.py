import pytest

from matecon.io.excel_reader import BookNode, ExcelReader
from matecon.models.templates import MATERIAL_HEADER

MATERIAL_XLSX_1 = "sample_data/MATERIAL_SAMPLE_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/MATERIAL_SAMPLE_2.xlsx"
MATERIAL_TXT_1 = "sample_data/MATERIAL_SAMPLE_1.txt"


def test_incorrect_node_creation():
    """`BookNode` を直接生成した場合のエラー"""
    with pytest.raises(TypeError, match="BookNode は直接生成できません"):
        BookNode(MATERIAL_XLSX_1, MATERIAL_HEADER)


def test_load_booknode():
    """`BookNode` の読み込み"""
    reader = ExcelReader(MATERIAL_XLSX_1, MATERIAL_HEADER)
    book = reader.load_booknode()
    assert book.name == "MATERIAL_SAMPLE_1"
    assert book.header == MATERIAL_HEADER

    assert len(book) == 2
    assert book[0].name == "横桁"
    assert book[1].name == "排水装置"
