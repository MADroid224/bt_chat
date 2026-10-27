import os
import threading
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

class BluetoothTerminalWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        self.conn_sock = None
        self.stream_in = None
        self.stream_out = None
        
        # 1. Configuration Banner
        self.config_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=5)
        self.mac_input = TextInput(text='', placeholder_text='Target MAC Address (Client mode)', multiline=False)
        self.connect_btn = Button(text='Connect', size_hint_x=0.3)
        self.connect_btn.bind(on_press=self.start_connection)
        self.config_layout.add_widget(self.mac_input)
        self.config_layout.add_widget(self.connect_btn)
        self.add_widget(self.config_layout)
        
        # 2. Virtual Terminal Log Display
        self.scroll = ScrollView(size_hint_y=0.8)
        self.terminal_log = Label(text='[System] Console initialized. Ready for action.\n', 
                                  halign='left', valign='top', size_hint_y=None)
        self.terminal_log.bind(size=self.terminal_log.setter('text_size'))
        self.scroll.add_widget(self.terminal_log)
        self.add_widget(self.scroll)
        
        # 3. Input Text Panel
        self.msg_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=5)
        self.msg_input = TextInput(placeholder_text='Type your message...', multiline=False, disabled=True)
        self.send_btn = Button(text='Send', size_hint_x=0.2, disabled=True)
        self.send_btn.bind(on_press=self.send_data)
        self.msg_layout.add_widget(self.msg_input)
        self.msg_layout.add_widget(self.send_btn)
        self.add_widget(self.msg_layout)

    def log(self, text):
        def update_ui(dt):
            self.terminal_log.text += f"{text}\n"
            self.terminal_log.height = self.terminal_log.texture_size + 20
        Clock.schedule_once(update_ui)

    def start_connection(self, instance):
        target_mac = self.mac_input.text.strip()
        if not target_mac:
            self.log("[Error] Target MAC Address field cannot be empty.")
            return
        
        self.connect_btn.disabled = True
        self.mac_input.disabled = True
        self.log(f"[System] Initiating Bluetooth connection payload to {target_mac}...")
        threading.Thread(target=self.connect_worker, args=(target_mac,), daemon=True).start()

    def connect_worker(self, mac):
        if platform == 'android':
            try:
                from jnius import autoclass
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                UUID = autoclass('java.util.UUID')
                
                adapter = BluetoothAdapter.getDefaultAdapter()
                device = adapter.getRemoteDevice(mac)
                
                # Standard Serial Port Profile (SPP) UUID
                spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
                self.conn_sock = device.createRfcommSocketToServiceRecord(spp_uuid)
                self.conn_sock.connect()
                
                self.stream_in = self.conn_sock.getInputStream()
                self.stream_out = self.conn_sock.getOutputStream()
                
                self.log("[System] Android Bluetooth RFCOMM linked successfully!")
                self.enable_controls()
                self.listen_loop_android()
            except Exception as e:
                self.log(f"[Error] Connection aborted: {str(e)}")
        else:
            # Desktop Fallback Architecture (Linux)
            import socket
            try:
                self.conn_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                self.conn_sock.connect((mac, 1))
                self.log("[System] Linux Desktop RFCOMM Channel connected.")
                self.enable_controls()
                self.listen_loop_desktop()
            except Exception as e:
                self.log(f"[Error] Desktop Connection Failure: {str(e)}")

    def enable_controls(self):
        def unlock(dt):
            self.msg_input.disabled = False
            self.send_btn.disabled = False
        Clock.schedule_once(unlock)

    def listen_loop_android(self):
        # Native Android Byte-Reader loop
        from jnius import jarray, c_byte
        buffer = jarray(c_byte)(1024)
        while True:
            try:
                bytes_read = self.stream_in.read(buffer)
                if bytes_read > 0:
                    msg = bytes([buffer[i] for i in range(bytes_read)]).decode('utf-8')
                    self.log(f"Peer: {msg.strip()}")
            except Exception:
                self.log("[System] Connection dropped by remote hardware device.")
                break

    def listen_loop_desktop(self):
        # Python standard desktop reader loop
        while True:
            try:
                data = self.conn_sock.recv(1024)
                if not data:
                    break
                self.log(f"Peer: {data.decode('utf-8').strip()}")
            except Exception:
                break
        self.log("[System] Connection terminated.")

    def send_data(self, instance):
        text = self.msg_input.text.strip()
        if text:
            try:
                if platform == 'android':
                    self.stream_out.write(bytes(text + '\n', 'utf-8'))
                else:
                    self.conn_sock.send(text.encode('utf-8'))
                self.log(f"Me: {text}")
                self.msg_input.text = ''
            except Exception as e:
                self.log(f"[Error] Broadcast failed: {e}")

class BluetoothChatApp(App):
    def build(self):
        return BluetoothTerminalWidget()

if __name__ == '__main__':
    BluetoothChatApp().run()
