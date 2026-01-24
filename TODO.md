# TODO

## ✨ feat/gui/improvements

- [x] `Fusion` テーマの適用
- [x] ファイルパスをコマンドライン引数としてアプリに渡す処理
- [x] ファイル未選択状態で「ここにファイルをドラッグ」というヒントを表示 (`FileCardContainer`)
- [x] ウインドウ幅変化時のツリー列幅の挙動を調整 (`MaterialTreeView`)
- [x] ウインドウ幅変化時のファイルカードリスト幅の挙動を調整 (`FileCardContainer`)

## ✨ feat/gui/material-treeview

- [ ] END行はツリー表示から除外する

## ✨ feat/gui/preferences

- [ ] 環境設定クラス `PreferencesDialog` の実装

## ✨ feat/gui/controller

- [ ] ファイル保存時にファイル名選択ダイアログを表示 (`Controller.save_file`)
  - デフォルト名は先頭の Excel ファイル名を基にする
  - 日時のサフィックスを付与するオプション

## ✨ feat/gui/menubar

- [ ] メニューバーの実装
- [ ] ヘルプ/使い方の表示
- [ ] ヘルプ/バージョン情報の表示

## ✨ feat/io/excel-reader

- [x] 追加時のみ Excel ファイルを開く処理に変更
  - `with` 構文内で `load_workbook()` を実行

## ✨ feat/io/validate-excel

- [ ] ファイル読み込み時: 有効な材片テーブルが存在するかチェック
- [ ] ファイル内容のバリデーション (材片名、員数の妥当性など)
- [ ] Excel 読込時に不正なシートを除外する処理
  - 非表示のシート
  - 不正なヘッダー
  - 不正な階層構造: #1 階層が存在しない
  - 不正な階層構造: #2 の次が #4 のように階層が連続していない
- [ ] 不正な Excel ファイル読込時のエラー処理
  - 読み込み可能なシートが存在しない場合

## ✨ feat/gui/filecard

- [ ] 追加済みの Excel ファイルを再読み込みするボタンを追加
  - 再読み込み時にファイルパスが存在しない場合、リストから除外
- [ ] 追加済みの Excel ファイルが上書き保存 (タイムスタンプを更新) された場合、画面に通知する機能

## ✨ feat/models/material

- [ ] `DetailNode` にツリー表示用文字列を返すプロパティ `tree_label` を実装
  - 返り値の例: "PL 160 x 9 x 640 (SM400A)"

## 💎 refactor/gui

- [ ] `@Slot` の明示
- [ ] ウィジェットの初期化処理メソッド名を整理 (`_setup_ui()`)
- [ ] ウィジェットの初期化を `_setup_ui()` としてメソッド化
- [ ] シグナル接続を `_connect_signals()` としてメソッド化

## 💎 refactor/gui/controller

- [ ] `Controller` のクラス分割を検討

## 💎 refactor/models

- [ ] 基底クラスを `NodeMixIn` に変更 (`spreadsheet`)
- [ ] `Worksheet` を直接保持しない設計に変更 (`spreadsheet`)

## 🏗️ build

- [ ] pyinstaller でビルド済みのバイナリファイルを追加
- [ ] インストーラの検討 (Inno Setup)
- [ ] アプリアイコンの追加

## 📖 docs

- [ ] README: 内容の見直し
- [ ] README: まてりある入力用Excelテンプレートデータの設置
