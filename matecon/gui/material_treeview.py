from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

from matecon.models.material import Material, MaterialNode


class MaterialTreeView(QTreeWidget):
    """材片情報 `Material` をツリー描画するコンポーネント"""

    def __init__(self, material: Material | None = None, parent=None):
        super().__init__(parent)
        self._material = material

        # ヘッダーの設定
        header_names = ["名称", "員数"]
        self.setColumnCount(len(header_names))
        self.setHeaderLabels(header_names)
        right_vcenter = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        self.headerItem().setTextAlignment(1, right_vcenter)

        # 列幅の設定
        self.setColumnWidth(0, 300)  # レベル・名称
        self.setColumnWidth(1, 30)  # 員数

        # インデント幅の設定
        self.setIndentation(16)

        self.reload()

    def reload(self, material: Material | None = None):
        """ツリーを更新する"""
        self._material = material
        if self._material is None:
            self.clear()
            return
        self._populate_tree()

    def _populate_tree(self):
        """ツリーを構築する"""
        self.clear()
        if not self._material:
            return
        root_node = self._material.root
        for child in root_node.children:
            self._add_node_recursive(child, self)

    def _add_node_recursive(self, node: MaterialNode, parent_item):
        """`MaterialNode` ツリーを再帰的に `QTreeWidgetItem` へ変換"""
        item = QTreeWidgetItem(parent_item, [node.name, str(node.each)])

        # 員数列を右揃え
        right_vcenter = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        item.setTextAlignment(1, right_vcenter)

        for child in node.children:
            self._add_node_recursive(child, item)

    def expand_to_depth(self, depth: int):
        """ツリーを指定した深さまで展開する"""

        def _expand(item, current_depth):
            if current_depth >= depth:
                return
            self.expandItem(item)
            for i in range(item.childCount()):
                _expand(item.child(i), current_depth + 1)

        # ルート直下のアイテムから再帰的に展開
        for i in range(self.topLevelItemCount()):
            _expand(self.topLevelItem(i), 1)
