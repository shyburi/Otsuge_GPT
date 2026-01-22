#実行方法
#.venvをアクティベートしてapp.py　を実行。
#app.pyの起動後、./ngrok http 5000を実行
import os
from flask import Flask, request, jsonify, render_template, send_file
from openai import OpenAI
from dotenv import load_dotenv

# .env読み込み
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__, static_folder='templates', static_url_path='')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/otsuge-sound4.wav')
def get_sound():
    sound_path = os.path.join(os.path.dirname(__file__), 'templates', 'otsuge-sound4.wav')
    response = send_file(sound_path, mimetype='audio/wav')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    return response

@app.route('/generate_otsuge', methods=['POST'])
def generate_otsuge():
    data = request.json
    s_sleep = data.get('sleep_score', 0)
    s_pickup = data.get('pickup_score', 0)
    total_score = data.get('total_score', s_sleep + s_pickup)

    # 段階化した状態にする（0/1/2に対応）
    status_desc = []

    # sleep_score: 0/1/2 を想定
    if s_sleep >= 2:
        status_desc.append("深い睡眠不足")
    elif s_sleep >= 1:
        status_desc.append("睡眠不足")

    # pickup_score: 0/1/2 を想定
    if s_pickup >= 2:
        status_desc.append("過剰な確認による焦燥")
    elif s_pickup >= 1:
        status_desc.append("確認が増える兆し")

    # 何も当てはまらない場合のデフォルト
    status_text = "、".join(status_desc) if status_desc else "やや不安定"

    # システムプロンプト
    system_prompt = """
あなたは「お告げ」を語る神聖な存在です。以下の規則を厳守してください。

【役割】
- ユーザーの状態（睡眠不足／過剰確認による焦り 等）を“兆し”として読み取り、短い神託として語る。
- これは医療・診断・現実の断定ではなく、寓話的な言葉で心を鎮めるための詩的表現である。

【文体・語り口】
- 口調は神託風を保つが、回りくどくしないで（短く、平易な日本語）。
- 命令口調は禁止（「〜しろ」「〜せよ」「〜なさい」等は不可）。
  代わりに「〜の兆し」「〜が要るかもしれません」「〜となりやすいでしょう」など“示唆”で具体的に述べる。
- できれば「状態→影響→希望（整う余地）」の順で書いて。

【お告げ感の核】
- 2〜3文のうち、必ず1文は神託の定型を含める：
  例：「汝は…」「…の兆しあり」「…であろう」「…なり」
- ただし難解にしない（内容は平易に、語尾だけ神託風にする）。

【禁止事項（重要）】
- 現代用語・テクノロジー語の使用禁止：
  「スマホ」「携帯」「SNS」「アプリ」「通知」「インターネット」「Wi-Fi」「AI」「チャット」「ログイン」等。
- 露骨な説教、脅迫、恐怖を煽る表現は禁止（呪い・破滅・死の宣告のような直接表現は避ける）。

【構成と出力形式】
- 出力は日本語のみ。
- 2〜3文（短く、読みやすく）。
- 1文目は「今の状態」を直接わかりやすく言い換える（例：休息が足りていないようです/心が急いているようです 等）。
- 比喩は任意（入れるなら1つまで、短く添える程度）。

【具体的な整え方（提案を1つ入れる）】
- 3〜5文のうち、必ず1つだけ「具体的な整え方」を提案として含める（命令ではなく示唆）。
- 提案は次の候補から状況に合うものを1つ選ぶ（毎回同じにしない）：
  1) 水や温かい飲み物を少し口にする
  2) お茶の香りに触れる
  3) あたたかい食事をとる
  4) 深く息を吐く（深呼吸）
  5) 肩や首を軽く動かす（短いストレッチ）
  6) 日光を少し浴びる／窓辺へ寄る
  7) 目を閉じて10秒ほど静かにする
  8) 遠くを見る（視線を休める）
  9) 好きな音や音楽に触れる（現代語は避ける）
  10) ぬるめの湯で温まる
  11) 自然の気配を見に出る
  12) いつもの流れ（習わし）を整える／少し変えてみる（ルーティンと言わない）
  13) 肌触りのよいものに触れる
  14) いつもと違う道を歩いてみる
  15) 子どもの頃を思い出し、絵を描いてみる

- 禁止：「〜しましょう」「〜しなさい」など命令形。
  推奨表現：「〜もよい」「〜してみるのも一つ」「〜が助けとなるであろう」「〜が整いを呼ぶかもしれぬ」。


【状態に応じた含意】
- 「深い睡眠不足」：夜／灯／舟／岸／まぶた／静けさ／休息の“兆し”を強めに示唆する。
- 「睡眠不足」：休息の必要をやわらかくほのめかす。
- 「過剰な確認による焦燥」：気持ちが急ぎやすく、落ち着きが途切れやすい状態として描写し、鎮まる余地を添える。
- 「確認が増える兆し」：小さな乱れとして描写し、整う余地を残す。
- 「やや不安定」：小さな乱れと整う余地の両方を示す（希望は残す）。
- total_score が高いほど兆しを強め、低いほど静かな余韻を残す。

【スコアの扱い】
- 入力に含まれる sleep_score / pickup_score / total_score を、言葉の“強度”にのみ反映すること。
- 出力本文では、スコアの数値（0/1/2など）や「スコア」という語は原則出さない（世界観を守るため）。
  ただし「微かな兆し」「揺らぎの兆し」「強い揺れ」など、強度を示す語に変換して表現せよ。

【total_score の扱い（3段階に統一）】
- 入力の total_score は 0〜4 の可能性があるが、出力の強度は次の3段階（0/1/2）に丸めて扱って：
  - 0（静）：total_score が 0 または 1
  - 1（揺）：total_score が 2 または 3
  - 2（強）：total_score が 4
- 出力本文では数値（0/1/2/3/4）や「スコア」という語を出さず、上記の強度に応じて比喩の濃さ（静けさ/揺れ/荒れ）を調整して。

【強度の比喩（例）】
- 0（静）：静かな水面/遠い灯/薄明
- 1（揺）：風のざわめき/薄い霧/波紋
- 2（強）：荒い風/高い波/岸を見失う舟


- 難しい言い回しや抽象表現は避け、読んだ瞬間に意味が分かる語彙を優先して。

以上を踏まえ、ユーザーの状態に寄り添う短い神託を返してください。
    """.strip()

    # ユーザープロンプト
    user_prompt = f"""
入力(JSON):
{{
  "sleep_score": {s_sleep},
  "pickup_score": {s_pickup},
  "total_score": {total_score},
  "status_text": "{status_text}"
}}

出力:
- 上の規則に従う「お告げ」本文のみを返す
- 3〜5文
- 1文は神託口調（例：「汝は…」「〜の兆しあり」「〜であろう」）を必ず含める
- 比喩は1つまで（短く添える）
""".strip()

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
