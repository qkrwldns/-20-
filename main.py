import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# 사용자 에이전트 설정: 일부 웹사이트가 비브라우저 트래픽을 차단하는 것을 방지하기 위해
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 영화 데이터를 가져오는 함수
def fetch_movie_data():
    # 실시간 영화 순위 페이지 URL
    URL = "https://m.moviechart.co.kr/rank/realtime/index/image"
    # 페이지 요청 및 응답 저장
    page = requests.get(URL, headers=HEADERS)
    # BeautifulSoup 객체 생성하여 HTML 파싱
    soup = BeautifulSoup(page.content, 'html.parser')
    # 영화 목록 아이템을 찾음
    movie_items = soup.find_all('li', class_='movieBox-item')[:20]
    movie_data = []

    # 영화 목록 아이템을 순회하며 필요한 정보 추출
    for index, item in enumerate(movie_items, start=1):
        title = item.find('h3').text.strip()
        rate = item.find('li', class_='ticketing').find('span').text.strip()
        release_date = item.find('li', class_='movie-launch').text.strip().replace('개봉일 ', '')
        img_path = item.find('img')['src'].split('source=')[1]
        full_img_path = f"https:{img_path}" if not img_path.startswith('http') else img_path
        movie_data.append((index, title, rate, release_date, full_img_path))

    return movie_data

# 이미지를 다운로드하는 함수
def download_image(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        return pixmap
    except Exception as e:
        print(f"이미지 다운로드 중 오류 발생: {e}")
    return QPixmap()

# 영화 테이블을 표시하는 클래스
class MovieTable(QTableWidget):
    def __init__(self, data):
        super().__init__()
        self.setRowCount(len(data))
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['순위', '포스터', '제목', '예매율', '개봉일'])
        self.set_data(data)
        self.resizeColumnsToContents()

        # 행 번호(왼쪽에 있는 인덱스 숫자)를 숨깁니다.
        self.verticalHeader().setVisible(False)

    # 테이블 데이터 설정 함수
    def set_data(self, data):
        for row, (index, title, rate, release_date, img_path) in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(str(index)))
            self.setItem(row, 2, QTableWidgetItem(title))
            self.setItem(row, 3, QTableWidgetItem(rate))
            self.setItem(row, 4, QTableWidgetItem(release_date))

            pixmap = download_image(img_path)
            if not pixmap.isNull():
                label = QLabel()
                label.setPixmap(pixmap.scaled(95, 95, Qt.KeepAspectRatio))
                self.setCellWidget(row, 1, label)


def main():
    app = QApplication(sys.argv)
    movie_data = fetch_movie_data()
    table = MovieTable(movie_data)
    layout = QVBoxLayout()
    layout.addWidget(table)

    window = QWidget()
    window.setLayout(layout)
    window.setWindowTitle("실시간 영화 순위")
    window.resize(610, 975)  # 창의 크기를 800x600으로 설정
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
