# pylint: disable=c-extension-no-member

import os
import signal
import subprocess
import sys

from PyQt5 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg

from gui_scripts.gui_args.config_args import SETTINGS_CONFIG_DICT


class SettingsDialog(qtw.QDialog):  # pylint: disable=too-few-public-methods
    """
    The settings window in the menu bar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings Menu")
        self.resize(400, 600)
        self.layout = qtw.QVBoxLayout()
        self.tabs = qtw.QTabWidget()
        self.settings_widgets = {}
        self._setup_layout()

        self.setLayout(self.layout)

    def _setup_layout(self):
        for category in SETTINGS_CONFIG_DICT:
            tab = qtw.QWidget()
            tab_layout = qtw.QFormLayout()
            for setting in category["settings"]:
                widget, label = self._create_widget(setting)
                if isinstance(widget, qtw.QLabel): # choosing QLabel for all headers
                    tab_layout.addRow(widget)
                else:
                    tab_layout.addRow(label, widget)
                self.settings_widgets[label] = widget
            tab.setLayout(tab_layout)
            self.tabs.addTab(tab, category["category"])
        self.layout.addWidget(self.tabs)

        self._setup_buttons()

    @staticmethod
    def _create_widget(setting):
        widget_type = setting["type"]
        widget = None
        label = setting["label"]
        if widget_type == "combo":
            widget = qtw.QComboBox()
            widget.addItems(setting["options"])
            widget.setCurrentText(setting["default"])
        elif widget_type == "check":
            widget = qtw.QCheckBox()
            widget.setChecked(setting["default"])
        elif widget_type == "line":
            widget = qtw.QLineEdit(setting["default"])
        elif widget_type == "spin":
            widget = qtw.QSpinBox()
            widget.setValue(setting["default"])
            widget.setMinimum(setting.get("min", 0))
            widget.setMaximum(setting.get("max", 100))
        elif widget_type == "double_spin":
            widget = qtw.QDoubleSpinBox()
            widget.setValue(setting["default"])
            widget.setMinimum(setting.get("min", 0.0))
            widget.setSingleStep(setting.get("step", 1.0))
        elif widget_type == "header":
            widget = qtw.QLabel(label)
            widget.setStyleSheet("""
                font-weight: bold;
                font-size: 13pt;
            """)
        return widget, label

    def _setup_buttons(self):
        buttons = qtw.QDialogButtonBox(
            qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def get_settings(self):
        """
        Gets and structures all configuration settings.

        :return: The simulation configuration.
        :rtype: dict
        """
        settings = {}
        for category in SETTINGS_CONFIG_DICT:
            category_name = category["category"].lower() + "_settings"
            settings[category_name] = {}
            for setting in category["settings"]:
                label = setting["label"]
                widget = self.settings_widgets[label]
                settings[category_name][
                    self._format_label(label)] = self._get_widget_value(widget)
        return {"s1": settings}

    @staticmethod
    def _format_label(label):
        return label.lower().replace(" ", "_").replace(":", "")

    @staticmethod
    def _get_widget_value(widget):
        resp = None
        if isinstance(widget, qtw.QComboBox):
            resp = widget.currentText()
        elif isinstance(widget, qtw.QCheckBox):
            resp = widget.isChecked()
        elif isinstance(widget, qtw.QLineEdit):
            resp = widget.text()
        elif isinstance(widget, qtw.QSpinBox):
            resp = widget.value()
        elif isinstance(widget, qtw.QDoubleSpinBox):
            resp = widget.value()

        return resp


class SimulationThread(qtc.QThread):
    """
    Sets up simulation thread runs.
    """
    progress_changed = qtc.pyqtSignal(int)
    finished_signal = qtc.pyqtSignal(str)
    output_hints_signal = qtc.pyqtSignal(str)

    def __init__(self):
        super(SimulationThread, self).__init__()  # pylint: disable=super-with-arguments

        self.simulation_process = None
        self.paused = False
        self.stopped = False
        self.mutex = qtc.QMutex()
        self.pause_condition = qtc.QWaitCondition()

    def _run(self):
        for output_line in self.simulation_process.stdout:
            with qtc.QMutexLocker(self.mutex):
                if self.stopped:
                    break

                while self.paused:
                    self.pause_condition.wait(
                        self.mutex
                    )

            self.output_hints_signal.emit(output_line)

        self.simulation_process.stdout.close()
        self.simulation_process.wait()

        self.finished_signal.emit('Simulation done')
        self.output_hints_signal.emit(
            'Done...cleaning up simulation from thread')

    def run(self):
        """
        Overrides run method in QtCore.QThread.
        """
        command = os.path.join(os.getcwd(), "run_sim.py")

        self.simulation_process = subprocess.Popen(  # pylint: disable=consider-using-with
            args=[sys.executable, command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self._run()

    def handle_process_state(self, process_state: qtc.QProcess.ProcessState):  # pylint: disable=consider-using-with
        """
        Starts or runs a specific process.

        :param process_state: The current state of the process.
        :return: None
        """
        if process_state == qtc.QProcess.ProcessState.Starting:
            self.output_hints_signal.emit('Starting process')
        elif process_state == qtc.QProcess.ProcessState.Running:
            self.output_hints_signal.emit('Running process')

    def pause(self):
        """
        Pauses a single simulation thread.
        """
        with qtc.QMutexLocker(self.mutex):
            os.kill(self.simulation_process.pid, signal.SIGSTOP)
            self.paused = True
            self.output_hints_signal.emit('Pausing simulation from thread')

    def resume(self):
        """
        Resumes a simulation thread.
        """
        with qtc.QMutexLocker(self.mutex):
            os.kill(self.simulation_process.pid, signal.SIGCONT)
            self.paused = False
            self.output_hints_signal.emit('Resuming simulation from thread')
        self.pause_condition.wakeOne()

    def stop(self):
        """
        Stops a simulation thread.
        """
        with qtc.QMutexLocker(self.mutex):
            os.kill(self.simulation_process.pid, signal.SIGKILL)
            self.stopped = True
            self.paused = False
            self.output_hints_signal.emit('Stopping simulation from thread')
        self.pause_condition.wakeOne()


class DirectoryTreeView(qtw.QTreeView):
    """
    Sets up a new directory tree view.
    """
    item_double_clicked_sig = qtc.pyqtSignal(qtc.QModelIndex)

    def __init__(
        self,
        file_model: qtw.QFileSystemModel,
        parent: qtw.QWidget = None
    ):
        super().__init__(parent)
        self.setSelectionBehavior(qtw.QTreeView.SelectRows)
        self.setSelectionMode(qtw.QTreeView.SingleSelection)
        self.setUniformRowHeights(True)

        self.model = file_model
        self.setModel(self.model)

        self.copied_path = None
        self.is_directory = False
        self.is_cut_operation = False

    def copy_item(
        self,
        source_index: qtc.QModelIndex,
        is_cut_operation: bool = False
    ):
        """
        Implements the copy/cut operations in the directory tree view.
        :param source_index:        the QModelIndex of the item to be copied
        or cut.
        :param is_cut_operation:    boolean to choose between copying
        and cutting.
        """
        # Store the source path and determine if it's a directory
        self.copied_path = self.model.filePath(source_index)
        self.is_directory = qtc.QFileInfo(self.copied_path).isDir()
        self.is_cut_operation = is_cut_operation

    def _copy_directory(
        self,
        source_dir: str,
        destination_dir: str
    ):
        """
        Copies a directory recursively

        :param source_dir:          Path to old directory location
        :param destination_dir:     Path to new directory location
        """
        source_obj = qtc.QDir(source_dir)
        destination_obj = qtc.QDir(destination_dir)

        destination_path = destination_obj.filePath(
            qtc.QFileInfo(source_dir).fileName())
        if not destination_obj.exists(destination_path):
            destination_obj.mkpath(destination_path)

        for file_name in source_obj.entryList(qtc.QDir.Files):
            qtc.QFile.copy(source_obj.absoluteFilePath(file_name),
                              qtc.QDir(destination_path).filePath(file_name))

        for subdir in source_obj.entryList(
                qtc.QDir.Dirs | qtc.QDir.NoDotAndDotDot):
            self._copy_directory(source_obj.absoluteFilePath(subdir), qtc.QDir(destination_path).filePath(subdir))

        if self.is_cut_operation:
            self.delete_directory(source_dir)

    def paste_item(
        self,
        destination_index: qtc.QModelIndex
    ):
        """
        Pastes a file/folder at destination_index.

        :param destination_index:    index of location where item is to be
        pasted.
        """
        if self.copied_path:
            destination_dir = self.model.filePath(destination_index)
            if not qtc.QFileInfo(destination_dir).isDir():
                destination_dir = qtc.QFileInfo(
                    destination_dir).absolutePath()

            if self.is_directory:
                self._copy_directory(self.copied_path, destination_dir)
            else:
                file_name = qtc.QFileInfo(self.copied_path).fileName()
                if qtc.QFile.copy(self.copied_path,
                                     qtc.QDir(destination_dir).filePath(
                                         file_name)):
                    pass  # basically do nothing
                else:
                    qtw.QMessageBox.critical(self, "Error",
                                                   "Failed to paste the file")

            if self.is_cut_operation:
                self._delete()
            self.refresh_view()

    def delete_item(
        self,
        target_index: qtc.QModelIndex
    ):
        """
        Delete an item from the tree.

        :param target_index:    Index of item to be deleted.
        """
        path = self.model.filePath(target_index)
        is_directory = qtc.QFileInfo(path).isDir()

        if is_directory:
            reply = qtw.QMessageBox.question(self, "Delete Directory",
                                                   f"Are you sure you want to delete the directory '{path}' and all its contents?",
                                                   qtw.QMessageBox.Yes | qtw.QMessageBox.No,
                                                   qtw.QMessageBox.No)
        else:
            reply = qtw.QMessageBox.question(self, "Delete File",
                                                   f"Are you sure you want to delete the file '{path}'?",
                                                   qtw.QMessageBox.Yes | qtw.QMessageBox.No,
                                                   qtw.QMessageBox.No)

        if reply == qtw.QMessageBox.Yes:
            if is_directory:
                qtc.QDir(path).removeRecursively()
            else:
                qtc.QFile.remove(path)
            self.refresh_view()  # Refresh the model to reflect the deletion

    def _delete(self):
        """
        Deletes an item after a paste operation
        """
        if self.is_directory:
            qtc.QDir(self.copied_path).removeRecursively()
        else:
            qtc.QFile.remove(self.copied_path)
        self.refresh_view()  # Refresh the model to reflect changes

    def handle_context_menu(
        self,
        position: qtc.QModelIndex
    ):
        """
        Callback function to handle contextEvent signal. The context menu
        created by this function is rooted at position.

        :param position:    index of item that generated the signal.
        """
        index = self.indexAt(position)
        if index.isValid():
            menu_obj = qtw.QMenu(self)

            menu_obj.addSeparator()
            copy_action = menu_obj.addAction("Copy")
            cut_action = menu_obj.addAction("Cut")
            paste_action = menu_obj.addAction("Paste")
            menu_obj.addSeparator()
            delete_action = menu_obj.addAction("Delete")
            menu_obj.addSeparator()

            action = menu_obj.exec_(self.viewport().mapToGlobal(position))

            if action == copy_action:
                self.copy_item(index)
            elif action == cut_action:
                self.copy_item(index, is_cut_operation=True)
            elif action == paste_action:
                self.paste_item(index)
            elif action == delete_action:
                self.delete_item(index)

    def refresh_view(self):
        """
        Refreshes the view of the tree model. Necessary when certain copy or cut
        operations are performed
        """
        self.setRootIndex(self.model.index(self.model.rootPath()))

    def mousePressEvent(self, event: qtg.QMouseEvent):  # pylint: disable=invalid-name
        """
        Overrides mousePressEvent in QTreeView for single click

        :param event:   event instance generated by a left mouse click
                        on this object.
        """
        index = self.indexAt(event.pos())
        if event.button() == qtc.Qt.LeftButton and index.isValid():
            self.setCurrentIndex(index)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):  # pylint: disable=invalid-name
        """
        Overrides mouseDoubleClickEvent in QTreeView for double-click

        :param event:   event instance generated by a right mouse click on
                        this object.
        """
        index = self.indexAt(event.pos())
        if event.button() == qtc.Qt.LeftButton and index.isValid():
            self.item_double_clicked_sig.emit(index)
        super().mouseDoubleClickEvent(event)
