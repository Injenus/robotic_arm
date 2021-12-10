from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice

delay = 0.01
receive_data_flag = True
# 0-rock, 1-v, 2-phone, 3-spider, 4-ok, 5-thumbs, 6-fuck, 7-initial
action_flag = [False for i in range(8)]  # only for 360's
run_time = 300  # only for 360's
app = QtWidgets.QApplication([])
ui = uic.loadUi('main_window.ui')
ui.setWindowTitle('Robotic Arm Control')
ui.fuck_off.setVisible(False)


class Servo:
    threshold = (0, 180)
    step_coeff = 30
    step_value = 9
    control_values = {180 // step_coeff // 2: 90}
    for i in range(180 // step_coeff // 2):
        control_values[
            i] = 90 - step_value * 180 // step_coeff // 2 + i * step_value
    for i in range(180 // step_coeff // 2 + 1, 180 // step_coeff + 1):
        control_values[i] = 90 + (i - 180 // step_coeff // 2) * step_value

    slider_value = [threshold[0], threshold[1]]

    full_action_flag = True

    time = run_time

    def __init__(self, name, bend, extend, slider, mode_360, mode_180,
                 servo_type=180):
        self.name = name
        if self.name == 'wrist':
            self.num = 10
        elif self.name == 'thumb':
            self.num = 1
        elif self.name == 'index':
            self.num = 2
        elif self.name == 'middle':
            self.num = 3
            self.count = 0
        elif self.name == 'ring':
            self.num = 4
        elif self.name == 'pinky':
            self.num = 5
        else:
            self.num = 99
        self.bend_button = bend
        self.extend_button = extend
        self.slider = slider
        self.slider.setMinimum(self.slider_value[0])
        self.slider.setMaximum(self.slider_value[1])
        self.mode_button_360 = mode_360
        self.mode_button_180 = mode_180
        self.servo_type = servo_type
        self.extend_off()
        if self.servo_type == 180:
            self.mode_button_180.setChecked(True)
        else:
            self.mode_button_360.setChecked(True)
        self.set_mode()

    def extend_off(self):
        self.extend_button.setEnabled(False)

    def extend_on(self):
        self.extend_button.setEnabled(True)

    def bend_off(self):
        self.bend_button.setEnabled(False)

    def bend_on(self):
        self.bend_button.setEnabled(True)

    def slider_off(self):
        self.slider.setEnabled(False)

    def slider_on(self):
        self.slider.setEnabled(True)

    def set_servo_type(self, value):
        self.servo_type = value

    def set_mode(self):
        if self.mode_button_360.isChecked():
            print('set 360 for', self.name)
            self.bend_off()
            self.extend_off()
            self.set_servo_type(360)
            self.slider.setMinimum(0)
            self.slider.setMaximum(180 // self.step_coeff)
            self.slider.setValue(180 // self.step_coeff // 2)
        else:
            print('set 180 for', self.name)
            self.bend_on()
            self.extend_on()
            self.set_servo_type(180)
            self.slider.setMinimum(self.slider_value[0])
            self.slider.setMaximum(self.slider_value[1])
            self.slider.setValue(self.slider_value[0])

    def bending(self):
        transmit_data([self.num, self.slider_value[1]])
        self.slider.setValue(self.slider_value[1])
        if self.name == 'middle':
            self.count += 1
            if self.count == 3:
                ui.fuck_off.setVisible(True)
                self.count = 0

    def extending(self):
        transmit_data([self.num, self.slider_value[0]])
        self.slider.setValue(self.slider_value[0])

    def sliding(self):
        if self.servo_type == 180:
            transmit_data([self.num, self.slider.value()])
        elif self.servo_type == 360:
            transmit_data(
                [self.num, self.control_values[self.slider.value()]])

    def neutraling(self):
        transmit_data([self.num, 90])

    def slider_start(self):
        self.slider.setValue(180 // self.step_coeff // 2)


wrist = Servo('wrist', ui.wrist_downwards, ui.wrist_upwards, ui.wrist_slider,
              ui.wrist_360, ui.wrist_180, 360)
thumb = Servo('thumb', ui.thumb_bend, ui.thumb_extend, ui.thumb_slider,
              ui.thumb_360, ui.thumb_180)
index = Servo('index', ui.index_bend, ui.index_extend, ui.index_slider,
              ui.index_360, ui.index_180, 360)
middle = Servo('middle', ui.middle_bend, ui.middle_extend, ui.middle_slider,
               ui.middle_360, ui.middle_180, 360)
ring = Servo('ring', ui.ring_bend, ui.ring_extend, ui.ring_slider, ui.ring_360,
             ui.ring_180, 360)
pinky = Servo('pinky', ui.pinky_bend, ui.pinky_extend, ui.pinky_slider,
              ui.pinky_360, ui.pinky_180)


def refresh_serial_list():
    ui.serial_combobox.clear()
    port_list = []
    ports = QSerialPortInfo().availablePorts()
    for port in ports:
        port_list.append((port.portName()))
    ui.serial_combobox.addItems(port_list)


def open_port():
    serial.setPortName(ui.serial_combobox.currentText())
    serial.open(QIODevice.ReadWrite)
    transmit_data([7, 1])


def close_port():
    serial.close()
    ui.output_text.setText('The COM-port was closed.')


def receive_data():
    global receive_data_flag
    receive_data_flag = True
    rx = serial.readLine()
    rxs = str(rx, 'utf-8').strip()
    print('Arduino says:', rxs)
    if rxs == 'READY (setup)' or rxs == 'Init Led':
        ui.output_text.setText('The COM-port is open. All ready to work!')


def transmit_data(data):
    global receive_data_flag
    if receive_data_flag or data == [7, 1]:
        txs = ''
        for val in data:
            txs += str(val) + ','
        txs = txs[:-1]
        serial.write(txs.encode())
        print(txs)
        receive_data_flag = False


def disabled_actions():
    ui.rock_sign.setEnabled(False)
    ui.v_sign.setEnabled(False)
    ui.phone_call.setEnabled(False)
    ui.spider_man.setEnabled(False)
    ui.ok.setEnabled(False)
    ui.thumbs_up.setEnabled(False)
    ui.fuck_off.setEnabled(False)


def enabled_actions():
    ui.rock_sign.setEnabled(True)
    ui.v_sign.setEnabled(True)
    ui.phone_call.setEnabled(True)
    ui.spider_man.setEnabled(True)
    ui.ok.setEnabled(True)
    ui.thumbs_up.setEnabled(True)
    ui.fuck_off.setEnabled(True)


def rock_sign(direc):
    index_slider_value = 1
    middle.time = 320
    ring.time = 300
    if direc == 0:
        index_slider_value = 0
        middle.time = 235
        ring.time = 180
    action_flag[7] = False
    if thumb.servo_type == middle.servo_type == ring.servo_type == 180:
        data = [11, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type,
                middle.servo_type, ring.servo_type, pinky.servo_type,
                thumb.slider_value[1], index.slider_value[0],
                middle.slider_value[1], ring.slider_value[1],
                pinky.slider_value[0]]
        thumb.slider.setValue(thumb.slider_value[1])
        index.slider.setValue(index.slider_value[0])
        middle.slider.setValue(ring.slider_value[1])
        ring.slider.setValue(ring.slider_value[1])
        pinky.slider.setValue(pinky.slider_value[0])
    else:
        data = [11, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type, middle.servo_type,
                ring.servo_type, pinky.servo_type,
                thumb.slider_value[index_slider_value], 90, middle.time,
                ring.time, pinky.slider_value[0], direc, 90, direc, direc, 90]
        action_flag[0] = True
        disabled_actions()
    transmit_data(data)


def v_sign(direc):
    action_flag[7] = False
    index_slider_value = 1
    ring.time = 300
    if direc == 0:
        index_slider_value = 0
        ring.time = 140
    if thumb.servo_type == ring.servo_type == pinky.servo_type == 180:
        data = [12, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type,
                middle.servo_type, ring.servo_type, pinky.servo_type,
                thumb.slider_value[1], index.slider_value[0],
                middle.slider_value[0], ring.slider_value[1],
                pinky.slider_value[1]]
        thumb.slider.setValue(thumb.slider_value[1])
        index.slider.setValue(index.slider_value[0])
        middle.slider.setValue(ring.slider_value[0])
        ring.slider.setValue(ring.slider_value[1])
        pinky.slider.setValue(pinky.slider_value[1])
    else:
        data = [12, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type, middle.servo_type,
                ring.servo_type, pinky.servo_type,
                thumb.slider_value[index_slider_value], 90, 90, ring.time,
                pinky.slider_value[index_slider_value], 90, 90, 90, direc, 90]
        action_flag[1] = True
        disabled_actions()
    transmit_data(data)


def phone_call(direc):
    action_flag[7] = False
    index.time = 300
    middle.time = 350
    ring.time = 300
    if direc == 0:
        index.time = 220
        middle.time = 290
        ring.time = 220
    if index.servo_type == middle.servo_type == ring.servo_type == 180:
        data = [13, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type,
                middle.servo_type, ring.servo_type, pinky.servo_type,
                thumb.slider_value[0], index.slider_value[1],
                middle.slider_value[1], ring.slider_value[1],
                pinky.slider_value[0]]
        thumb.slider.setValue(thumb.slider_value[0])
        index.slider.setValue(index.slider_value[1])
        middle.slider.setValue(ring.slider_value[1])
        ring.slider.setValue(ring.slider_value[1])
        pinky.slider.setValue(pinky.slider_value[0])
    else:
        data = [13, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type, middle.servo_type,
                ring.servo_type, pinky.servo_type, 90, index.time, middle.time,
                ring.time, 90, 90, direc, direc, direc, 90]
        action_flag[2] = True
        disabled_actions()
    transmit_data(data)


def spider_man(direc):
    action_flag[7] = False
    middle.time = 300
    ring.time = 300
    if direc == 0:
        middle.time = 250
        ring.time = 170
    if middle.servo_type == ring.servo_type == 180:
        data = [14, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type,
                middle.servo_type, ring.servo_type, pinky.servo_type,
                thumb.slider_value[0], index.slider_value[0],
                middle.slider_value[1], ring.slider_value[1],
                pinky.slider_value[0]]
        thumb.slider.setValue(thumb.slider_value[0])
        index.slider.setValue(index.slider_value[0])
        middle.slider.setValue(ring.slider_value[1])
        ring.slider.setValue(ring.slider_value[1])
        pinky.slider.setValue(pinky.slider_value[0])
    else:
        data = [14, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type, middle.servo_type,
                ring.servo_type, pinky.servo_type, 90, 90, middle.time,
                ring.time, 90, 90, 90, direc, direc, 90]
        action_flag[3] = True
        disabled_actions()
    transmit_data(data)


def ok(direc):
    action_flag[7] = False
    index_slider_value = 1
    index.time = 180
    if direc == 0:
        index_slider_value = 0
        index.time = 120
    if thumb.servo_type == index.servo_type == 180:
        data = [15, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type,
                middle.servo_type, ring.servo_type, pinky.servo_type,
                thumb.slider_value[1] // 1.3, index.slider_value[1],
                middle.slider_value[0], ring.slider_value[0],
                pinky.slider_value[0]]
        thumb.slider.setValue(thumb.slider_value[1])
        index.slider.setValue(index.slider_value[1])
        middle.slider.setValue(ring.slider_value[0])
        ring.slider.setValue(ring.slider_value[0])
        pinky.slider.setValue(pinky.slider_value[0])
    else:
        data = [15, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type, middle.servo_type,
                ring.servo_type, pinky.servo_type,
                thumb.slider_value[index_slider_value] // 1.3, index.time, 90,
                90, 90, 90, direc, 90, 90, 90]
        action_flag[4] = True
        disabled_actions()
    transmit_data(data)


def thumbs_up(direc):
    action_flag[7] = False
    index_slider_value = 1
    index.time = 380
    middle.time = 420
    ring.time = 370
    if direc == 0:
        index_slider_value = 0
        index.time = 260
        middle.time = 320
        ring.time = 240
    if index.servo_type == middle.servo_type == ring.servo_type == pinky.servo_type == 180:
        data = [16, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type,
                middle.servo_type, ring.servo_type, pinky.servo_type,
                thumb.slider_value[0], index.slider_value[1],
                middle.slider_value[1], ring.slider_value[1],
                pinky.slider_value[1]]
        thumb.slider.setValue(thumb.slider_value[0])
        index.slider.setValue(index.slider_value[1])
        middle.slider.setValue(ring.slider_value[1])
        ring.slider.setValue(ring.slider_value[1])
        pinky.slider.setValue(pinky.slider_value[1])
    else:
        data = [16, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type, middle.servo_type,
                ring.servo_type, pinky.servo_type, 90, index.time, middle.time,
                ring.time, pinky.slider_value[index_slider_value], 90, direc,
                direc, direc, 90]
        action_flag[5] = True
        disabled_actions()
    transmit_data(data)


def fuck_off(direc):
    action_flag[7] = False
    ui.fuck_off.setVisible(False)
    index_slider_value = 1
    index.time = 330
    ring.time = 300
    if direc == 0:
        index_slider_value = 0
        index.time = 230
        ring.time = 210
    if thumb.servo_type == index.servo_type == ring.servo_type == pinky.servo_type == 180:
        data = [17, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type,
                middle.servo_type, ring.servo_type, pinky.servo_type,
                thumb.slider_value[1] // 1.23, index.slider_value[1],
                middle.slider_value[0], ring.slider_value[1],
                pinky.slider_value[1]]
        thumb.slider.setValue(thumb.slider_value[1])
        index.slider.setValue(index.slider_value[1])
        middle.slider.setValue(ring.slider_value[0])
        ring.slider.setValue(ring.slider_value[1])
        pinky.slider.setValue(pinky.slider_value[1])
    else:
        data = [17, thumb.num, index.num, middle.num, ring.num, pinky.num,
                thumb.servo_type, index.servo_type, middle.servo_type,
                ring.servo_type, pinky.servo_type,
                thumb.slider_value[index_slider_value] // 1.23, index.time, 90,
                ring.time, pinky.slider_value[index_slider_value], 90, direc,
                90, direc, direc, 90]
        action_flag[6] = True
        disabled_actions()
    transmit_data(data)


def initial_position():
    if thumb.servo_type == index.servo_type == middle.servo_type == ring.servo_type == pinky.servo_type == 180:
        data_init = [18, thumb.num, index.num, middle.num, ring.num, pinky.num,
                     thumb.servo_type, index.servo_type,
                     middle.servo_type, ring.servo_type, pinky.servo_type,
                     thumb.slider_value[0], index.slider_value[0],
                     middle.slider_value[0], ring.slider_value[0],
                     pinky.slider_value[0]]
        thumb.slider.setValue(thumb.slider_value[0])
        index.slider.setValue(index.slider_value[0])
        middle.slider.setValue(ring.slider_value[0])
        ring.slider.setValue(ring.slider_value[0])
        pinky.slider.setValue(pinky.slider_value[0])
        transmit_data(data_init)
    else:
        if action_flag[0]:
            rock_sign(0)
            action_flag[0] = False
        elif action_flag[1]:
            v_sign(0)
            action_flag[1] = False
        elif action_flag[2]:
            phone_call(0)
            action_flag[2] = False
        elif action_flag[3]:
            spider_man(0)
            action_flag[3] = False
        elif action_flag[4]:
            ok(0)
            action_flag[4] = False
        elif action_flag[5]:
            thumbs_up(0)
            action_flag[5] = False
        elif action_flag[6]:
            fuck_off(0)
            action_flag[6] = False
        action_flag[7] = True
        enabled_actions()


# def wrist_rotation():
#     if wrist.slider.value() == 180 // wrist.step_coeff // 2:
#         thumb.slider.setMaximum(thumb.slider_value[1])
#         index.slider.setMaximum(index.slider_value[1])
#         middle.slider.setMaximum(middle.slider_value[1])
#         ring.slider.setMaximum(ring.slider_value[1])
#         pinky.slider.setMaximum(pinky.slider_value[1])
#     else:
#         initial_position()
#         thumb.slider.setMaximum(thumb.slider_value[1] // 2)
#         index.slider.setMaximum(index.slider_value[1] // 2)
#         middle.slider.setMaximum(middle.slider_value[1] // 2)
#         ring.slider.setMaximum(ring.slider_value[1] // 2)
#         pinky.slider.setMaximum(pinky.slider_value[1] // 2)

ui.output_text.setText('The COM-port is closed. Please, open one.')
#
wrist.mode_button_360.toggled.connect(wrist.set_mode)
thumb.mode_button_360.toggled.connect(thumb.set_mode)
index.mode_button_360.toggled.connect(index.set_mode)
middle.mode_button_360.toggled.connect(middle.set_mode)
ring.mode_button_360.toggled.connect(ring.set_mode)
pinky.mode_button_360.toggled.connect(pinky.set_mode)
#
serial = QSerialPort()
serial.setBaudRate(115200)
refresh_serial_list()
ui.refresh_serial.clicked.connect(refresh_serial_list)
#
ui.open_serial.clicked.connect(open_port)
ui.close_serial.clicked.connect(close_port)
#
serial.readyRead.connect(receive_data)

#
wrist.bend_button.clicked.connect(wrist.bending)
thumb.bend_button.clicked.connect(thumb.bending)
index.bend_button.clicked.connect(index.bending)
middle.bend_button.clicked.connect(middle.bending)
ring.bend_button.clicked.connect(ring.bending)
pinky.bend_button.clicked.connect(pinky.bending)
#
wrist.extend_button.clicked.connect(wrist.extending)
thumb.extend_button.clicked.connect(thumb.extending)
index.extend_button.clicked.connect(index.extending)
middle.extend_button.clicked.connect(middle.extending)
ring.extend_button.clicked.connect(ring.extending)
pinky.extend_button.clicked.connect(pinky.extending)
#
wrist.slider.valueChanged.connect(wrist.sliding)
thumb.slider.valueChanged.connect(thumb.sliding)
index.slider.valueChanged.connect(index.sliding)
middle.slider.valueChanged.connect(middle.sliding)
ring.slider.valueChanged.connect(ring.sliding)
pinky.slider.valueChanged.connect(pinky.sliding)
#
ui.rock_sign.clicked.connect(lambda: rock_sign(180))
ui.v_sign.clicked.connect(lambda: v_sign(180))
ui.phone_call.clicked.connect(lambda: phone_call(180))
ui.spider_man.clicked.connect(lambda: spider_man(180))
ui.ok.clicked.connect(lambda: ok(180))
ui.thumbs_up.clicked.connect(lambda: thumbs_up(180))
ui.fuck_off.clicked.connect(lambda: fuck_off(180))
ui.initial_position.clicked.connect(initial_position)
#
if wrist.servo_type == 360:
    wrist.slider.sliderReleased.connect(wrist.slider_start)
if thumb.servo_type == 360:
    thumb.slider.sliderReleased.connect(thumb.slider_start)
if index.servo_type == 360:
    index.slider.sliderReleased.connect(index.slider_start)
if middle.servo_type == 360:
    middle.slider.sliderReleased.connect(middle.slider_start)
if ring.servo_type == 360:
    ring.slider.sliderReleased.connect(ring.slider_start)
if pinky.servo_type == 360:
    pinky.slider.sliderReleased.connect(pinky.slider_start)
#
# wrist.slider.valueChanged.connect(wrist_rotation)
#
ui.show()
app.exec()
