# まてコン：JIP-まてりある用Excel変換ツール

![まてコン](docs/matecon.png)

## 機能

- JIP-まてりある（材料計算ソフトウェア）データ作成支援ツールです。
- 材料が計上された Excel ファイルを読み込み、JIP-まてりあるインポートデータ（`*.txt`）を出力します。
- ファイル拡張子 `*.xlsx` または `*.xlsm` の Excel ファイルを読み込みできます。

## Excel テンプレート

材料計上用 Excel ファイルとして、以下のテンプレートを利用できます。

- [MATERIAL_SAMPLE_1.xlsx](sample_data/MATERIAL_SAMPLE_1.xlsx)

Excel ファイルのシートには以下のヘッダー行が必要です。

<table><tr><td>MARK</td><td>S1</td><td>S2</td><td>S3</td><td>S4</td><td>L</td><td>EACH</td><td>UNITW</td><td>NET</td><td>QUALITY</td><td>REMARK</td><td>COMMENT</td><td>PR1</td><td>PR2</td><td>JV</td><td>ALIAS</td><td>P</td><td>T</td><td>C1</td><td>A1</td><td>C2</td><td>A2</td><td>WT</td><td>WB</td><td>WL</td><td>WR</td><td>YW</td><td>YL</td><td>HT</td><td>FACE1</td><td>FACE2</td><td>BOLT</td><td>PW</td><td>BEND</td><td>LC</td><td>BODY</td><td>WRT</td><td>WRB</td><td>WRL</td><td>WRR</td></tr></table>

## Excel ファイルの注意点

- ヘッダー行（MARK, S1, S2, S3, S4, L, ...）が必要です。
- 以下のシートは材料データの変換対象から除外されます。
  1. ヘッダー行が存在しないシート
  2. 非表示のシート
- ヘッダー行以降の行を材料データとして扱います。
- 材料データは複数シート、複数ファイルに分割可能です。
- 階層名が同一となる階層はマージされます。
