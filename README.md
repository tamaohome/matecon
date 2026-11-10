# まてコン：JIP-まてりある用Excel変換ツール

![まてコン](docs/matecon.png)

## 機能

- JIP-まてりある（材料計算ソフトウェア）データ作成支援ツールです。
- 材料が計上された Excel ファイルを読み込み、JIP-まてりあるインポートデータ（`*.txt`）を出力します。
- ファイル拡張子 `*.xlsx` または `*.xlsm` の Excel ファイルを読み込みできます。

## Excel テンプレート

材料計上用 Excel ファイルとして、以下のテンプレートを利用できます。

- [material_data_1.xlsx](sample_data/material_data_1.xlsx)

Excel ファイルのシートには以下のヘッダー行が必要です。

<table><tr><td>MARK</td><td>S1</td><td>S2</td><td>S3</td><td>S4</td><td>L</td><td>EACH</td><td>UNITW</td><td>NET</td><td>QUALITY</td><td>REMARK</td><td>COMMENT</td><td>PR1</td><td>PR2</td><td>JV</td><td>ALIAS</td><td>P</td><td>T</td><td>C1</td><td>A1</td><td>C2</td><td>A2</td><td>WT</td><td>WB</td><td>WL</td><td>WR</td><td>YW</td><td>YL</td><td>HT</td><td>FACE1</td><td>FACE2</td><td>BOLT</td><td>PW</td><td>BEND</td><td>LC</td><td>BODY</td><td>WRT</td><td>WRB</td><td>WRL</td><td>WRR</td></tr></table>

## Excel ファイルの注意点

- 材料データは複数シート・複数ファイルに分割可能です。ただし、以下にご注意ください。
  - 各シートにはヘッダー行（MARK, S1, S2, S3, S4, L, ...）が必要です。ヘッダー行以降の行が材料データとして読み込まれます。
  - 各シートにはレベル 1 階層 (#1) からのデータ入力が必要です。

- 上位階層の省略および途中階層の省略はできません。
  - 例: #2 階層のすぐ下に #4 階層が存在するシートの場合、正常に読み込みできません。

- 以下のシートは材料データの変換対象から除外されます。
  - ヘッダー行が存在しないシート
  - 非表示のシート

## リリース手順（開発者向け）

1. コミット件名は `<絵文字> <type>(scope): 件名` の形式で書く（type: `feat` / `fix` / `refactor` など）。
2. main にマージ後、ローカルで `uv run cz bump --dry-run` を実行し、上がるバージョンを確認する。
3. `uv run cz bump` を実行する。`pyproject.toml` の version 更新、コミット、タグ作成をまとめて行う。
4. `git push origin main --follow-tags` で push する。タグ push により Windows 向けビルドと GitHub Release が自動作成される。

- バージョン上げ規則: `feat` → MINOR、`fix` / `refactor` / `perf` → PATCH、`!` 付き（破壊的変更）→ MAJOR。`build` / `chore` / `docs` などのみの場合は上がらない。
- タグと `pyproject.toml` の version が一致しない場合、CI が失敗する。
