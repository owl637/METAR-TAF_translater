from .map import extract_icao, get_airport_name
from .taf_timeline import parse_taf_timeline
from .taf_translate import translate_taf_forecast_block

def translate_taf(code: str) -> str:
    """
    TAF全体を読み取り、自然な日本語の予報文に変換する。
    """
    icao = extract_icao(code)
    airport = get_airport_name(icao) or icao

    try:
        blocks = parse_taf_timeline(code)
        translated_blocks = [translate_taf_forecast_block(b) for b in blocks]
        return f"{airport}（{icao}）のTAF予報：\n" + "\n・" + "\n・".join(translated_blocks)
    except Exception as e:
        return f"[TAF翻訳エラー] {e}"
