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

        # 列幅の設定
        self.setColumnWidth(0, 300)  # レベル・名称
        self.setColumnWidth(1, 30)  # 員数

        self.reload()

    def reload(self, material: Material | None = None):
        """ツリーを更新する"""
        if material is not None:
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
        for child in node.children:
            self._add_node_recursive(child, item)
