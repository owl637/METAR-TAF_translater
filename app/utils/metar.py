from metar import Metar
from datetime import datetime
from .map import get_airport_name

def parse_metar(code):
    try:
        obs = Metar.Metar(code)
        result = obs.string()
        print("=== Metar.Metar(code).string() ===")
        print(result)
        print("==================================")
        return result
    except Exception as e:
        return f"[METAR解析失敗] {e}"

def translate_structured_metar(raw: str, icao: str = "") -> str:
    lines = raw.strip().split("\n")
    output = []

    airport_name = get_airport_name(icao) if icao else icao
    clouds = []
    collecting_clouds = False

    for i, line in enumerate(lines):
        line = line.rstrip()

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
            base = parts[0].strip().replace("wind:", "").replace("at", "から").replace("knots", "ノット")

            # 方位変換
            for abbr, jp in {
                "N": "北", "NNE": "北北東", "NE": "北東", "ENE": "東北東",
                "E": "東", "ESE": "東南東", "SE": "南東", "SSE": "南南東",
                "S": "南", "SSW": "南南西", "SW": "南西", "WSW": "西南西",
                "W": "西", "WNW": "西北西", "NW": "北西", "NNW": "北北西"
            }.items():
                base = base.replace(abbr, jp)

            gust = parts[1].strip().replace("knots", "ノット") if len(parts) > 1 else ""
            wind_text = f"風：{base}"
            if gust:
                wind_text += f"、最大瞬間風速{gust}"
            output.append(wind_text)


        elif line.startswith("visibility:"):
            val = line.split(":")[1].strip().replace("miles", "マイル")
            output.append(f"視程：{val}（約{round(float(val.split()[0]) * 1.6,1)}km）")

        elif line.startswith("pressure:"):
            val = line.split(":")[1].strip()
            output.append(f"気圧：{val.replace('mb','hPa')}")

        elif line.startswith("sky:"):
            first = line[5:].strip().replace('feet', 'フィート').replace('meters', 'メートル')
            if "clouds at" in first:
                clouds.append(first)
                print(f"[DEBUG] sky line → {first}")
            collecting_clouds = True  # 次の行も雲かもしれない

        elif line.startswith("sea-level pressure:"):
            val = line.split(":")[1].strip()
            output.append(f"海面気圧：{val.replace('mb','hPa')}")
            collecting_clouds = False  # 次の構造が来たので雲情報の収集終了

        elif line.startswith("remarks:"):
            # remarks: が出る前に雲の出力を行う
            if clouds:
                output.append("雲の状況：")
                for c in clouds:
                    if " at " in c:
                        typ, alt = c.split(" at ")
                        jp_typ = {
                            "scattered clouds": "雲が点在",
                            "broken clouds": "厚い雲",
                            "few clouds": "わずかな雲",
                            "overcast clouds": "全面的な雲"
                        }.get(typ.strip(), typ.strip())
                        output.append(f"- 高度{alt.strip()}に{jp_typ}")
            output.append("備考：")
            collecting_clouds = False

        elif collecting_clouds and "clouds at" in line:
            clouds.append(line.strip().replace('feet', 'フィート').replace('meters', 'メートル'))
            print(f"[DEBUG] continued cloud → {line.strip()}")

        elif line.startswith("- "):
            if "pressure change" in line:
                output.append("- 過去3時間の気圧変化：" + line.split("change")[1]
                              .replace("decreasing", "減少")
                              .replace("increasing", "増加")
                              .replace("then", "その後")
                              .replace("hPa", "hPa"))
            elif "AO2A" in line:
                output.append("- AO2A（自動気象観測装置）、降水情報なし、着氷情報なし")
            else:
                output.append("- " + line[2:])
    return "\n".join(output)
