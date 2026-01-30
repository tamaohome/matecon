import pytest

from matecon.models.excel_file import ExcelFile
from matecon.models.excel_file_set import ExcelFileSet

BOOK_SAMPLE = "sample_data/BOOK_SAMPLE.xlsx"
MATERIAL_XLSX_1 = "sample_data/MATERIAL_SAMPLE_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/MATERIAL_SAMPLE_2.xlsx"


def test_excel_file_set_init():
    """`ExcelFileSet` の初期化"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1), ExcelFile(MATERIAL_XLSX_2)]
    excel_file_set = ExcelFileSet(excel_files)

    assert len(excel_file_set) == 2


def test_excel_file_set_add():
    """`ExcelFileSet` への追加"""
    excel_file_set = ExcelFileSet()
    assert len(excel_file_set) == 0

    # ExcelFileを追加
    excel_file_set.add(ExcelFile(BOOK_SAMPLE))
    assert len(excel_file_set) == 1
    assert excel_file_set[0] == ExcelFile(BOOK_SAMPLE)

    # 同じファイルパスが追加された場合（エラー）
    with pytest.raises(ValueError):
        excel_file_set.add(ExcelFile(BOOK_SAMPLE))

    # ExcelFileリストを追加
    excel_files = [ExcelFile(MATERIAL_XLSX_1), ExcelFile(MATERIAL_XLSX_2)]
    excel_file_set.add(*excel_files)
    assert len(excel_file_set) == 3
    assert excel_file_set[2] == ExcelFile(MATERIAL_XLSX_2)


def test_excel_file_set_discard():
    """`ExcelFileSet` から削除"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1), ExcelFile(MATERIAL_XLSX_2)]
    excel_file_set = ExcelFileSet(excel_files)

    excel_file_1 = ExcelFile(MATERIAL_XLSX_1)
    excel_file_set.discard(excel_file_1)
    assert len(excel_file_set) == 1
    assert excel_file_set[0] == ExcelFile(MATERIAL_XLSX_2)
    assert excel_file_1 not in excel_file_set

    # 既に削除したExcelファイルを削除しようとしてもエラーは発生しない
    excel_file_set.discard(excel_file_1)


def test_excel_file_set_clear():
    """セットを空にする"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1), ExcelFile(MATERIAL_XLSX_2)]
    excel_file_set = ExcelFileSet(excel_files)

    excel_file_set.clear()
    assert len(excel_file_set) == 0
    assert not excel_file_set


def test_excel_file_set_plus():
    """`ExcelFileSet` の加算演算子"""
    initial_set = ExcelFileSet()

    # ExcelFileを加算
    result_set = initial_set + ExcelFile(BOOK_SAMPLE)
    assert len(result_set) == 1

    # ExcelFileSetを加算
    excel_files = [ExcelFile(MATERIAL_XLSX_1), ExcelFile(MATERIAL_XLSX_2)]
    additional_set = result_set + ExcelFileSet(excel_files)
    assert len(additional_set) == 3

    # 同じExcelファイルが加算された場合（エラー）
    with pytest.raises(ValueError):
        additional_set += ExcelFile(BOOK_SAMPLE)
