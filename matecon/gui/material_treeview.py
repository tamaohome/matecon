from __future__ import annotations

from typing import override

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QActionGroup, QContextMenuEvent
from PySide6.QtWidgets import QMenu, QTreeWidget, QTreeWidgetItem

from matecon.models.material import Material, MaterialNode


class MaterialTreeView(QTreeWidget):
    """材片情報 `Material` をツリー描画するコンポーネント"""

    def __init__(self, material: Material | None = None, parent=None):
        super().__init__(parent)
        self._material = material
        self._expand_depth = 6  # 現在の展開深さ (デフォルトはBLOCK)

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
        self.expand_to_current_depth()  # ツリー展開状態を更新

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

    def expand_to_current_depth(self) -> None:
        """ツリーを現在の展開深さまで展開する"""
        self.expand_to_depth(self.expand_depth)

    def expand_to_depth(self, depth: int) -> None:
        """ツリーを指定した深さまで展開する"""
        self._expand_depth = depth  # 現在の展開深さを更新
        self.collapseAll()  # 展開状態をリセット

        def _expand(item, current_depth):
            if current_depth >= depth:
                return
            self.expandItem(item)
            for i in range(item.childCount()):
                _expand(item.child(i), current_depth + 1)

        # ルート直下のアイテムから再帰的に展開
        for i in range(self.topLevelItemCount()):
            _expand(self.topLevelItem(i), 1)

    @override
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = MaterialTreeViewContextMenu(self)
        menu.expandDepthChanged.connect(self.expand_to_depth)
        menu.exec(event.globalPos())

    @property
    def expand_depth(self) -> int:
        """現在の展開深さ"""
        return self._expand_depth


class MaterialTreeViewContextMenu(QMenu):
    """`MaterialTreeView` の右クリックメニュー"""

    expandDepthChanged = Signal(int)

    def __init__(self, parent: MaterialTreeView):
        super().__init__(parent)
        self._action_group = QActionGroup(self)
        self._action_group.setExclusive(True)  # ラジオボタンの有効化

        actions = [
            ExpandAction("#1 まで展開", self, depth=1),
            ExpandAction("#2 まで展開", self, depth=2),
            ExpandAction("#3 まで展開", self, depth=3),
            ExpandAction("#4 まで展開", self, depth=4),
            ExpandAction("#5 まで展開", self, depth=5),
            ExpandAction("BLOCK まで展開", self, depth=6),
        ]
        self._set_expand_actions(actions)

    def _set_expand_actions(self, actions: list[ExpandAction]) -> None:
        for action in actions:
            self._set_expand_action(action)

    def _set_expand_action(self, action: ExpandAction) -> None:
        self.addAction(action)
        self._action_group.addAction(action)  # ラジオボタン用

    def _on_expand_depth_requested(self, action: ExpandAction) -> None:
        """ツリー展開時に呼び出されるスロット"""
        self.expandDepthChanged.emit(action.expand_depth)


class ExpandAction(QAction):
    """
    `MaterialTreeView` を展開するアクション

    - `level` には 1~6 を指定する
    """

    def __init__(self, text: str, parent: MaterialTreeViewContextMenu, depth: int):
        super().__init__(text, parent)
        self._expand_depth = depth
        self.triggered.connect(lambda _: parent._on_expand_depth_requested(self))
        self.setCheckable(True)  # チェックボタン表示

        # 現在の展開深さと一致する場合、チェック表示
        if self._expand_depth == self.tree_view.expand_depth:
            self.setChecked(True)

    @property
    def expand_depth(self) -> int:
        """展開レベル"""
        return self._expand_depth

    @property
    def tree_view(self) -> MaterialTreeView:
        context_menu = self.parent()
        assert isinstance(context_menu, MaterialTreeViewContextMenu)
        tree_view = context_menu.parent()
        assert isinstance(tree_view, MaterialTreeView)
        return tree_view
