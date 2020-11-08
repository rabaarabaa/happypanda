# """
# This file is part of Happypanda.
# Happypanda is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Happypanda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Happypanda.  If not, see <http://www.gnu.org/licenses/>.
# """

import sys, logging, logging.handlers, os, argparse, platform, scandir
import traceback

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtGui import QFontDatabase

try:
    from database import db, db_constants
    import app
    import app_constants
    import gallerydb
    import utils
except ImportError:
    from .database import db, db_constants
    from . import app
    from . import app_constants
    from . import gallerydb
    from . import utils


# IMPORTANT STUFF
def start(test=False):
    app_constants.APP_RESTART_CODE = -123456789

    if os.name == 'posix':
        main_path = os.path.dirname(os.path.realpath(__file__))
        log_path = os.path.join(main_path, 'happypanda.log')
        debug_log_path = os.path.join(main_path, 'happypanda_debug.log')
    else:
        log_path = 'happypanda.log'
        debug_log_path = 'happypanda_debug.log'
    if os.path.exists('cacert.pem'):
        os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.getcwd(), "cacert.pem")

    parser = argparse.ArgumentParser(prog='Happypanda',
                                     description='A manga/doujinshi manager with tagging support')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='happypanda_debug_log.log will be created in main directory')
    parser.add_argument('-v', '--version', action='version',
                        version='Happypanda v{}'.format(app_constants.vs))
    parser.add_argument('-e', '--exceptions', action='store_true',
                        help='Disable custom excepthook')
    parser.add_argument('-x', '--dev', action='store_true',
                        help='Development Switch')

    args = parser.parse_args()
    log_handlers = []
    log_level = logging.INFO
    if args.dev:
        log_handlers.append(logging.StreamHandler())
    if args.debug:
        print("happypanda_debug.log created at {}".format(os.getcwd()))
        # create log
        try:
            with open(debug_log_path, 'x') as f:
                pass
        except FileExistsError:
            pass

        log_handlers.append(logging.FileHandler(debug_log_path, 'w', 'utf-8'))
        log_level = logging.DEBUG
        app_constants.DEBUG = True
    else:
        try:
            with open(log_path, 'x') as f:
                pass
        except FileExistsError:
            pass
        log_handlers.append(logging.handlers.RotatingFileHandler(
            log_path, maxBytes=1000000 * 10, encoding='utf-8', backupCount=2))

    # Fix for logging not working
    # clear the handlers first before adding these custom handler
    # http://stackoverflow.com/a/15167862
    logging.getLogger('').handlers = []
    logging.basicConfig(level=log_level,
                        format='%(asctime)-8s %(levelname)-6s %(name)-6s %(message)s',
                        datefmt='%d-%m %H:%M',
                        handlers=tuple(log_handlers))

    log = logging.getLogger(__name__)
    log_i = log.info
    log_d = log.debug
    log_w = log.warning
    log_e = log.error
    log_c = log.critical

    if not args.exceptions:
        def uncaught_exceptions(ex_type, ex, tb):
            log_c(''.join(traceback.format_tb(tb)))
            log_c('{}: {}'.format(ex_type, ex))
            traceback.print_exception(ex_type, ex, tb)

        sys.excepthook = uncaught_exceptions

    if app_constants.FORCE_HIGH_DPI_SUPPORT:
        log_i("Enabling high DPI display support")
        os.environ.putenv("QT_DEVICE_PIXEL_RATIO", "auto")

    effects = [Qt.UI_AnimateCombo, Qt.UI_FadeMenu, Qt.UI_AnimateMenu,
               Qt.UI_AnimateTooltip, Qt.UI_FadeTooltip]
    for effect in effects:
        QApplication.setEffectEnabled(effect)

    application = QApplication(sys.argv)
    application.setOrganizationName('Pewpews')
    application.setOrganizationDomain('https://github.com/Pewpews/happypanda')
    application.setApplicationName('Happypanda')
    application.setApplicationDisplayName('Happypanda')
    application.setApplicationVersion('v{}'.format(app_constants.vs))
    application.setAttribute(Qt.AA_UseHighDpiPixmaps)
    application.font().setStyleStrategy(application.font().PreferAntialias)

    log_i('Starting Happypanda...'.format(app_constants.vs))
    if args.debug:
        log_i('Running in debug mode'.format(app_constants.vs))
        import pprint
        sys.displayhook = pprint.pprint
    app_constants.load_icons()
    log_i('Happypanda Version {}'.format(app_constants.vs))
    log_i('OS: {} {}\n'.format(platform.system(), platform.release()))
    conn = None
    try:
        conn = db.init_db()
        log_d('Init DB Conn: OK')
        log_i("DB Version: {}".format(db_constants.REAL_DB_VERSION))
    except:
        log_c('Invalid database')
        log.exception('Database connection failed!')
        from PyQt5.QtGui import QIcon
        from PyQt5.QtWidgets import QMessageBox
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(app_constants.APP_ICO_PATH))
        msg_box.setText('Invalid database')
        msg_box.setInformativeText("Do you want to create a new database?")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        if msg_box.exec() == QMessageBox.Yes:
            pass
        else:
            application.exit()
            log_d('Normal Exit App: OK')
            sys.exit()

    def start_main_window(conn):
        db.DBBase._DB_CONN = conn
        # if args.test:
        #	import threading, time
        #	ser_list = []
        #	for x in range(5000):
        #		s = gallerydb.gallery()
        #		s.profile = app_constants.NO_IMAGE_PATH
        #		s.title = 'Test {}'.format(x)
        #		s.artist = 'Author {}'.format(x)
        #		s.path = app_constants.static_dir
        #		s.type = 'Test'
        #		s.language = 'English'
        #		s.info = 'I am number {}'.format(x)
        #		ser_list.append(s)

        #	done = False
        #	thread_list = []
        #	i = 0
        #	while not done:
        #		try:
        #			if threading.active_count() > 5000:
        #				thread_list = []
        #				done = True
        #			else:
        #				thread_list.append(
        #					threading.Thread(target=gallerydb.galleryDB.add_gallery,
        #					  args=(ser_list[i],)))
        #				thread_list[i].start()
        #				i += 1
        #				print(i)
        #				print('Threads running: {}'.format(threading.activeCount()))
        #		except IndexError:
        #			done = True

        WINDOW = app.AppWindow(args.exceptions)

        # styling
        d_style = app_constants.default_stylesheet_path
        u_style = app_constants.user_stylesheet_path

        if len(u_style) > 0:
            try:
                style_file = QFile(u_style)
                log_i('Select userstyle: OK')
            except:
                style_file = QFile(d_style)
                log_i('Select defaultstyle: OK')
        else:
            style_file = QFile(d_style)
            log_i('Select defaultstyle: OK')

        style_file.open(QFile.ReadOnly)
        style = str(style_file.readAll(), 'utf-8')
        application.setStyleSheet(style)
        try:
            os.mkdir(app_constants.temp_dir)
        except FileExistsError:
            try:
                for root, dirs, files in scandir.walk('temp', topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
            except:
                log.exception("Empty temp: FAIL")
        log_d('Create temp: OK')

        if test:
            return application, WINDOW

        return application.exec_()

    def db_upgrade():
        log_d('Database connection failed')
        from PyQt5.QtGui import QIcon
        from PyQt5.QtWidgets import QMessageBox

        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(app_constants.APP_ICO_PATH))
        msg_box.setText('Incompatible database!')
        msg_box.setInformativeText("Do you want to upgrade to newest version?" +
                                   " It shouldn't take more than a second. Don't start a new instance!")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        if msg_box.exec() == QMessageBox.Yes:
            utils.backup_database()
            import threading
            db_p = db_constants.DB_PATH
            db.add_db_revisions(db_p)
            conn = db.init_db()
            return start_main_window(conn)
        else:
            application.exit()
            log_d('Normal Exit App: OK')
            return 0

    if conn:
        return start_main_window(conn)
    else:
        return db_upgrade()


if __name__ == '__main__':
    current_exit_code = 0
    while current_exit_code == app_constants.APP_RESTART_CODE:
        current_exit_code = start()
    sys.exit(current_exit_code)
