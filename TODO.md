# TODO

## ✨ feat/gui

- [ ] `Fusion` テーマの適用
- [ ] ファイルパスをコマンドライン引数としてアプリに渡す処理
- [ ] ファイル未選択状態で「ここにファイルをドラッグ」というヒントを表示 (`FileCardContainer`)
- [ ] ウインドウ幅変化時のツリー列幅の挙動を調整 (`MaterialTreeView`)
- [ ] 環境設定の実装

## ✨ feat/gui/controller

- [ ] ファイル保存時にファイル名選択ダイアログを表示 (`Controller.save_file`)
  - デフォルト名は先頭の Excel ファイル名を基にする
  - 日時のサフィックスを付与するオプション

## ✨ feat/gui/menubar

- [ ] メニューバーの実装
- [ ] ヘルプ/使い方の表示
- [ ] ヘルプ/バージョン情報の表示

## ✨ feat/models

- [ ] 追加時のみ Excel ファイルを開く処理に変更
  - `with` 構文内で `load_workbook()` を実行
- [ ] 追加済みの Excel ファイルを再読み込みするボタンを追加
  - 再読み込み時にファイルパスが存在しない場合、リストから除外
- [ ] 追加済みの Excel ファイルが上書き保存 (タイムスタンプを更新) された場合、画面に通知する機能
- [ ] ファイル読み込み時: 有効な材片テーブルが存在するかチェック
- [ ] ファイル内容のバリデーション (材片名、員数の妥当性など)
- [ ] Excel 読込時に不正なシートを除外する処理
  - 非表示のシート
  - 不正なヘッダー
  - 不正な階層構造: #1 階層が存在しない
  - 不正な階層構造: #2 の次が #4 のように階層が連続していない
- [ ] 不正な Excel ファイル読込時のエラー処理
  - 読み込み可能なシートが存在しない場合

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

## 💎 refactor/gui/config

- [ ] ウィンドウ設定管理クラスに `QSettings` を利用
- [ ] ウインドウ設定管理クラスの整理
- [x] デフォルトウインドウサイズを調整 (`WindowGeometry`)

## 💎 refactor/models

- [ ] 基底クラスを `NodeMixIn` に変更 (`spreadsheet`)
- [ ] `Worksheet` を直接保持しない設計に変更 (`spreadsheet`)

## 🏗️ build

- [ ] pyinstaller でビルド済みのバイナリファイルを追加
- [ ] インストーラの検討 (Inno Setup)

## 📖 docs

- [ ] README: 内容の見直し
- [ ] README: まてりある入力用Excelテンプレートデータの設置
