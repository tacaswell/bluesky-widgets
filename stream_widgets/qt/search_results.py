from qtpy import QtCore
from qtpy.QtCore import QAbstractTableModel, Qt
from qtpy.QtWidgets import QAbstractItemView, QHeaderView, QTableView


class _SearchResultsModel(QAbstractTableModel):
    """
    Qt model connecting our model to Qt's model--view machinery
    """
    def __init__(self, model, *args, **kwargs):
        self.model = model  # our internal model for the components subpackage
        super().__init__(*args, **kwargs)

        # Changes to the model update the GUI.
        self.model.events.reset.connect(self.on_entries_changed)

    def on_entries_changed(self, event):
        # TODO Maybe expose to signals out of the model, one that is emitted
        # before it starts breaking its internal state and one after the new
        # state is ready.
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent=None):
        return self.model.get_length()

    def columnCount(self, parent=None):
        return len(self.model.headings)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return super().headerData(section, orientation, role)
        if orientation == Qt.Horizontal and section < self.columnCount():
            return str(self.model.headings[section])
        elif orientation == Qt.Vertical and section < self.rowCount():
            return section

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():  # does > 0 bounds check
            return QtCore.QVariant()
        if index.column() >= self.columnCount() or index.row() >= self.rowCount():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return self.model.get_data(index.row(), index.column())
        else:
            return QtCore.QVariant()


class QtSearchResults(QTableView):
    """
    Table of search results

    Parameters
    ----------
    model: stream_widgets.components.search_results.SearchResults
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(False)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.setAlternatingRowColors(True)
        self.setModel(_SearchResultsModel(model))

        # Notify model of changes to selection.
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Update the view to changes in the model.
        self.model.selected_rows.events.added(self.on_row_added)
        self.model.selected_rows.events.removed(self.on_row_removed)

    def on_selection_changed(self, selected, deselected):
        # One would expect we could ask Qt directly for the rows, as opposed to
        # using set() here, but I cannot find such a method.
        for row in set(index.row() for index in deselected.indexes()):
            self.model.selected_rows.remove(row)
        for row in set(index.row() for index in selected.indexes()):
            self.model.selected_rows.append(row)

    def on_row_added(self, event):
        # TODO
        ...

    def on_row_removed(self, event):
        # TODO
        ...
