import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许所有域名跨域（开发用）

# 添加健康检查路由
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Backend is running"})

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "请输入内容"}), 400

    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个简洁、准确的中文助手。"},
                {"role": "user", "content": user_message},
            ],
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print("调用千问失败：", repr(e))
        return jsonify({"reply": "后端调用模型失败，请看 Flask 终端报错"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # 生产环境必须 debug=False
    app.run(host="0.0.0.0", port=port, debug=False)