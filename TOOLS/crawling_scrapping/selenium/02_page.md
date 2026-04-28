페이지 조작은 주제별로 나눠 설명하겠습니다. 먼저 각 상호작용 기법을 직접 시뮬레이션해볼 수 있는 인터랙티브 데모입니다.탭을 바꿔가며 각 동작 버튼을 눌러보면 브라우저 안의 변화와 실행되는 코드를 함께 확인할 수 있습니다. 이제 각 영역을 코드와 함께 상세히 설명드립니다.

---

## 1. 클릭 조작

```python
from selenium.webdriver.common.by import By

# 기본 클릭
driver.find_element(By.CSS_SELECTOR, ".post-item a").click()

# 링크 텍스트로 클릭
driver.find_element(By.LINK_TEXT, "다음").click()

# 브라우저 네비게이션
driver.back()       # 이전 페이지
driver.forward()    # 앞 페이지
driver.refresh()    # 새로고침

# 새 탭으로 열리는 링크 처리
driver.find_element(By.CSS_SELECTOR, "a[target='_blank']").click()
driver.switch_to.window(driver.window_handles[-1])  # 새 탭으로 전환
# 작업 후 원래 탭으로 복귀
driver.close()
driver.switch_to.window(driver.window_handles[0])
```

---

## 2. 텍스트 입력

```python
from selenium.webdriver.common.keys import Keys

search = driver.find_element(By.ID, "search_text")

# 입력 전 항상 clear()로 기존 값 제거
search.clear()
search.send_keys("삼성전자")

# 키보드 단축키 조합
search.send_keys(Keys.ENTER)              # 엔터
search.send_keys(Keys.CONTROL + "a")      # 전체 선택
search.send_keys(Keys.CONTROL + "c")      # 복사
search.send_keys(Keys.TAB)               # 다음 필드로 이동
search.send_keys(Keys.ARROW_DOWN)        # 방향키 (자동완성 탐색)
search.send_keys(Keys.ESCAPE)            # ESC (팝업 닫기)
```

자동완성 드롭다운이 있는 검색창 처리 패턴:

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

search = driver.find_element(By.ID, "search_text")
search.clear()
search.send_keys("삼성")

# 자동완성 목록이 뜰 때까지 대기 후 첫 번째 선택
wait = WebDriverWait(driver, 5)
first = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, ".autocomplete-item:first-child")
))
first.click()
```

---

## 3. 스크롤

스크롤은 동적 로딩 페이지(무한 스크롤, lazy load)에서 필수입니다.

```python
# 특정 픽셀 위치로 이동
driver.execute_script("window.scrollTo(0, 1000)")

# 맨 아래로 스크롤 (무한 스크롤 트리거용)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

# 특정 요소가 화면에 보이도록 스크롤
element = driver.find_element(By.CSS_SELECTOR, ".comment-section")
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

# ActionChains로 부드럽게 스크롤 (Selenium 4.2+)
from selenium.webdriver.common.action_chains import ActionChains
ActionChains(driver).scroll_by_amount(0, 500).perform()

# 무한 스크롤 페이지 전체 수집 패턴
import time

def scroll_and_collect(driver):
    results = []
    last_height = 0
    
    while True:
        # 현재 보이는 게시글 수집
        items = driver.find_elements(By.CSS_SELECTOR, ".post-item")
        for item in items:
            text = item.text
            if text not in results:
                results.append(text)
        
        # 맨 아래로 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)  # 새 콘텐츠 로드 대기
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 더 이상 콘텐츠 없음
        last_height = new_height
    
    return results
```

---

## 4. 드롭다운과 체크박스

```python
from selenium.webdriver.support.ui import Select

# 드롭다운 (<select> 태그)
dropdown = Select(driver.find_element(By.NAME, "board_type"))

dropdown.select_by_visible_text("종목토론실")  # 텍스트로 선택
dropdown.select_by_index(0)                    # 인덱스로 선택 (0부터)
dropdown.select_by_value("1")                  # value 속성으로 선택

# 현재 선택된 값 확인
print(dropdown.first_selected_option.text)

# 다중 선택 드롭다운
dropdown.select_by_index(1)
dropdown.select_by_index(2)  # 추가 선택
dropdown.deselect_all()      # 전체 해제

# 체크박스
chk = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']#today_only")

if not chk.is_selected():    # 현재 선택 안 돼있으면
    chk.click()              # 선택

print(chk.is_selected())     # True / False
```

---

## 5. 팝업·iframe·새 탭 전환

이 세 가지는 가장 자주 막히는 지점입니다.

```python
# ── iframe 전환 ────────────────────────────────────
# iframe ID나 name으로 전환
driver.switch_to.frame("frame_main")

# 요소를 찾아서 전환
iframe = driver.find_element(By.CSS_SELECTOR, "iframe.ad-frame")
driver.switch_to.frame(iframe)

# iframe 내부에서 요소 탐색 가능
content = driver.find_element(By.CSS_SELECTOR, ".inner-content")

# 반드시 메인으로 복귀 후 다음 작업
driver.switch_to.default_content()

# ── 브라우저 Alert 팝업 처리 ───────────────────────
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

wait = WebDriverWait(driver, 5)

try:
    alert = wait.until(EC.alert_is_present())
    print("팝업 텍스트:", alert.text)
    alert.accept()    # 확인 버튼
    # alert.dismiss() # 취소 버튼
except:
    pass  # 팝업 없으면 그냥 통과

# ── 새 탭/창 전환 ──────────────────────────────────
original = driver.current_window_handle

# 새 탭 링크 클릭 후
driver.find_element(By.CSS_SELECTOR, "a.detail-link").click()

# 새 탭으로 전환
for handle in driver.window_handles:
    if handle != original:
        driver.switch_to.window(handle)
        break

# 작업 완료 후 원래 탭으로 복귀
driver.close()
driver.switch_to.window(original)

# ── 쿠키 동의·로그인 팝업 자동 닫기 ──────────────
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    btn = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".agree-btn, .close-btn"))
    )
    btn.click()
except:
    pass
```

---

## 6. JavaScript 직접 실행 — `execute_script()`

일반 Selenium 메서드로 안 되는 상황의 최후 수단입니다.

```python
# 값 읽기 (return으로 반환)
title = driver.execute_script("return document.title")
url   = driver.execute_script("return window.location.href")
height = driver.execute_script("return document.body.scrollHeight")

# 숨겨진 요소 강제 클릭 (visibility:hidden, display:none 등)
el = driver.find_element(By.CSS_SELECTOR, ".hidden-button")
driver.execute_script("arguments[0].click()", el)

# 요소 속성·스타일 강제 변경
driver.execute_script("arguments[0].removeAttribute('disabled')", el)
driver.execute_script("arguments[0].style.display = 'block'", el)

# 요소의 화면 위치·크기 확인
rect = driver.execute_script("return arguments[0].getBoundingClientRect()", el)
print(rect)  # {'top': 120, 'left': 40, 'width': 300, 'height': 44}

# LocalStorage 읽기 (로그인 토큰 등)
token = driver.execute_script("return localStorage.getItem('auth_token')")

# 여러 작업을 하나의 스크립트에서
driver.execute_script("""
    arguments[0].setAttribute('data-scraped', 'true');
    arguments[0].style.border = '2px solid green';
    window.scrollBy(0, 200);
""", el)
```

---

## 7. ActionChains — 고급 마우스·키보드 조작

```python
from selenium.webdriver.common.action_chains import ActionChains

actions = ActionChains(driver)

# 마우스 호버 (hover) — 드롭다운 메뉴 펼치기
menu = driver.find_element(By.CSS_SELECTOR, ".nav-menu")
actions.move_to_element(menu).perform()

# 드래그 앤 드롭
source = driver.find_element(By.ID, "drag-item")
target = driver.find_element(By.ID, "drop-zone")
actions.drag_and_drop(source, target).perform()

# 더블 클릭
actions.double_click(element).perform()

# 우클릭 (컨텍스트 메뉴)
actions.context_click(element).perform()

# 체인으로 연결 — 호버 후 나타나는 서브메뉴 클릭
(ActionChains(driver)
    .move_to_element(driver.find_element(By.CSS_SELECTOR, ".menu-item"))
    .pause(0.5)
    .click(driver.find_element(By.CSS_SELECTOR, ".submenu a"))
    .perform())
```

---

## 8. 실전 종합 예제 — 주식 토론방 수집 플로우

```python
import time
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def scrape_board(driver, stock_code):
    wait = WebDriverWait(driver, 10)
    driver.get(f"https://finance.naver.com/item/board.naver?code={stock_code}")

    # 1. 쿠키 팝업 닫기
    try:
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".btn_agree, .close")
        )).click()
    except:
        pass

    # 2. 드롭다운으로 게시판 유형 선택
    try:
        sel = Select(driver.find_element(By.NAME, "board_type"))
        sel.select_by_visible_text("종목토론실")
    except:
        pass

    results = []

    for page in range(1, 6):
        # 3. 게시글 목록 로드 대기
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".type2 tr td.title")
        ))

        rows = driver.find_elements(By.CSS_SELECTOR, ".type2 tr")
        for row in rows:
            try:
                a = row.find_element(By.CSS_SELECTOR, "td.title a")
                results.append({
                    "title": a.text.strip(),
                    "link":  a.get_attribute("href"),
                    "date":  row.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text,
                })
            except:
                continue

        # 4. 다음 페이지 이동
        try:
            next_btn = wait.until(EC.element_to_be_clickable(
                (By.LINK_TEXT, str(page + 1))
            ))
            # 요소가 화면에 보이도록 스크롤 후 클릭
            driver.execute_script("arguments[0].scrollIntoView()", next_btn)
            next_btn.click()
            time.sleep(0.8)
        except:
            break

    return results
```

다음 단계인 대기 전략(Explicit Wait, Expected Conditions)으로 넘어가면 이 코드에서 `wait.until()` 부분을 훨씬 정교하게 다룰 수 있게 됩니다. 원하시면 이어서 설명드리겠습니다.