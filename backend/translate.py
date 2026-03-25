# translate.py
import os
import requests
from dotenv import load_dotenv
from fastapi import APIRouter

# ------------------ Baidu Translator 功能 ------------------
class BaiduTranslator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("BAIDU_API_KEY")
        self.secret_key = os.getenv("BAIDU_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise RuntimeError("请在 .env 文件中配置 BAIDU_API_KEY 和 BAIDU_SECRET_KEY")

        self.access_token = self._get_access_token()

    def _get_access_token(self):
        token_url = (
            f"https://aip.baidubce.com/oauth/2.0/token?"
            f"grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        )
        try:
            res = requests.get(token_url, timeout=5).json()
        except Exception as e:
            raise RuntimeError(f"获取 access_token 失败: {e}")

        access_token = res.get("access_token")
        if not access_token:
            raise RuntimeError(f"获取 access_token 失败: {res}")
        return access_token

    def translate(self, text, from_lang="auto", to_lang="zh"):
        url = f"https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token={self.access_token}"
        payload = {"q": text, "from": from_lang, "to": to_lang}
        headers = {"Content-Type": "application/json"}

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=5).json()
        except Exception as e:
            print("调用翻译接口失败:", e)
            return None

        # 调试信息
        print("------ 调试信息 ------")
        print("请求文本:", text)
        print("接口返回:", res)
        print("--------------------")

        if "result" in res and "trans_result" in res["result"]:
            return res["result"]["trans_result"][0]["dst"]
        else:
            print("翻译接口返回异常:", res)
            return None

# ------------------ FastAPI 路由 ------------------
router = APIRouter()
translator = BaiduTranslator()

@router.get("/translate")
def translate(q: str, from_lang: str = "auto", to_lang: str = "zh"):
    """
    GET /translate?q=Hello&from_lang=auto&to_lang=zh
    """
    result = translator.translate(q, from_lang, to_lang)
    return {"original": q, "translated": result}

# ------------------ 测试用 ------------------
if __name__ == "__main__":
    translator = BaiduTranslator()
    text = "Hello world"
    translated = translator.translate(text)
    print("------ 翻译结果 ------")
    print("原文:", text)
    print("翻译:", translated)