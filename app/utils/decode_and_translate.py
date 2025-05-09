from .determine_type import is_taf
from .metar import parse_metar, translate_structured_metar
from .taf import translate_taf
from .map import extract_icao

def decode_and_translate(code: str) -> str:
    if is_taf(code):
        result = translate_taf(code)         # 翻訳本体
        return result
    else:
        icao = extract_icao(code)
        parsed = parse_metar(code)
        return translate_structured_metar(parsed, icao)
