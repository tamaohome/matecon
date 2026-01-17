from matecon.models.table import Table
from matecon.models.templates import TABLE_HEADER

MATERIAL_XLSX_1 = "sample_data/MATERIAL_SAMPLE_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/MATERIAL_SAMPLE_2.xlsx"


def test_table():
    filepaths = [MATERIAL_XLSX_1, MATERIAL_XLSX_2]
    table = Table(TABLE_HEADER, filepaths)
    assert table.header == TABLE_HEADER

    assert len(table.books) == 2  # 読み込んだExcelファイル数
    assert len(table.sheets) == 3  # 総シート数
    assert len(table.rows) == 50  # 総行数
    assert table.filenames == ["MATERIAL_SAMPLE_1.xlsx", "MATERIAL_SAMPLE_2.xlsx"]
