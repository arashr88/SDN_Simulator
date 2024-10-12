from PyQt5 import QtWidgets as qtw
from gui_scripts.gui_args.config_args import AlertCode


class Alert(qtw.QMessageBox):

    def __init__(self, **kwargs):
        self.arguments = kwargs
        super().__init__(parent=self.arguments.get('parent', None))

    def alert(self, alert_code: AlertCode = 0):
        parent = self.arguments.get('parent', None)
        title = self.arguments.get('title', '')
        text = self.arguments.get('text', '')

        if alert_code == AlertCode.INFORMATION:
            self.information(parent, title, text)
        elif alert_code == AlertCode.CRITICAL:
            self.critical(parent, title, text)
        elif alert_code == AlertCode.WARNING:
            self.warning(parent, title, text)
        else:
            self.question(parent, title, text)
