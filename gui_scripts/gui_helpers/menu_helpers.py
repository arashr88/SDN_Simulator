# pylint: disable=c-extension-no-member

import networkx as nx
from PyQt5 import QtWidgets as qtw, QtCore as qtc
from data_scripts.structure_data import create_network

from gui_scripts.gui_helpers.topology_helpers import TopologyCanvas
from gui_scripts.gui_helpers.general_helpers import SettingsDialog
from gui_scripts.gui_args.config_args import GUI_DEFAULT_SETTINGS
from gui_scripts.gui_helpers.dialogs import Alert
from gui_scripts.gui_args.config_args import AlertCode


class MenuBar(qtw.QMenuBar):
    """
    The Menu Bar.
    """
    app_close_signal_relay = qtc.pyqtSignal()

    def __init__(self, main_window_ref: qtw.QMainWindow, parent=None):
        """
        Initializes the menu_bar.

        :param main_window_ref: reference to the main window on which it belongs
        :type QtWidgets.QMainWindow:
        """
        super().__init__(parent)
        self.main_window_ref_obj = main_window_ref
        self.menu_creator_obj = MenuCreator(self, self.main_window_ref_obj)

        self.file_menu_obj = None
        self.help_menu_obj = None
        self.edit_menu_obj = None
        self.plot_menu_obj = None

        self.setup_menu_bar()

    def setup_menu_bar(self):
        """
        Sets up the menu options for the menu bar.

        :param : None
        :return : None
        """
        self.file_menu_obj = self.menu_creator_obj.create_file_menu()
        self.help_menu_obj = self.menu_creator_obj.create_edit_menu()
        self.edit_menu_obj = self.menu_creator_obj.create_plot_menu()
        self.plot_menu_obj = self.menu_creator_obj.create_help_menu()


class MenuCreator:
    """
    Contains methods for configuring the menubar with menu items.
    """

    def __init__(self, menu_bar: MenuBar, main_window_ref: qtw.QMainWindow):
        """
        Initializes the menu helpers object.

        :param menu_bar: A reference to the main window menu bar
        :type menu_bar: QtWidgets.QMenuBar
        :return : None
        """
        self.menu_bar_obj = menu_bar
        self.main_window_ref_obj = main_window_ref
        self.menu_bar_action_handler_obj = MenuActionHandler(self.menu_bar_obj, self.main_window_ref_obj)
        """
        Creates the basis of the file menu along with adding an open action.
        """
        self.file_menu_obj = self.menu_bar_obj.addMenu('&File')
        open_action = QtWidgets.QAction('&Load Configuration from File', self.menu_bar_obj)
        open_action.triggered.connect(self.open_file)
        self.file_menu_obj.addAction(open_action)

    def create_edit_menu(self):
        """
        Creates the edit menu section.
        """
        self.edit_menu_obj = self.menu_bar_obj.addMenu('&Edit')

    def create_help_menu(self):
        """
        Creates the help menu section.
        """
        self.help_menu_obj = self.menu_bar_obj.addMenu('&Help')
