import sqlite3
import sys
from pathlib import Path

from openpyxl import Workbook
from PyQt5 import QtCore, QtWidgets

DB_FILE = Path("products.db")
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Products (
    productID INTEGER PRIMARY KEY,
    productName TEXT NOT NULL,
    productPrice INTEGER NOT NULL
)
"""


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    return conn


def fetch_products(conn: sqlite3.Connection, search_text: str = "") -> list[tuple]:
    cursor = conn.cursor()
    if search_text:
        like_value = f"%{search_text}%"
        cursor.execute(
            "SELECT productID, productName, productPrice FROM Products "
            "WHERE productName LIKE ? OR CAST(productID AS TEXT) LIKE ? "
            "ORDER BY productID",
            (like_value, like_value),
        )
    else:
        cursor.execute("SELECT productID, productName, productPrice FROM Products ORDER BY productID")
    return cursor.fetchall()


def insert_product(conn: sqlite3.Connection, product_id: int, name: str, price: int) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
        (product_id, name, price),
    )
    conn.commit()


def update_product(conn: sqlite3.Connection, product_id: int, name: str, price: int) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Products SET productName = ?, productPrice = ? WHERE productID = ?",
        (name, price, product_id),
    )
    conn.commit()


def delete_product(conn: sqlite3.Connection, product_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE productID = ?", (product_id,))
    conn.commit()


def export_to_excel(products: list[tuple], output_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Products"
    sheet.append(["productID", "productName", "productPrice"])
    for product_id, name, price in products:
        sheet.append([product_id, name, price])
    workbook.save(output_path)


class ProductManagerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Products 관리자")
        self.setFixedSize(800, 600)

        self.conn = init_db()
        self._create_ui()
        self.load_products()

    def _create_ui(self) -> None:
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        title_label = QtWidgets.QLabel("Products 관리")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        form_layout = QtWidgets.QGridLayout()
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)
        main_layout.addLayout(form_layout)

        self.product_id_edit = QtWidgets.QLineEdit()
        self.product_name_edit = QtWidgets.QLineEdit()
        self.product_price_edit = QtWidgets.QLineEdit()
        self.search_edit = QtWidgets.QLineEdit()

        form_layout.addWidget(QtWidgets.QLabel("제품 ID:"), 0, 0)
        form_layout.addWidget(self.product_id_edit, 0, 1)
        form_layout.addWidget(QtWidgets.QLabel("제품명:"), 0, 2)
        form_layout.addWidget(self.product_name_edit, 0, 3)
        form_layout.addWidget(QtWidgets.QLabel("가격:"), 0, 4)
        form_layout.addWidget(self.product_price_edit, 0, 5)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        main_layout.addLayout(button_layout)

        self.add_button = QtWidgets.QPushButton("입력")
        self.update_button = QtWidgets.QPushButton("수정")
        self.delete_button = QtWidgets.QPushButton("삭제")
        self.reset_button = QtWidgets.QPushButton("리셋")
        self.search_button = QtWidgets.QPushButton("검색")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch(1)
        button_layout.addWidget(QtWidgets.QLabel("검색:"))
        button_layout.addWidget(self.search_edit)
        button_layout.addWidget(self.search_button)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["productID", "productName", "productPrice"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)
        main_layout.addWidget(self.table, stretch=1)

        bottom_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(bottom_layout)

        self.export_button = QtWidgets.QPushButton("엑셀 저장")
        self.status_label = QtWidgets.QLabel("준비 완료")
        bottom_layout.addWidget(self.export_button)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.status_label)

        self.add_button.clicked.connect(self.on_add)
        self.update_button.clicked.connect(self.on_update)
        self.delete_button.clicked.connect(self.on_delete)
        self.reset_button.clicked.connect(self.on_reset)
        self.search_button.clicked.connect(self.on_search)
        self.export_button.clicked.connect(self.on_export_excel)
        self.table.itemSelectionChanged.connect(self.on_table_selection)
        self.table.itemDoubleClicked.connect(self.on_table_double_click)

        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1f272f, stop:1 #28343f);
                color: #e8eef2;
                font-size: 13px;
            }
            #titleLabel {
                font-size: 26px;
                font-weight: bold;
                color: #ffd05b;
                padding: 12px;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit {
                background: #2f3b52;
                border: 1px solid #4a6aa9;
                border-radius: 8px;
                padding: 8px;
                color: #eef1f5;
            }
            QPushButton {
                background-color: #437fef;
                border: none;
                border-radius: 8px;
                color: white;
                padding: 10px 16px;
                min-width: 72px;
            }
            QPushButton:hover {
                background-color: #5d99ff;
            }
            QPushButton:pressed {
                background-color: #2f5dd5;
            }
            QTableWidget {
                background: rgba(36, 49, 71, 0.9);
                alternate-background-color: #232f4a;
                gridline-color: #3d5aa5;
                border: 1px solid #4a6aa9;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #344c7a;
                color: white;
                padding: 10px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #5d99ff;
                color: black;
            }
            QScrollBar:vertical {
                width: 10px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #5d99ff;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
        )

    def load_products(self, search_text: str = "") -> None:
        products = fetch_products(self.conn, search_text)
        self.table.setRowCount(0)

        for product in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(product[0])))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(product[1]))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(product[2])))

        self.status_label.setText(f"총 제품 수: {len(products)}")

    def _get_inputs(self) -> tuple[int, str, int] | None:
        product_id_text = self.product_id_edit.text().strip()
        name = self.product_name_edit.text().strip()
        price_text = self.product_price_edit.text().strip()

        if not product_id_text or not name or not price_text:
            QtWidgets.QMessageBox.warning(self, "입력 오류", "제품 ID, 제품명, 가격을 모두 입력하세요.")
            return None

        try:
            product_id = int(product_id_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "입력 오류", "제품 ID는 정수여야 합니다.")
            return None

        try:
            price = int(price_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "입력 오류", "가격은 정수여야 합니다.")
            return None

        return product_id, name, price

    def on_add(self) -> None:
        values = self._get_inputs()
        if values is None:
            return

        product_id, name, price = values
        try:
            insert_product(self.conn, product_id, name, price)
            self.load_products(self.search_edit.text().strip())
            self.status_label.setText(f"제품 추가 완료: {product_id}")
        except sqlite3.IntegrityError:
            QtWidgets.QMessageBox.critical(self, "오류", f"이미 존재하는 productID입니다: {product_id}")
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "오류", f"제품 추가 중 오류가 발생했습니다:\n{exc}")

    def on_update(self) -> None:
        values = self._get_inputs()
        if values is None:
            return

        product_id, name, price = values
        update_product(self.conn, product_id, name, price)
        self.load_products(self.search_edit.text().strip())
        self.status_label.setText(f"제품 수정 완료: {product_id}")

    def on_delete(self) -> None:
        values = self._get_inputs()
        if values is None:
            return

        product_id, _, _ = values
        answer = QtWidgets.QMessageBox.question(
            self,
            "삭제 확인",
            f"productID {product_id} 제품을 삭제하시겠습니까?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if answer == QtWidgets.QMessageBox.Yes:
            delete_product(self.conn, product_id)
            self.load_products(self.search_edit.text().strip())
            self.status_label.setText(f"제품 삭제 완료: {product_id}")

    def on_search(self) -> None:
        self.load_products(self.search_edit.text().strip())
        self.status_label.setText(f"검색 결과: '{self.search_edit.text().strip()}'")

    def on_reset(self) -> None:
        self.product_id_edit.clear()
        self.product_name_edit.clear()
        self.product_price_edit.clear()
        self.search_edit.clear()
        self.load_products()
        self.status_label.setText("폼과 검색어가 초기화되었습니다.")

    def on_table_selection(self) -> None:
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        self.product_id_edit.setText(selected_items[0].text())
        self.product_name_edit.setText(selected_items[1].text())
        self.product_price_edit.setText(selected_items[2].text())

    def on_table_double_click(self, item: QtWidgets.QTableWidgetItem) -> None:
        row = item.row()
        self.table.selectRow(row)
        self.on_table_selection()
        self.status_label.setText("항목을 상단에 로드했습니다. 수정 또는 삭제 가능합니다.")

    def on_export_excel(self) -> None:
        products = fetch_products(self.conn, self.search_edit.text().strip())
        if not products:
            QtWidgets.QMessageBox.information(self, "엑셀 저장", "저장할 제품 데이터가 없습니다.")
            return

        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "엑셀 파일로 저장",
            "products.xlsx",
            "Excel Files (*.xlsx)",
            options=options,
        )
        if not filename:
            return

        try:
            export_to_excel(products, Path(filename))
            QtWidgets.QMessageBox.information(self, "엑셀 저장", f"엑셀 파일이 저장되었습니다:\n{filename}")
            self.status_label.setText(f"엑셀 저장 완료: {filename}")
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "오류", f"엑셀 저장 중 오류가 발생했습니다:\n{exc}")


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = ProductManagerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
