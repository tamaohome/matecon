from helpers import read_txt_file

from matecon.models.excel_file import ExcelFile
from matecon.models.excel_file_set import ExcelFileSet
from matecon.models.material import Material

MATERIAL_XLSX_1 = "sample_data/MATERIAL_SAMPLE_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/MATERIAL_SAMPLE_2.xlsx"
MATERIAL_TXT_1 = "sample_data/MATERIAL_SAMPLE_1.txt"
MATERIAL_TXT_12 = "sample_data/MATERIAL_SAMPLE_1+2.txt"
TXT_SAMPLE_1 = read_txt_file(MATERIAL_TXT_1)
TXT_SAMPLE_12 = read_txt_file(MATERIAL_TXT_12)


def test_material_format_block_line():
    """BLOCKノードの員数"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    node1 = mate.nodes[5]
    node2 = mate.nodes[12]
    assert node1.format_line == "     中間横桁本体                 6"
    assert node2.format_line == "     中間横桁仕口                12"


def test_material_format_lines_single_file():
    """単一ファイルで生成した `Material` の出力形式チェック"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    lines = mate.format_lines
    assert lines == TXT_SAMPLE_1


def test_material_format_lines_multi_files():
    """複数ファイルで生成した `Material` の出力形式チェック"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1), ExcelFile(MATERIAL_XLSX_2)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    lines = mate.format_lines
    assert lines == TXT_SAMPLE_12
