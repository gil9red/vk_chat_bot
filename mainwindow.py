#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtWebKit import *
from PySide.QtNetwork import *

from mainwindow_ui import Ui_MainWindow
from common import *


logger = get_logger('main_window')


class MainWindow(QMainWindow, QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('vk_chat_bot')

        # Все действия к прикрепляемым окнам поместим в меню
        for dock in self.findChildren(QDockWidget):
            self.ui.menuDockWindow.addAction(dock.toggleViewAction())

        # Все действия к toolbar'ам окнам поместим в меню
        for tool in self.findChildren(QToolBar):
            self.ui.menuTools.addAction(tool.toggleViewAction())

        # Выполнение кода в окне "Выполнение скрипта"
        self.ui.button_exec.clicked.connect(lambda x=None: exec(self.ui.code.toPlainText()))

        #
        #
        #

        # Чтобы не было проблем запуска компов с прокси:
        QNetworkProxyFactory.setUseSystemConfiguration(True)

        QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        # TODO: оптимищация
        # QWebSettings::PrintElementBackgrounds
        # QWebSettings.globalSettings().setAttribute(QWebSettings.AutoLoadImages, False)

        self.web_view = QWebView()
        self.setCentralWidget(self.web_view)

        self.web_view.load('http://www.boibot.com/en/')
        self.wait_loading()

        # TODO: Установка вопроса, отправка его
        # self.slog(
        # self.doc.evaluateJavaScript("""
        # //cleverbot.stimuluselement.value = "Расскажи анекдот!"
        # alert(cleverbot.stimuluselement.value)
        # alert(cleverbot.input)
        # alert(cleverbot.reply)
        # //cleverbot.sendAI()
        # """)
        # )

    def _get_doc(self):
        return self.web_view.page().mainFrame().documentElement()

    doc = property(_get_doc)

    def wait_loading(self):
        """Функция ожидания загрузки страницы. Использовать только при изменении url."""

        logger.debug('Начинаю ожидание загрузки страницы.')

        # Ждем пока прогрузится страница
        loop = QEventLoop()
        self.web_view.loadFinished.connect(loop.quit)
        loop.exec_()

        logger.debug('Закончено ожидание загрузки страницы.')

    # TODO: добавить возможность выбрать область поиска элемента для клика, а то она все время вся страница -- self.doc
    def click_tag(self, css_path):
        """Функция находит html тег по указанному пути и эмулирует клик на него.

        Строки в css_path нужно оборачивать в апострофы.
        Пример:
            # Кликаем на кнопку "Отнять у слабого"
            self.click_tag("div[class='button-big btn f1']")

            # Кликаем на кнопку "Искать другого"
            self.click_tag(".button-search a")
        """

        logger.debug('Выполняю клик по тегу: %s', css_path)

        # Используем для клика jQuery
        code = """
        tag = $("{}");
        tag.click();""".format(css_path)

        ok = self.doc.evaluateJavaScript(code)
        if ok is None:
            logger.warn('Выполнение js скрипта неудачно. Code:\n' + code)

    def slog(self, text):
        """Функция для добавления текста в виджет-лог, находящегося на форме."""

        self.ui.simple_log.appendPlainText('{}'.format(text))

    def read_settings(self):
        # TODO: при сложных настройках, лучше перейти на json или yaml
        config = QSettings(CONFIG_FILE, QSettings.IniFormat)
        self.restoreState(config.value('MainWindow_State'))
        self.restoreGeometry(config.value('MainWindow_Geometry'))

    def write_settings(self):
        config = QSettings(CONFIG_FILE, QSettings.IniFormat)
        config.setValue('MainWindow_State', self.saveState())
        config.setValue('MainWindow_Geometry', self.saveGeometry())

    def closeEvent(self, *args, **kwargs):
        self.write_settings()
        super().closeEvent(*args, **kwargs)
