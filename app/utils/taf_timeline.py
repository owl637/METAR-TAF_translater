import re

def parse_taf_timeline(code: str):
    """
    TAFコードを以下の構造に分解する：
    [
        {
            "type": "main" | "TEMPO" | "BECMG" | "FM",
            "period": "0908/1014"（またはFM時刻など）,
            "elements": [ ... ]  # 予報構文トークン
        },
        ...
    ]
    """
    tokens = code.strip().split()
    result = []

    # 先頭に TAF が2回書かれるパターンもありうるので、複数回削除
    while tokens and tokens[0].upper() == "TAF":
        tokens.pop(0)

    # ICAOコード（4文字）
    if tokens and re.match(r"^[A-Z]{4}$", tokens[0]):
        tokens.pop(0)

    # 発表時刻（6桁+Z）
    if tokens and re.match(r"^\d{6}Z$", tokens[0]):
        tokens.pop(0)

    # 最初の有効期間（例：0908/1014）を取得
    if re.match(r"^\d{4}/\d{4}$", tokens[0]):
        current_block = {
            "type": "main",
            "period": tokens.pop(0),
            "elements": []
        }
        result.append(current_block)
    else:
        current_block = {
            "type": "main",
            "period": "",
            "elements": []
        }
        result.append(current_block)

    # 残りの構文をブロックに分割
    for token in tokens:
        # 新しいセクションが始まる
        if token.startswith(("FM", "BECMG", "TEMPO")):
            kind = None
            period = ""
            if token.startswith("FM"):
                kind = "FM"
                period = token[2:]
            elif token == "BECMG" or token == "TEMPO":
                kind = token
            elif re.match(r"^BECMG\d{4}/\d{4}$", token):
                kind = "BECMG"
                period = token[5:]
            elif re.match(r"^TEMPO\d{4}/\d{4}$", token):
                kind = "TEMPO"
                period = token[5:]

            current_block = {
                "type": kind,
                "period": period,
                "elements": []
            }
            result.append(current_block)
        elif re.match(r"^\d{4}/\d{4}$", token):
            current_block["period"] = token
        else:
            current_block["elements"].append(token)

    return result
