from flask import Blueprint, render_template, request, send_file, session
from io import BytesIO
from .utils.decode_and_translate import decode_and_translate
from .utils.map import extract_icao, get_google_maps_url, get_airport_name
from .utils.taf_timeline import parse_taf_timeline

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    result = ""
    code = ""
    map_url = ""
    timeline = []
    airport_name = ""

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        action = request.form.get("action")
        if code:
            result = decode_and_translate(code)
            icao = extract_icao(code)
            map_url = get_google_maps_url(icao)
            airport_name = get_airport_name(icao)

            # 履歴に保存
            history = session.get("history", [])
            history_entry = {"code": code, "airport": airport_name, "icao": icao, "result": result}
            if history_entry not in history:
                history.insert(0, history_entry)  # 新しい順に追加
            session["history"] = history[:10]    # 最大10件に制限

            if action == "download":
                # ダウンロード用ファイルを作成
                file_content = f"【入力コード】\n{code}\n\n【解析結果】\n{result}"
                if code.upper().startswith("TAF"):
                    timeline_data = parse_taf_timeline(code)
                    file_content += "\n\n【TAFタイムライン】\n" + "\n".join(timeline_data)

                # バイナリ形式でファイルを送信
                buffer = BytesIO()
                buffer.write(file_content.encode("utf-8"))
                buffer.seek(0)
                return send_file(buffer, as_attachment=True, download_name="解析結果.txt", mimetype="text/plain")

            # 通常の解析処理
            icao = extract_icao(code)
            map_url = get_google_maps_url(icao)

            if code.upper().startswith("TAF"):
                timeline = parse_taf_timeline(code)
    history = session.get("history", [])
    return render_template("index.html", code=code, result=result, map_url=map_url, timeline=timeline, history=history, airport_name=airport_name)