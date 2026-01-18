# TODO

## 🏗️ アーキテクチャ・リファクタリング

- [ ] 肥大化した `Controller` への対処（責務の分散）
- [ ] `Controller.is_valid_excel_file()` を `spreadsheet_reader` に移動するか検討
- [ ] `MainWindow.closeEvent()` を整理: `view.py` で `WindowGeometry` のimportを不要にする
- [ ] `MainToolBar.action_open` を private メソッドに変更

## 🏗️ アーキテクチャ・リファクタリング / モデル改善

- [ ] `DetailNode` にツリー表示用文字列を返すプロパティ `tree_label` を実装
  - 返り値の例: "PL 160 x 9 x 640 (SM400A)"

## ✨ MaterialTreeView (GUI)

- [ ] 員数列を右揃えに変更
- [ ] ツリー展開ボタンを追加
- [ ] 設定の永続化 (iniファイル保存): セパレータ幅、ツリー列幅

## 🛡️ Excel読込・バリデーション

- [ ] ファイル読み込み時: ファイルロックしない処理に修正（一時ファイル経由等）
- [ ] ファイル読み込み時: 有効な材片テーブルが存在するかチェック
- [ ] ファイル内容のバリデーション (材片名、員数の妥当性など)
- [ ] 不正なExcelデータ（ヘッダー不正等）読込時のエラー処理
- [ ] ファイル保存時にファイル名選択ダイアログを表示 (`Controller.save_file`)

## 📖 ドキュメント

- [ ] README: 内容の見直し
- [ ] README: まてりある入力用Excelテンプレートデータの設置
