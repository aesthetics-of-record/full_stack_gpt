from fastapi import FastAPI
import pyautogui
import base64
from PIL import Image
from io import BytesIO
from redis import Redis
import time
import asyncio
from contextlib import asynccontextmanager


# Redis 서버에 연결합니다. 호스트, 포트, db 번호를 필요에 따라 조정하세요.
redis_client = Redis(host='redis-13855.c290.ap-northeast-1-2.ec2.cloud.redislabs.com',
                     port=13855, password="rYuK2XYDjh0cNWlitwSy1tn34F0xmlHQ")


running = True


async def capture_screenshot_forever():
    count = 0
    global running

    while running:
        start_time = time.perf_counter()  # 시작 시간 기록

        # 스크린샷 캡처
        screenshot = pyautogui.screenshot()

        # BytesIO 객체를 사용하여 메모리상에서 이미지 처리
        img_buffer = BytesIO()

        # 스크린샷을 JPEG 형식으로 변환하여 BytesIO 객체에 저장
        screenshot.save(img_buffer, format="JPEG")

        # BytesIO 객체의 내용을 Base64 문자열로 인코딩
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

        # Redis에 키-값 쌍을 저장합니다.
        redis_client.set("screen_1", img_base64)

        count += 1

        end_time = time.perf_counter()  # 종료 시간 기록
        elapsed_time = end_time - start_time  # 경과 시간 계산

        print(f"Captured {count} - {elapsed_time}")

        await asyncio.sleep(0)


app = FastAPI()


@app.get('/start')
async def start_screen():
    global running
    running = True
    asyncio.create_task(capture_screenshot_forever())
    return "시작"


@app.get('/stop')
async def stop_screen():
    global running
    running = False
    return "종료"


@app.get('/api/screen')
async def get_screen():
    screen = redis_client.get("screen_1")
    return screen

if __name__ == "__main__":
    capture_screenshot_forever()
