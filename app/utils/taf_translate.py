import re

def translate_taf_forecast_block(block: dict) -> str:
    type_map = {
        "main": "期間中を通じて",
        "BECMG": "次第に",
        "TEMPO": "一時的に",
        "FM": "時刻以降に"
    }

    jp = []

    # 時間表現
    period = block.get("period", "")
    if re.match(r"^\d{4}/\d{4}$", period):
        f_day, f_hour = period[:2], period[2:4]
        t_day, t_hour = period[5:7], period[7:]
        time_phrase = f"{f_day}日{f_hour}時〜{t_day}日{t_hour}時"
    elif re.match(r"^\d{6}$", period):  # FM時刻（例：100600）
        day, hour, minute = period[:2], period[2:4], period[4:]
        time_phrase = f"{day}日{hour}時{minute}分以降"
    else:
        time_phrase = ""

    prefix = type_map.get(block["type"], "")
    if prefix and time_phrase:
        jp.append(f"{time_phrase}に{prefix}")
    elif time_phrase:
        jp.append(f"{time_phrase}")
    elif prefix:
        jp.append(f"{prefix}")

    elements = block.get("elements", [])

    # 風
    for token in elements:
        if re.match(r'^(VRB|\d{3})\d{2}(G\d{2})?KT$', token):
            direction = token[:3]
            speed = int(token[3:5])
            gust = re.search(r'G(\d{2})', token)

            if direction == "VRB":
                dir_jp = "風向不定"
            elif direction == "000":
                dir_jp = "静穏"
            else:
                dir_jp = f"{int(direction)}度"

            text = f"{dir_jp}の風 {speed}ノット"
            if gust:
                text += f"（最大{int(gust.group(1))}ノット）"
            jp.append(text)
            break

    # 視程
    for token in elements:
        if re.match(r'^\d{4}$', token):
            val = int(token)
            if val >= 9999:
                jp.append("視程10km以上")
            else:
                jp.append(f"視程{val/1000:.1f}km")
            break

    # 天気現象
    wx_map = {
        "-RA": "小雨", "RA": "雨", "+RA": "強い雨",
        "-SHRA": "にわか雨", "SHRA": "にわか雨",
        "TSRA": "雷雨", "+TSRA": "強い雷雨",
        "BR": "もや", "FG": "霧", "NSW": "顕著な天気現象なし"
    }

    for token in elements:
        if token in wx_map:
            jp.append(wx_map[token])

    # 雲
    cloud_map = {
        "FEW": "わずかな雲", "SCT": "雲が点在",
        "BKN": "厚い雲", "OVC": "全面的な雲"
    }

    for token in elements:
        match = re.match(r'^(FEW|SCT|BKN|OVC)(\d{3})(CB|TCU)?$', token)
        if match:
            typ, alt_str, suffix = match.groups()
            alt = int(alt_str) * 100
            desc = f"高度{alt}フィートに{cloud_map.get(typ, typ)}"
            if suffix == "CB":
                desc += "（積乱雲）"
            elif suffix == "TCU":
                desc += "（塔状積雲）"
            jp.append(desc)

    # 気圧（QNH2985INS → 1010.9hPa）
    for token in elements:
        if token.startswith("QNH") and "INS" in token:
            qnh = token[3:7]
            try:
                qnh_float = round(float(qnh) * 33.8639 / 100, 1)
                jp.append(f"気圧{qnh_float}hPa")
            except:
                continue

    return "、".join(jp).rstrip("、") + "。"
