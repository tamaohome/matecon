from matecon.models.table import Table
from matecon.models.templates import MATERIAL_HEADER

MATERIAL_XLSX_1 = "sample_data/MATERIAL_SAMPLE_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/MATERIAL_SAMPLE_2.xlsx"


def test_table():
    filepaths = [MATERIAL_XLSX_1, MATERIAL_XLSX_2]
    table = Table(MATERIAL_HEADER, filepaths)
    assert table.header == MATERIAL_HEADER

    assert len(table.books) == 2  # 読み込んだExcelファイル数
    assert len(table.sheets) == 3  # 総シート数（有効シートのみ）
    assert len(table.rows) == 56  # 総行数（空白行を含む）
    assert table.filenames == ["MATERIAL_SAMPLE_1.xlsx", "MATERIAL_SAMPLE_2.xlsx"]
