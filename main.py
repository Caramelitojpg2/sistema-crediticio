import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QStatusBar
)
from PySide6.QtCore import Qt
from database import init_db, get_client_by_dni, get_all_clients, save_query
from pdf_report import generate_pdf

APP_TITLE = "Sistema de Consultas Crediticias - V1"

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar sesión")
        self.setFixedSize(360, 220)
        layout = QVBoxLayout(self)

        title = QLabel("SISTEMA DE CONSULTAS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        self.user = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("Usuario:", self.user)
        form.addRow("Contraseña:", self.password)
        layout.addLayout(form)

        buttons = QDialogButtonBox()
        login_btn = buttons.addButton("Ingresar", QDialogButtonBox.AcceptRole)
        login_btn.clicked.connect(self.login)
        layout.addWidget(buttons)

        hint = QLabel("Demo V1: admin / admin123")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #666;")
        layout.addWidget(hint)

    def login(self):
        if self.user.text() == "admin" and self.password.text() == "admin123":
            self.accept()
        else:
            QMessageBox.warning(self, "Acceso denegado", "Usuario o contraseña incorrectos.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1050, 700)
        self.current_client = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        header = QLabel("SISTEMA DE CONSULTAS CREDITICIAS")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 12px;")
        root.addWidget(header)

        notice = QLabel(
            "MODO DEMOSTRACIÓN: los datos mostrados son ficticios. "
            "No representan información real de Infocorp/Equifax."
        )
        notice.setStyleSheet("background:#fff3cd; padding:10px; color:#664d03;")
        root.addWidget(notice)

        search_row = QHBoxLayout()
        self.dni_input = QLineEdit()
        self.dni_input.setPlaceholderText("Ingrese DNI de 8 dígitos")
        self.dni_input.setMaxLength(8)
        search_btn = QPushButton("🔎 Consultar DNI")
        search_btn.clicked.connect(self.search_client)
        clear_btn = QPushButton("Limpiar")
        clear_btn.clicked.connect(self.clear_form)
        search_row.addWidget(QLabel("DNI:"))
        search_row.addWidget(self.dni_input)
        search_row.addWidget(search_btn)
        search_row.addWidget(clear_btn)
        root.addLayout(search_row)

        self.info_label = QLabel("Ingrese un DNI para consultar.")
        self.info_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        root.addWidget(self.info_label)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Entidad", "Tipo", "Estado", "Monto (S/.)", "Fecha"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)

        actions = QHBoxLayout()
        self.pdf_btn = QPushButton("📄 Generar reporte PDF")
        self.pdf_btn.setEnabled(False)
        self.pdf_btn.clicked.connect(self.create_pdf)
        actions.addWidget(self.pdf_btn)
        root.addLayout(actions)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Listo.")

        self.load_demo_list()

    def load_demo_list(self):
        clients = get_all_clients()
        if clients:
            self.status.showMessage(f"Base de prueba cargada: {len(clients)} clientes.")

    def search_client(self):
        dni = self.dni_input.text().strip()

        if len(dni) != 8 or not dni.isdigit():
            QMessageBox.warning(self, "DNI inválido", "Ingrese un DNI de 8 dígitos.")
            return

        client = get_client_by_dni(dni)
        self.table.setRowCount(0)
        self.current_client = None
        self.pdf_btn.setEnabled(False)

        if not client:
            self.info_label.setText("No se encontró información en la base de demostración.")
            self.status.showMessage(f"Consulta realizada para DNI {dni}.")
            save_query(dni, "SIN_RESULTADO")
            return

        self.current_client = client
        self.info_label.setText(
            f"Cliente: {client['nombres']} {client['apellidos']} | "
            f"DNI: {client['dni']} | Resultado: {client['resultado']}"
        )

        for item in client["obligaciones"]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [
                item["entidad"], item["tipo"], item["estado"],
                f"{item['monto']:.2f}", item["fecha"]
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

        self.pdf_btn.setEnabled(True)
        save_query(dni, client["resultado"])
        self.status.showMessage("Consulta completada.")

    def create_pdf(self):
        if not self.current_client:
            return
        try:
            path = generate_pdf(self.current_client)
            QMessageBox.information(
                self, "Reporte generado",
                f"El PDF fue generado correctamente:\n\n{path}"
            )
            self.status.showMessage("Reporte PDF generado correctamente.")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF:\n{exc}")

    def clear_form(self):
        self.dni_input.clear()
        self.info_label.setText("Ingrese un DNI para consultar.")
        self.table.setRowCount(0)
        self.current_client = None
        self.pdf_btn.setEnabled(False)
        self.status.showMessage("Formulario limpiado.")

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    login = LoginDialog()
    if login.exec() != QDialog.Accepted:
        sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
