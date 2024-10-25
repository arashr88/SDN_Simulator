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

    def create_file_menu(self) -> qtw.QMenu:
        """
        Creates the basis of the file menu along with adding an open action.
        """
        # add file menu
        file_menu_obj = self.menu_bar_obj.addMenu('File')

        # create file menu actions
        load_config_action = self.menu_bar_action_handler_obj.create_load_config_from_file_action()
        display_topology_action = self.menu_bar_action_handler_obj.create_display_topology_action()
        settings_action = self.menu_bar_action_handler_obj.create_settings_action()
        exit_action = self.menu_bar_action_handler_obj.create_exit_action()

        # arrange file menu actions
        file_menu_obj.addAction(load_config_action)
        file_menu_obj.addAction(display_topology_action)
        file_menu_obj.addAction(settings_action)
        file_menu_obj.addSeparator()
        file_menu_obj.addAction(exit_action)

        return file_menu_obj

        """
        Creates the edit menu section.
        """
        self.edit_menu_obj = self.menu_bar_obj.addMenu('&Edit')

    def create_help_menu(self):
        """
        Creates the help menu section.
        """

    def create_plot_menu(self) -> qtw.QMenu:
        """
        Creates the plot menu
        """
        # add plot menu
        plot_menu_obj = self.menu_bar_obj.addMenu('Plot')

        # create plot menu actions e.g. plot >, configure plotting settings, export plot, etc
        plot_submenu_obj = qtw.QMenu('Plot', plot_menu_obj)

        plots = GUI_DEFAULT_SETTINGS['plots']
        for plot_action in plots:
            action = self.menu_bar_action_handler_obj.create_plot_sm_action(plot_action)
            action.setParent(plot_submenu_obj)
            plot_submenu_obj.addAction(action)

        config_plot_settings_action = self.menu_bar_action_handler_obj.create_configure_plot_settings_action()
        export_plot_action = self.menu_bar_action_handler_obj.create_export_plot_action()

        # arrange plot menu actions
        plot_menu_obj.addMenu(plot_submenu_obj)
        plot_menu_obj.addAction(config_plot_settings_action)
        plot_menu_obj.addSeparator()
        plot_menu_obj.addAction(export_plot_action)

        return plot_menu_obj
