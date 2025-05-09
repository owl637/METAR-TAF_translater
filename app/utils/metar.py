from metar import Metar
from datetime import datetime
from .map import get_airport_name

def parse_metar(code):
    try:
        obs = Metar.Metar(code)
        return obs.string()
    except Exception as e:
        return f"[METAR解析失敗] {e}"

def translate_structured_metar(raw: str, icao: str = "") -> str:
    lines = raw.strip().split("\n")
    output = []

    airport_name = get_airport_name(icao) if icao else icao

    for line in lines:
        line = line.strip()

        if line.startswith("station:"):
            code = line.split(":")[1].strip()
            output.append(f"観測地点：{code}（{airport_name}）")
        elif line.startswith("type:"):
            if "automatic" in line:
                output.append("報告種別：定時報告（自動報告）")
            else:
                output.append("報告種別：定時報告")
        elif line.startswith("time:"):
            dt_str = line.replace("time:", "").strip()
            try:
                dt = datetime.strptime(dt_str, "%a %b %d %H:%M:%S %Y")
                output.append(f"観測時刻：{dt.year}年{dt.month}月{dt.day}日 {dt.hour}時{dt.minute:02d}分（{['月','火','水','木','金','土','日'][dt.weekday()]}）")
            except:
                output.append(f"観測時刻：{dt_str}")
        elif line.startswith("temperature:"):
            val = line.split(":")[1].strip()
            output.append(f"気温：{val.replace(' C','')}℃")
        elif line.startswith("dew point:"):
            val = line.split(":")[1].strip()
            output.append(f"露点温度：{val.replace(' C','')}℃")
        elif line.startswith("wind:"):
            parts = line.split("gusting to")
            base = parts[0].strip().replace("wind:", "").replace("at", "で").replace("knots", "ノット")
            gust = parts[1].strip().replace("knots", "ノット") if len(parts) > 1 else ""
            wind_text = f"風：{base}"
            if gust:
                wind_text += f"、最大瞬間風速{gust}"
            output.append(wind_text)
        elif line.startswith("visibility:"):
            val = line.split(":")[1].strip()
            output.append(f"視程：{val}（約{round(float(val.split()[0]) * 1.6,1)}km）")
        elif line.startswith("pressure:"):
            val = line.split(":")[1].strip()
            output.append(f"気圧：{val.replace('mb','ヘクトパスカル')}")
        elif line.startswith("sky:"):
            clouds = [line[5:].strip()]
            output.append("雲の状況：")
        elif line.startswith("     "):  # 雲の続き
            clouds.append(line.strip())
        elif line.startswith("sea-level pressure:"):
            val = line.split(":")[1].strip()
            output.append(f"海面気圧：{val.replace('mb','ヘクトパスカル')}")
        elif line.startswith("remarks:"):
            output.append("備考：")
        elif line.startswith("- "):
            if "pressure change" in line:
                output.append("- 過去3時間の気圧変化：" + line.split("change")[1].replace("decreasing", "減少").replace("increasing", "増加").replace("then", "その後").replace("hPa", "hPa"))
            elif "AO2A" in line:
                output.append("- AO2A（自動気象観測装置）、降水情報なし、着氷情報なし")
            else:
                output.append("- " + line[2:])
        else:
            if "clouds" in line:
                typ, alt = line.split(" at ")
                trans = {
                    "scattered clouds": "雲が点在",
                    "broken clouds": "厚い雲"
                }.get(typ.strip(), typ.strip())
                output.append(f"- 高度{alt.strip()}に{trans}")

    # 雲のまとめ（省略せず出力）
    if 'clouds' in locals():
        for c in clouds:
            typ, alt = c.split(" at ")
            jp_typ = {
                "scattered clouds": "雲が点在",
                "broken clouds": "厚い雲"
            }.get(typ.strip(), typ.strip())
            output.append(f"- 高度{alt.strip()}に{jp_typ}")

    return "\n".join(output)
