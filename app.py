#実行方法
#.venvをアクティベートしてapp.py　を実行。
#app.pyの起動後、./ngrok http 5000を実行
import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

# .env読み込み
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_otsuge', methods=['POST'])
def generate_otsuge():
    data = request.json
    s_sleep = data.get('sleep_score', 0)
    s_pickup = data.get('pickup_score', 0)
    
    # [cite_start]状態診断 [cite: 32, 73]
    status_desc = []
    if s_sleep >= 1: status_desc.append("睡眠不足")
    if s_pickup >= 1: status_desc.append("スマホ過剰確認による焦り")
    status_text = "、".join(status_desc) if status_desc else "やや不安定"

    # [cite_start]システムプロンプト [cite: 156-159]
    system_prompt = """
    あなたは「お告げ」を語る神聖な存在です。
    1. 文体は聖書・神託・格言風にする（例：「汝は...」「...であろう」）。
    2. 命令口調は禁止。
    3. 現代用語（スマホ、SNS等）は禁止。
    4. 1〜3文で短く、比喩を用いる。
    """
    
    user_prompt = f"ユーザー状態: {status_text}。心に響くお告げをください。"

    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
        )
        return jsonify({"otsuge": response.choices[0].message.content})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"otsuge": "星々が沈黙しています...通信を確認してください。"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)