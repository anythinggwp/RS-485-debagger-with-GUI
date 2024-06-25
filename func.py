import time

import serial
import serial.rs485
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5 import QtCore
from PyQt5.QtCore import Qt


def calculate_crc16_modbus(message):
    crc = 0xFFFF
    for byte in message:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def add_crc(crc_int, msg):
    temp = bytearray(msg)
    temp.append(crc_int & 0xFF)
    temp.append(crc_int >> 8)
    return temp


def search(com, message, freq):
    con = serial.Serial(com, baudrate=115200, timeout=freq)
    con.rs485_mode = serial.rs485.RS485Settings()
    con.write(message)
    temp = con.readline()
    con.close()
    return temp


def convert_to_byte(color, chanel):
    adr = bytearray()
    indices = []
    ind = 0
    adr_ind = 0
    for _ in range(len(chanel)):
        indices = [i for i in range(len(chanel[_])) if chanel[_][i] == color]
        if len(indices) == 2:
            indices = 2**indices[0] | 2**indices[1]
        elif len(indices) == 3:
            indices = 2 ** indices[0] | 2 ** indices[1] | 2 ** indices[2]
        elif len(indices) == 1:
            indices = 2 ** indices[0]
        else:
            indices = 0
        if ind == 0 and ind % 8 == 0:
            temp = indices << (ind % 8)
            adr.append(temp)
            ind += 3
        elif ind != 0 and ind % 8 != 0:
            temp = indices << (ind % 8)
            adr[adr_ind] = adr[adr_ind] | temp
            ind += 3
        else:
            temp = indices << (ind % 8)
            adr.append(adr[adr_ind] | temp)
            ind += 3
            adr_ind += 1
    return adr


def get_bit_value(num, bit_index):
    mask = 1 << bit_index
    bit_value = (num & mask) >> bit_index
    return bit_value


def get_seq_true(pw_mods_cnt, seq_arr, bytes_count, start_byte):
    true_pose = []
    for i in range(pw_mods_cnt - 1):
        true_pose.append(bytearray([seq_arr[0][i + start_byte] for i in range(bytes_count)]))
        for pos in range(1, len(true_pose[i]), 2):
            true_pose[i][pos], true_pose[i][pos - 1] = true_pose[i][pos - 1], true_pose[i][pos]
    return true_pose


def from_bytes_to_int(bytes):
    new_int = 0
    for i in range(len(bytes)):
        new_int = new_int | (bytes[i] << (8 * i))
    return new_int


def decrease_brightness(image_path, brightness_factor):
    pixmap = QPixmap(image_path)
    pixmap = pixmap.scaled(pixmap.size(), Qt.IgnoreAspectRatio)
    image = pixmap.toImage()

    for i in range(image.width()):
        for j in range(image.height()):
            pixel_color = image.pixelColor(i, j)
            new_color = pixel_color.darker(brightness_factor)
            image.setPixelColor(i, j, new_color)

    pixmap = QPixmap.fromImage(image)
    return pixmap


def broadcast_write(adr_channels):
    msg_on = bytearray(b'\x00\x10\x00\x07\x00')
    for i in range(len(adr_channels)):
        msg_on.append(adr_channels[i])
        msg_on.insert(-len(adr_channels), 0) if i == len(adr_channels) - 1 and len(adr_channels) % 2 != 0 else print(0)
    msg_on.insert(5, len(msg_on) - 5)
    msg_on.insert(5, msg_on[5] >> 1)
    return msg_on



