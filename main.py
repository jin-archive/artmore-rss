import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import re
from urllib.parse import urljoin
import urllib3

# 공공/관련 기관 사이트 SSL 인증서 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_rss():
    # 아트모어 채용정보 리스트 URL
    url = "https://www.artmore.kr/sub/recruit/search_list.do"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    # HTTP 요청 및 파싱
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # RSS 피드 초기화
    fg = FeedGenerator()
    fg.title('아트모어 채용공고')
    fg.link(href=url, rel='alternate')
    fg.description('아트모어(artmore.kr) 최신 채용공고 RSS 피드입니다.')
    fg.language('ko')
    
    # 채용 공고 목록 추출 (a 태그 중심 탐색)
    links = soup.select('a')
    added_links = set()
    count = 0
    
    for a_tag in links:
        title = a_tag.get_text(strip=True)
        href = a_tag.get('href', '')
        onclick = a_tag.get('onclick', '')
        
        # 텍스트가 비어있거나 메뉴용 버튼인 경우 건너뜀
        if len(title) < 5 or title in ["로그인", "회원가입", "자세히보기", "검색"]:
            continue
            
        link = ""
        
        # 일반적인 링크 형태인 경우 (예: /sub/recruit/search_view.do?seq=123)
        if 'view.do' in href or 'seq=' in href or 'idx=' in href:
            link = urljoin(url, href)
            
        # 자바스크립트 함수로 연결되는 형태인 경우 (예: javascript:goView('123'))
        elif 'javascript:' in href or onclick:
            target_str = href if 'javascript:' in href else onclick
            match = re.search(r"\('?(.*?)'?\)", target_str)
            if match:
                post_id = match.group(1)
                # 실제 아트모어 상세페이지 파라미터 구조에 맞춰 조합 (필요시 'seq=' 등으로 변경)
                link = f"https://www.artmore.kr/sub/recruit/search_view.do?idx={post_id}"

        # 채용공고 링크로 유효하며, 중복 추가되지 않은 경우에만 RSS에 반영
        if link and link not in added_links:
            added_links.add(link)
            
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(f"새로운 채용 공고가 등록되었습니다: {title}")
            fe.guid(link)
            count += 1
            
    # 완성된 RSS를 xml 파일로 저장
    fg.rss_file('rss.xml')
    print(f"✅ rss.xml 생성 완료! (총 {count}개의 공고를 찾았습니다.)")

if __name__ == "__main__":
    generate_rss()
