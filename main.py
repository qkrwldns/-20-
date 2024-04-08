import sys  # 시스템 관련 모듈을 임포트합니다.
import requests  # 웹페이지 요청을 보내는 모듈을 임포트합니다.
from bs4 import BeautifulSoup  # HTML 파싱을 위한 모듈을 임포트합니다.
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QLabel, QVBoxLayout, QWidget  # PyQt5의 위젯 및 레이아웃을 임포트합니다.
from PyQt5.QtGui import QPixmap  # 이미지를 표시하기 위한 모듈을 임포트합니다.
from PyQt5.QtCore import Qt  # PyQt5의 핵심 모듈을 임포트합니다.

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
    movie_items = soup.find_all('li', class_='movieBox-item')[:20]  # 상위 20개 영화 정보만 가져옵니다.
    movie_data = []

    # 영화 목록 아이템을 순회하며 필요한 정보 추출
    for index, item in enumerate(movie_items, start=1):  # 영화 순위를 1부터 시작합니다.
        title = item.find('h3').text.strip()  # 영화 제목을 추출합니다.
        rate = item.find('li', class_='ticketing').find('span').text.strip()  # 예매율을 추출합니다.
        release_date = item.find('li', class_='movie-launch').text.strip().replace('개봉일 ', '')  # 개봉일을 추출합니다.
        img_path = item.find('img')['src'].split('source=')[1]  # 이미지 경로를 추출합니다.
        full_img_path = f"https:{img_path}" if not img_path.startswith('http') else img_path  # 완전한 이미지 경로를 생성합니다.
        movie_data.append((index, title, rate, release_date, full_img_path))  # 영화 데이터를 리스트에 추가합니다.

    return movie_data  # 영화 데이터를 반환합니다.


# 이미지를 다운로드하는 함수
def download_image(url):
    try:
        response = requests.get(url, headers=HEADERS)  # 이미지 다운로드를 위해 요청을 보냅니다.
        response.raise_for_status()  # 요청이 성공적으로 이루어졌는지 확인합니다.
        pixmap = QPixmap()  # QPixmap 객체를 생성합니다.
        pixmap.loadFromData(response.content)  # 이미지 데이터를 QPixmap에 로드합니다.
        return pixmap  # QPixmap 객체를 반환합니다.
    except Exception as e:
        print(f"이미지 다운로드 중 오류 발생: {e}")  # 오류 메시지를 출력합니다.
    return QPixmap()  # 빈 QPixmap 객체를 반환합니다.


# 영화 테이블을 표시하는 클래스
class MovieTable(QTableWidget):
    def __init__(self, data):
        super().__init__()
        self.setRowCount(len(data))  # 테이블의 행 수를 데이터 길이로 설정합니다.
        self.setColumnCount(5)  # 테이블의 열 수를 5로 설정합니다.
        self.setHorizontalHeaderLabels(['순위', '포스터', '제목', '예매율', '개봉일'])  # 가로 헤더 레이블을 설정합니다.
        self.set_data(data)  # 데이터를 테이블에 설정합니다.
        self.resizeColumnsToContents()  # 열의 크기를 콘텐츠에 맞게 조정합니다.

        # 행 번호(왼쪽에 있는 인덱스 숫자)를 숨깁니다.
        self.verticalHeader().setVisible(False)

    # 테이블 데이터 설정 함수
    def set_data(self, data):
        for row, (index, title, rate, release_date, img_path) in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(str(index)))  # 순위 정보를 셀에 추가합니다.
            self.setItem(row, 2, QTableWidgetItem(title))  # 제목 정보를 셀에 추가합니다.
            self.setItem(row, 3, QTableWidgetItem(rate))  # 예매율 정보를 셀에 추가합니다.
            self.setItem(row, 4, QTableWidgetItem(release_date))  # 개봉일 정보를 셀에 추가합니다.

            pixmap = download_image(img_path)  # 이미지를 다운로드합니다.
            if not pixmap.isNull():  # QPixmap이 유효한 이미지인지 확인합니다.
                label = QLabel()  # QLabel을 생성합니다.
                label.setPixmap(pixmap.scaled(95, 95, Qt.KeepAspectRatio))  # 이미지를 셀에 맞게 크기 조정하여 설정합니다.
                self.setCellWidget(row, 1, label)  # 셀에 QLabel을 추가합니다.



def main():
    app = QApplication(sys.argv)  # PyQt 애플리케이션 객체를 생성합니다.
    movie_data = fetch_movie_data()  # 영화 데이터를 가져옵니다.
    table = MovieTable(movie_data)  # 영화 테이블을 생성합니다.
    layout = QVBoxLayout()  # 수직 레이아웃을 생성합니다.
    layout.addWidget(table)  # 테이블을 레이아웃에 추가합니다.

    window = QWidget()  # 위젯을 생성합니다.
    window.setLayout(layout)  # 레이아웃을 위젯에 설정합니다.
    window.setWindowTitle("실시간 영화 순위")  # 창의 제목을 설정합니다.
    window.resize(606, 975)  # 창의 크기를 설정합니다.
    window.show()  # 창을 표시합니다.

    sys.exit(app.exec_())  # 애플리케이션 이벤트 루프를 시작하고 프로그램을 실행합니다.


if __name__ == "__main__":
    main()  # 메인 함수를 호출하여 프로그램을 실행합니다.