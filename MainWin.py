import time

import serial.tools.list_ports as p
import serial
import serial.rs485
from PyQt5.Qt import *
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import tlt
import func
import multiprocessing as ml
import sys

def Flicking_func(color_posse, COM, time):
    for y in range(5):
        for i in range(1, 5):
            adr = bytearray(func.convert_to_byte(i, color_posse))
            adr = func.broadcast_write(adr)
            adr = func.add_crc(func.calculate_crc16_modbus(adr), adr)
            print(adr)
            func.search(COM, adr, time)


class MainWindow(QtWidgets.QMainWindow, tlt.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.chan_stat = False
        self.isFlicking = False
        self.label.setVisible(False)
        self.pushButton.setText("")
        self.pushButton.setIcon(QIcon('rf_icon.png'))
        self.pushButton.setIconSize(QSize(30, 30))
        self.pushButton.clicked.connect(self.find_com)
        self.anim = QMovie('rf_anim2.gif')
        self.label.setMovie(self.anim)
        self.stat = QPixmap('black_crl.png')
        self.stat1 = QPixmap('red_crl.png')
        self.stat2 = QPixmap('yellow_crl.png')
        self.stat3 = QPixmap('green_crl.png')
        self.stat1_off = func.decrease_brightness('red_crl.png', 130)
        self.stat2_off = func.decrease_brightness('yellow_crl.png', 130)
        self.stat3_off = func.decrease_brightness('green_crl.png', 130)
        self.channels = [self.chanal_10, self.chanal_11, self.chanal_12,
                        self.chanal_20, self.chanal_21, self.chanal_22,
                        self.chanal_30, self.chanal_31, self.chanal_32,
                        self.chanal_40, self.chanal_41, self.chanal_42,
                        self.chanal_50, self.chanal_51, self.chanal_52,
                        self.chanal_60, self.chanal_61, self.chanal_62,
                        self.chanal_70, self.chanal_71, self.chanal_72,
                        self.chanal_80, self.chanal_81, self.chanal_82,
                        self.chanal_90, self.chanal_91, self.chanal_92,
                        self.chanal_100, self.chanal_101, self.chanal_102,
                        self.chanal_110, self.chanal_111, self.chanal_112,
                        self.chanal_120, self.chanal_121, self.chanal_122,
                        self.chanal_130, self.chanal_131, self.chanal_132,
                        self.chanal_140, self.chanal_141, self.chanal_142,
                        self.chanal_150, self.chanal_151, self.chanal_152,
                        self.chanal_160, self.chanal_161, self.chanal_162,
                         self.chanal_00, self.chanal_01, self.chanal_02]
        self.channels_txt = [self.chanaltxt_10, self.chanaltxt_11, self.chanaltxt_12,
                        self.chanaltxt_20, self.chanaltxt_21, self.chanaltxt_22,
                        self.chanaltxt_30, self.chanaltxt_31, self.chanaltxt_32,
                        self.chanaltxt_40, self.chanaltxt_41, self.chanaltxt_42,
                        self.chanaltxt_50, self.chanaltxt_51, self.chanaltxt_52,
                        self.chanaltxt_60, self.chanaltxt_61, self.chanaltxt_62,
                        self.chanaltxt_70, self.chanaltxt_71, self.chanaltxt_72,
                        self.chanaltxt_80, self.chanaltxt_81, self.chanaltxt_82,
                        self.chanaltxt_90, self.chanaltxt_91, self.chanaltxt_92,
                        self.chanaltxt_100, self.chanaltxt_101, self.chanaltxt_102,
                        self.chanaltxt_110, self.chanaltxt_111, self.chanaltxt_112,
                        self.chanaltxt_120, self.chanaltxt_121, self.chanaltxt_122,
                        self.chanaltxt_130, self.chanaltxt_131, self.chanaltxt_132,
                        self.chanaltxt_140, self.chanaltxt_141, self.chanaltxt_142,
                        self.chanaltxt_150, self.chanaltxt_151, self.chanaltxt_152,
                        self.chanaltxt_160, self.chanaltxt_161, self.chanaltxt_162,
                             self.chanaltxt_00, self.chanaltxt_01, self.chanaltxt_02]
        self.off_stat()
        self.con_but.clicked.connect(self.find_modules)
        self.pushButton_2.clicked.connect(self.rep_request)
        self.pushButton_3.clicked.connect(self.on_off)
        self.pushButton_4.clicked.connect(self.yellow_test)
        self.pushButton_5.clicked.connect(self.set_def_color)
        self.pushButton_6.clicked.connect(self.flicking)

    def find_anim(self):
        if self.pushButton.isVisible():
            self.pushButton.setVisible(False)
            self.label.setVisible(True)
            self.label.movie().start()
            QTimer.singleShot(1000, self.find_anim)
        else:
            self.label.movie().stop()
            self.label.setVisible(False)
            self.pushButton.setVisible(True)

    def find_com(self):
        self.comboBox.clear()
        ports = p.comports()
        active = [i.device for i in ports]
        self.comboBox.addItems(active)
        self.find_anim()

    def find_modules(self):
        self.modul_list.clear()
        message = bytearray(b'\x01\x03\x00\x00\x00\x07')
        disp_channel_ind = 0
        chanel_stat_ind = self.channel_status()
        for i in range(17):
            msg_crc = func.add_crc(func.calculate_crc16_modbus(message), message)
            if self.comboBox.currentText() != '' and i != 16:
                temp = func.search(self.comboBox.currentText(), msg_crc, 0.05)
                if temp != b'':
                    self.modul_list.addItem('MOD' + str(temp[4]))
                    color_type = func.get_seq_true(2, [temp], 4, 13)
                    color_type[0].pop(-1)
                    for color in color_type[0]:
                        if func.get_bit_value(chanel_stat_ind, disp_channel_ind):
                            if color == 1:
                                self.channels[disp_channel_ind].setPixmap(self.stat1)
                            elif color == 2:
                                self.channels[disp_channel_ind].setPixmap(self.stat2)
                            elif color == 3:
                                self.channels[disp_channel_ind].setPixmap(self.stat3)
                            else:
                                self.channels[disp_channel_ind].setPixmap(self.stat)
                        else:
                            if color == 1:
                                self.channels[disp_channel_ind].setPixmap(self.stat1_off)
                            elif color == 2:
                                self.channels[disp_channel_ind].setPixmap(self.stat2_off)
                            elif color == 3:
                                self.channels[disp_channel_ind].setPixmap(self.stat3_off)
                            else:
                                self.channels[disp_channel_ind].setPixmap(self.stat)
                        disp_channel_ind += 1
                    message[0] += 1
            elif self.comboBox.currentText() != '' and i == 16:
                if func.search(self.comboBox.currentText(), b'\x64\x03\x00\x00\x00\x01\x8D\xFF', 0.05) != b'':
                    self.modul_list.addItem('MOD_DF')
                    func.search(self.comboBox.currentText(), b'\x64\x10\x00\x07\x00\x01\x02\x00\x07\x71\x77', 0.05)
            else:
                print('не трогай ебанет!')

    def rep_request(self):
        msg_validity = bytearray(b'\x01\x03\x00\x0B\x00\x02')
        msg_pw = bytearray(b'\x01\x03\x00\x0D\x00\x03')
        msg_status = bytearray(b'\x00\x03\x00\x07\x00\x04')
        req_st = func.get_seq_true(2, [func.search(self.comboBox.currentText(), func.add_crc(func.calculate_crc16_modbus(msg_status), msg_status), 0.05)], 4)
        req_st = func.from_bytes_to_int(req_st[0])
        print(req_st)
        for i in range(self.modul_list.count() - 1):
            req_val = [func.search(self.comboBox.currentText(),
                                 func.add_crc(func.calculate_crc16_modbus(msg_validity), msg_validity), 0.05)]
            req_val = func.get_seq_true(2, req_val, 4)
            req_pw = [func.search(self.comboBox.currentText(),
                                          func.add_crc(func.calculate_crc16_modbus(msg_pw), msg_pw), 0.05)]
            req_pw = func.get_seq_true(2, req_pw, 6)
            req_full = req_val[0] + req_pw[0]
            msg_validity[0] += 1
            msg_pw[0] += 1

            #for _ in range(3):
            #    if func.get_bit_value(req_pw[4], _) and func.get_bit_value(req_st[], i + _):
            #
            #    else:
            #        self.channels_txt[i + _].setText('?')
            #        self.setVisible(True)

    def on_off(self):
        if not self.chan_stat:
            msg_on = bytearray(b'\x00\x10\x00\x07\x00\x04\x08\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
            msg_on = func.add_crc(func.calculate_crc16_modbus(msg_on), msg_on)
            print(func.search(self.comboBox.currentText(), msg_on, 0.05))
            self.chan_stat = True
        else:
            msg_on = bytearray(b'\x00\x10\x00\x07\x00\x04\x08\x00\x00\x00\x00\x00\x00\x00\x00')
            msg_on = func.add_crc(func.calculate_crc16_modbus(msg_on), msg_on)
            print(func.search(self.comboBox.currentText(), msg_on, 0.05))
            self.chan_stat = False

    def yellow_test(self):
        msg_yellow = bytearray(b'\x01\x10\x00\x05\x00\x02\x04\x02\x02\x02\x02')
        for i in range(self.modul_list.count() - 1):
            print(func.search(self.comboBox.currentText(),
                              func.add_crc(func.calculate_crc16_modbus(msg_yellow), msg_yellow), 0.05))
            msg_yellow[0] += 1
        print(func.search(self.comboBox.currentText(), b'\x64\x10\x00\x07\x00\x01\x02\x00\x07\x71\x77', 0.05))
        self.chan_stat = False
        self.on_off()

    def set_def_color(self):
        msg_def_color = bytearray(b'\x01\x10\x00\x05\x00\x02\x04\x02\x01\x15\x03')
        for i in range(self.modul_list.count() - 1):
            print(func.search(self.comboBox.currentText(),
                              func.add_crc(func.calculate_crc16_modbus(msg_def_color), msg_def_color), 0.05))
            msg_def_color[0] += 1

    def flicking(self):
        msg_get_color = bytearray(b'\x01\x03\x00\x05\x00\x02')
        temp = []
        for i in range(self.modul_list.count() - 1):
            temp.append(func.search(self.comboBox.currentText(),
                                    func.add_crc(func.calculate_crc16_modbus(msg_get_color), msg_get_color), 0.05))
        color_pos = func.get_seq_true(self.modul_list.count(), temp, 4, 3)
        self.on(color_pos, self.comboBox.currentText())
        #while True:
        #    for i in range(1, 5):
        #        adr = bytearray(func.convert_to_byte(i, color_pos))
        #        adr = func.broadcast_write(adr)
        #        adr = func.add_crc(func.calculate_crc16_modbus(adr), adr)
        #        print(adr)
        #        func.search(self.comboBox.currentText(), adr, 0.05)



    def off_stat(self):
        for i in range(len(self.channels)):
            self.channels[i].setPixmap(self.stat)
            self.channels_txt[i].setVisible(False)

    def channel_status(self):
        msg_status = bytearray(b'\x01\x03\x00\x07\x00\x04')
        req_st = func.get_seq_true(2, [
            func.search(self.comboBox.currentText(), func.add_crc(func.calculate_crc16_modbus(msg_status), msg_status),
                        0.05)], 8, 3)
        req_st = func.from_bytes_to_int(req_st[0])
        return req_st

    def on(self, color_pose, COM):
        if not self.isFlicking:
            self.isFlicking = True
            if self.isFlicking:
                proc_2(color_pose, COM)
        else:
            self.isFlicking = False

def proc_1():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
def proc_2(color_pos, COM):
    multi_2 = ml.Process(target=Flicking_func, args=(color_pos, COM, 0.05))
    multi_2.start()
    multi_3 = ml.Process()


if __name__ == '__main__':
    import sys

    multi_1 = ml.Process(target=proc_1)
    multi_1.start()

