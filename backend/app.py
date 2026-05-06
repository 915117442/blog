from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)

# 1. 全局启用 CORS，允许前端域名
CORS(app, origins=["https://915117442.github.io", "https://blog-production-2e54.up.railway.app"])

# 2. 添加健康检查
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Backend running"})

# 3. 聊天 API 路由（同时处理 OPTIONS 和 POST）
@app.route('/api/chat', methods=['OPTIONS', 'POST'])
def chat():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200

    # 实际 POST 逻辑
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "请输入内容"}), 400

    # 初始化 OpenAI 客户端（这里应使用你的 API Key）
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        return jsonify({"reply": "服务配置错误"}), 500

    client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
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
        print("调用失败：", e)
        return jsonify({"reply": "AI 服务繁忙，请稍后再试"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)