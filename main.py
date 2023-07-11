"""ずんだもんがYouTube Liveのコメントを読み上げてくれる"""
import json
import re
import time

import pytchat
import requests
from googletrans import Translator
from playsound import playsound

# VOICEVOXをインストールしたPCのホスト名を指定
HOSTNAME = "127.0.0.1"


def remove_custom_emoji(text) -> str:
    """絵文字を削除する関数

    Args:
        text (str): テキスト
    Returns:
        str: 絵文字削除後のテキスト
    """
    pattern = r":[^:]+:"
    return re.sub(pattern, "", text)


def contains_japanese(text: str) -> bool:
    """テキストが日本語で構成されているかどうかを判定する関数

    Args:
        text (str): 判定させたいテキスト

    Returns:
        bool: フラグ
    """
    japanese_pattern = re.compile("[\u3040-\u309F\u30A0-\u30FF\uFF66-\uFF9F]+")
    return bool(japanese_pattern.search(text))


def read_comment(input_texts, speaker=1) -> None:
    """テキストを読み上げさせる関数

    Args:
        input_texts (str): 読み上げさせたいテキスト
        speaker (int, optional): 読み上げさせたい話者（1がずんだもん、2がめたん). Defaults to 1.
    """
    # 「 。」で文章を区切り１行ずつ音声合成させる
    input_texts = input_texts.replace("鳳梨", "ほうり")
    texts = input_texts.split("。")

    # 音声合成処理のループ
    for text in enumerate(texts):
        if text == "":
            continue

        # audio_query (音声合成用のクエリを作成するAPI)
        res1 = requests.post(
            "http://" + HOSTNAME + ":50021/audio_query",
            params={"text": text, "speaker": speaker},
            timeout=3.5,
        )
        res1 = json.loads(res1.text)
        res1["speedScale"] = 1.3
        # synthesis (音声合成するAPI)
        res2 = requests.post(
            "http://" + HOSTNAME + ":50021/synthesis",
            params={"speaker": speaker},
            data=json.dumps(res1),
            timeout=5.0,
        )
        # wavファイルに書き込み
        with open("comment.wav", mode="wb") as file:
            file.write(res2.content)

        # wavの再生
        playsound("comment.wav")


if __name__ == "__main__":
    # https://www.youtube.com/watch?v=xxxxxxxxxxxのxxxxxxxxxxxの部分がvideo_id
    video_id = input("video_id: ")
    livechat = pytchat.create(video_id=video_id)
    while livechat.is_alive():
        # チャットデータの取得
        chatdata = livechat.get()
        for c in chatdata.items:
            # 日本語じゃないコメントが来たら翻訳する
            if contains_japanese(c.message) is False:
                translator = Translator()
                message = remove_custom_emoji(
                    translator.translate(c.message, src="en", dest="ja").text
                )
            else:
                message = remove_custom_emoji(c.message)

            print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
            print(f"{c.author.name}さん: {message}")
            try:
                read_comment(
                    f"{remove_custom_emoji(c.author.name)}さん {message}"
                )
            except (requests.exceptions.ReadTimeout, TimeoutError):
                print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
                print("Timed out.")

        time.sleep(1)
