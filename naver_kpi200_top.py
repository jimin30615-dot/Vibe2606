import re
import sys
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QHBoxLayout

BASE_URL = "https://finance.naver.com"
ENTRY_URL = f"{BASE_URL}/sise/entryJongmok.naver"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_kpi200_top(page=1):
    params = {"type": "KPI200", "page": page}
    res = requests.get(ENTRY_URL, headers=HEADERS, params=params)
    res.encoding = "euc-kr"
    soup = BeautifulSoup(res.text, "html.parser")

    table = None
    for candidate in soup.find_all("table", class_="type_1"):
        th = candidate.find("th", string=lambda s: s and "종목별" in s)
        if th:
            table = candidate
            break

    if table is None:
        raise RuntimeError("KPI200 편입종목 상위 테이블을 찾을 수 없습니다.")

    results = []
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) != 7:
            continue

        name_tag = cols[0].find("a")
        name = name_tag.get_text(strip=True) if name_tag else cols[0].get_text(strip=True)
        code = None
        if name_tag and name_tag.has_attr("href"):
            match = re.search(r"code=(\d+)", name_tag["href"])
            if match:
                code = match.group(1)

        results.append({
            "종목명": name,
            "종목코드": code,
            "현재가": cols[1].get_text(strip=True),
            "전일비": cols[2].get_text(strip=True),
            "등락률": cols[3].get_text(strip=True),
            "거래량": cols[4].get_text(strip=True),
            "거래대금(백만)": cols[5].get_text(strip=True),
            "시가총액(억)": cols[6].get_text(strip=True),
        })

    return results


def get_last_page(soup):
    nav = soup.find("table", class_="Nnavi")
    if nav is None:
        return 1

    pages = []
    for a in nav.find_all("a", href=True):
        match = re.search(r"page=(\d+)", a["href"])
        if match:
            pages.append(int(match.group(1)))

    return max(pages) if pages else 1


def fetch_all_kpi200_top():
    params = {"type": "KPI200", "page": 1}
    res = requests.get(ENTRY_URL, headers=HEADERS, params=params)
    res.encoding = "euc-kr"
    soup = BeautifulSoup(res.text, "html.parser")
    last_page = get_last_page(soup)

    results = []
    for page in range(1, last_page + 1):
        results.extend(fetch_kpi200_top(page=page))
    return results


class KPI200Window(QMainWindow):
    def __init__(self, entries):
        super().__init__()
        self.setWindowTitle("KPI200 편입종목 상위")
        self.setGeometry(100, 100, 1000, 600)
        self.entries = entries

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "종목명",
            "종목코드",
            "현재가",
            "전일비",
            "등락률",
            "거래량",
            "거래대금(백만)",
            "시가총액(억)",
        ])

        self.load_entries(entries)

        button_layout = QHBoxLayout()
        save_button = QPushButton("엑셀로 저장")
        save_button.clicked.connect(self.save_to_excel)
        button_layout.addWidget(save_button)
        button_layout.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("KPI200 편입종목 상위 전체 목록"))
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_entries(self, entries):
        self.table.setRowCount(len(entries))
        for row_index, entry in enumerate(entries):
            self.table.setItem(row_index, 0, QTableWidgetItem(entry["종목명"]))
            self.table.setItem(row_index, 1, QTableWidgetItem(entry["종목코드"] or ""))
            self.table.setItem(row_index, 2, QTableWidgetItem(entry["현재가"]))
            self.table.setItem(row_index, 3, QTableWidgetItem(entry["전일비"]))
            self.table.setItem(row_index, 4, QTableWidgetItem(entry["등락률"]))
            self.table.setItem(row_index, 5, QTableWidgetItem(entry["거래량"]))
            self.table.setItem(row_index, 6, QTableWidgetItem(entry["거래대금(백만)"]))
            self.table.setItem(row_index, 7, QTableWidgetItem(entry["시가총액(억)"]))
        self.table.resizeColumnsToContents()

    def save_to_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "엑셀로 저장", "kpi200.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "KPI200 편입종목"

        headers = [
            "종목명",
            "종목코드",
            "현재가",
            "전일비",
            "등락률",
            "거래량",
            "거래대금(백만)",
            "시가총액(억)",
        ]
        sheet.append(headers)

        for entry in self.entries:
            sheet.append([
                entry["종목명"],
                entry["종목코드"] or "",
                entry["현재가"],
                entry["전일비"],
                entry["등락률"],
                entry["거래량"],
                entry["거래대금(백만)"],
                entry["시가총액(억)"],
            ])

        workbook.save(path)


def main():
    entries = fetch_all_kpi200_top()
    app = QApplication(sys.argv)
    window = KPI200Window(entries)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
