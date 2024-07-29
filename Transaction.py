from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QRadioButton, QLineEdit, \
    QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog
from PySide6.QtGui import QPixmap
import qrcode
from PIL import Image
from io import BytesIO
import csv
from datetime import datetime
import random
import os
import hashlib

class PaymentDialog(QDialog):
    def __init__(self, parent=None):
        super(PaymentDialog, self).__init__(parent)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Payment Options')

        self.layout = QVBoxLayout()

        self.label = QLabel('Choose Payment Method:')
        self.layout.addWidget(self.label)

        self.student_card_radio = QRadioButton('Student Card')
        self.cash_radio = QRadioButton('Cash')
        self.qr_radio = QRadioButton('QR Code')

        self.layout.addWidget(self.student_card_radio)
        self.layout.addWidget(self.cash_radio)
        self.layout.addWidget(self.qr_radio)

        self.amount_label = QLabel('Enter Amount:')
        self.layout.addWidget(self.amount_label)

        self.amount_input = QLineEdit(self)
        self.layout.addWidget(self.amount_input)

        self.pay_button = QPushButton('Pay')
        self.pay_button.clicked.connect(self.process_payment)
        self.layout.addWidget(self.pay_button)

        # QLabel to display the QR code image
        self.qr_label = QLabel(self)
        self.layout.addWidget(self.qr_label)

        # Button to show payment history
        self.show_history_button = QPushButton('Show History')
        self.show_history_button.clicked.connect(self.show_payment_history)
        self.layout.addWidget(self.show_history_button)

        self.setLayout(self.layout)

    def process_payment(self):
        amount = self.amount_input.text()
        if not amount:
            self.show_error_message('Please enter the payment amount.')
            return

        try:
            amount = float(amount)
        except ValueError:
            self.show_error_message('Invalid amount. Please enter a numeric value.')
            return

        if self.student_card_radio.isChecked():
            self.execute_student_card_payment(amount)
        elif self.cash_radio.isChecked():
            self.execute_cash_payment(amount)
        elif self.qr_radio.isChecked():
            self.execute_qr_payment(amount)
        else:
            self.show_error_message('Please select a payment method.')

    def execute_student_card_payment(self, amount):
        if amount > 0:
            bill_id = self.generate_bill_id()
            self.save_transaction('Student Card', amount, bill_id)
            print(f'Student Card Payment of {amount} with Bill ID {bill_id} executed successfully.')
        else:
            self.show_error_message('Invalid amount for student card payment.')

    def execute_cash_payment(self, amount):
        if amount > 0:
            bill_id = self.generate_bill_id()
            self.save_transaction('Cash', amount, bill_id)
            print(f'Cash Payment of {amount} with Bill ID {bill_id} received.')
        else:
            self.show_error_message('Invalid amount for cash payment.')

    def execute_qr_payment(self, amount):
        if amount > 0:
            data = self.generate_qr_data(amount)
            self.generate_qr_data(data)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            img_byte_array = BytesIO()
            img.save(img_byte_array, format='PNG')
            img_byte_array = img_byte_array.getvalue()
            pixmap = QPixmap()
            pixmap.loadFromData(img_byte_array)

            self.qr_label.setPixmap(pixmap)
            self.qr_label.setScaledContents(True)

            bill_id = self.generate_bill_id()
            self.save_transaction('QR Code', amount, bill_id)
            self.export_to_csv()  # Automatically export to CSV after each payment
            print(f'QR Code Payment of {amount} with Bill ID {bill_id} processed successfully.')
        else:
            self.show_error_message('Invalid amount for QR code payment.')

    def generate_qr_data(self, amount):
        # Generate QR code data with a secure hash
        bill_id = self.generate_bill_id()
        secure_hash = hashlib.sha256(f'Payment: Amount: {amount} BillID: {bill_id}'.encode()).hexdigest()
        return f'Payment: Amount: {amount} BillID: {bill_id} Hash: {secure_hash}'

    def generate_bill_id(self):
        return f'{random.randint(100000, 999999)}'

    def save_transaction(self, method, amount, bill_id):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_path = 'transaction_records.csv'

        if not os.path.isfile(file_path):
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Method', 'Amount', 'Bill ID', 'Timestamp'])

        with open(file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([method, amount, bill_id, timestamp])

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle('Error')
        msg_box.setText(message)
        msg_box.exec_()

    def show_payment_history(self):
        # Create a new dialog to display payment history
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle('Payment History')

        # Create a table widget
        table_widget = QTableWidget()
        table_widget.setColumnCount(4)
        table_widget.setHorizontalHeaderLabels(['Method', 'Amount', 'Bill ID', 'Timestamp'])

        # Load data from CSV and populate the table
        file_path = 'transaction_records.csv'
        if os.path.isfile(file_path):
            with open(file_path, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                next(csv_reader)  # Skip header row
                for row in csv_reader:
                    table_widget.insertRow(table_widget.rowCount())
                    for col, value in enumerate(row):
                        item = QTableWidgetItem(value)
                        table_widget.setItem(table_widget.rowCount() - 1, col, item)

        # Create a layout for the history dialog
        history_layout = QVBoxLayout()
        history_layout.addWidget(table_widget)

        # Set the layout for the history dialog
        history_dialog.setLayout(history_layout)

        # Show the history dialog
        history_dialog.exec_()

    def export_to_csv(self):
        # Get the data from the table widget
        data = []
        header = ['Method', 'Amount', 'Bill ID', 'Timestamp']
        data.append(header)
        
        # Append the latest transaction data
        latest_transaction = self.get_latest_transaction()
        data.append(latest_transaction)

        # Save the data to the CSV file
        file_path = 'payment_history.csv'
        with open(file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(data)

    def get_latest_transaction(self):
        # Get the latest transaction data from the original CSV file
        file_path = 'transaction_records.csv'
        if os.path.isfile(file_path):
            with open(file_path, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                rows = list(csv_reader)
                if len(rows) > 1:  # Ensure there is at least one transaction (header row + data)
                    return rows[-1]
        return []

if __name__ == '__main__':
    app = QApplication([])
    dialog = PaymentDialog()
    dialog.show()
    app.exec()
