import customtkinter as ctk
from gui.view_tree_data import ModernCTkTable
import threading
import whatsapp_automation
import time

class SenderTapWindow(ctk.CTkFrame):
    def __init__(self, master, messages_tab, channels_tab, **kwargs):
        super().__init__(master, **kwargs)
        
        self.messages_tab = messages_tab
        self.channels_tab = channels_tab

        # ✅ بيانات حية
        self.selected_numbers = []
        self.messages = []

        # ✅ ربط إشعارات التغيير
        self.channels_tab.on_selection_changed = self.update_selected_numbers
        self.messages_tab.on_messages_changed = self.update_messages

        self.columnconfigure((0, 1, 2, 3), weight=1)
        self.rowconfigure((0), weight=1)
        self.rowconfigure((1), weight=2)
        self.rowconfigure((2), weight=1)
        
        self.count_numbers_sent_it = ctk.CTkLabel(self, text="Sent: ", font=('arial', 20, 'bold'))
        self.count_numbers_sent_it.grid(row=0, column=0 , columnspan=2)
        self.count_numbers_no_phone = ctk.CTkLabel(self, text="No Phone: ", font=('arial', 20, 'bold'))
        self.count_numbers_no_phone.grid(row=0, column=2 , columnspan=2)

        header = ["Send To", "Send From"]
        self.data_numbers = []
        # Pass the backing list to the table so it shows existing rows (empty at start)
        self.view_tree_results = ModernCTkTable(self, headers=header, data=self.data_numbers, checked_column=False)
        self.view_tree_results.grid(row=1, column=0, columnspan=4, sticky='nsew')
        
        self.run_btn = ctk.CTkButton(self, text="Run Sending 🚀", command=self.start_sending, fg_color='green', font=('arial', 12, 'bold'))
        self.run_btn.grid(row=2, column=0)
        self.stop_btn = ctk.CTkButton(self, text="Stop Sending ⛔", command=self.stopping_sending, font=('arial', 12, 'bold'))
        self.stop_btn.grid(row=2, column=1)
        self.import_numbers_btn = ctk.CTkButton(self, text="Import Numbers", command=self.import_numbers_fun, font=('arial', 12, 'bold'))
        self.import_numbers_btn.grid(row=2, column=2)
        self.clear_numbers = ctk.CTkButton(self, text="Clear Numbers", command=self.clear_numers_fun, font=('arial', 12, 'bold'))
        self.clear_numbers.grid(row=2, column=3)

    # 🔄 تحديث البيانات تلقائيًا
    def update_selected_numbers(self, numbers):
        self.selected_numbers = numbers
        print("📱 Selected Numbers Updated:", numbers)

    def update_messages(self, messages):
        self.messages = messages
        print("💬 Messages Updated:", messages)

    # 🚀 بدء الإرسال
    def start_sending(self):
        if not self.selected_numbers or not self.messages or not self.data_numbers:
            print("⚠️ تأكد من اختيار أرقام، رسائل، وقنوات الإرسال قبل الإرسال.")
            return

        # 🔹 تعريف callback لتحديث الجدول
        def update_gui(number, channel):
            row_index = self.view_tree_results.get_row_index_by_value(number)
            if row_index >= 0:
                self.view_tree_results.update_cell_value(row_index, 1, channel)  # عمود Send From

        import whatsapp_automation

        # If channels were already opened via channel_tab.open_only(),
        # then run() already created `current_parent_event`. In that case
        # simply signal it to start sending and don't start run() again.
        existing_evt = getattr(whatsapp_automation, 'current_parent_event', None)
        if existing_evt is not None:
            try:
                try:
                    print(f'🔧 GUI setting existing_evt id={id(existing_evt)}')
                except Exception:
                    pass
                existing_evt.set()
                # also set namespace fallback if available
                try:
                    ns = getattr(whatsapp_automation, 'current_parent_namespace', None)
                    if ns is not None:
                        try:
                            ns.started = True
                            print('🔧 GUI also set current_parent_namespace.started = True')
                        except Exception:
                            pass
                except Exception:
                    pass
                # also push a START into control queue if present
                try:
                    ctrl = getattr(whatsapp_automation, 'current_parent_control_queue', None)
                    if ctrl is not None:
                        try:
                            ctrl.put('START')
                            print('🔧 GUI pushed START into current_parent_control_queue')
                        except Exception:
                            pass
                except Exception:
                    pass
                print('✅ Found existing parent_event — signaled start.')
                return
            except Exception as e:
                print(f'⚠️ Failed to set existing parent_event: {e}')

        # Otherwise start the run() in a background thread (it will create parent_event)
        def _on_ready(evt):
            try:
                print(f'🔔 on_ready callback received evt id={id(evt)}; setting it to start sending')
                evt.set()
                # also set namespace fallback if available
                try:
                    ns = getattr(whatsapp_automation, 'current_parent_namespace', None)
                    if ns is not None:
                        try:
                            ns.started = True
                            print('🔔 on_ready also set current_parent_namespace.started = True')
                        except Exception:
                            pass
                except Exception:
                    pass
                # also push START into control queue
                try:
                    ctrl = getattr(whatsapp_automation, 'current_parent_control_queue', None)
                    if ctrl is not None:
                        try:
                            ctrl.put('START')
                            print('🔔 on_ready pushed START into current_parent_control_queue')
                        except Exception:
                            pass
                except Exception:
                    pass
            except Exception as e:
                print(f'⚠️ on_ready callback failed to set evt: {e}')

        threading.Thread(
            target=whatsapp_automation.run,
            args=(self.selected_numbers, self.messages, self.data_numbers, False, update_gui),
            kwargs={'on_ready': _on_ready},
            daemon=True
        ).start()
        # no watcher required when on_ready is provided and used by run()
    def stopping_sending(self):
        print("⛔ Stopping sending...")
        try:
            whatsapp_automation.stop_sending()
        except Exception as e:
            print(f"⚠️ خطأ أثناء محاولة إيقاف الإرسال: {e}")

    def force_start(self):
        pass

    def clear_numers_fun(self):
        self.data_numbers.clear()
        self.view_tree_results.clear()


    def import_numbers_fun(self):
        # Ask for a filename (tk filedialog does not accept an 'encoding' option)
        filepath = ctk.filedialog.askopenfilename()
        if not filepath:
            return

        new_rows = []
        try:
            with open(filepath, mode='r', encoding='utf-8') as file_obj:
                for line in file_obj:
                    n = line.strip()
                    if not n:
                        continue
                    row = [n]
                    self.data_numbers.append(row)
                    new_rows.append(row)
        except Exception as e:
            print(f"⚠️ خطأ أثناء قراءة الملف: {e}")
            return


        if new_rows:
            self.view_tree_results.add_data(new_rows)
        
