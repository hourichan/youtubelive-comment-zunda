"""ずんだもんがYouTube Liveのコメントを読み上げてくれる"""
import json
import re
import time

import pytchat
import requests
from playsound import playsound

# VOICEVOXをインストールしたPCのホスト名を指定
HOSTNAME = "127.0.0.1"


def remove_custom_emoji(text) -> str:
    """絵文字を削除する関数

    Args:
        text (string): テキスト
    Returns:
        string: 絵文字削除後のテキスト
    """
    pattern = r":[a-zA-z0-9_]+:"
    return re.sub(pattern, "", text)


def read_comment(input_texts, speaker=1) -> None:
    """_summary_

    Args:
        input_texts (string): 読み上げさせたいテキスト
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
            timeout=3.5,
        )
        # wavファイルに書き込み
        with open("comment.wav", mode="wb") as file:
            file.write(res2.content)
        playsound("comment.wav")


if __name__ == "__main__":
    # PytchatCoreオブジェクトの取得
    video_id = input("video_id: ")
    livechat = pytchat.create(video_id=video_id)
    while livechat.is_alive():
        # チャットデータの取得
        chatdata = livechat.get()
        for c in chatdata.items:
            print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
            print(f"{c.author.name}さん: {remove_custom_emoji(c.message)}")
            read_comment(
                f"{remove_custom_emoji(c.author.name)}さん\
                    {remove_custom_emoji(c.message)}"
            )
        time.sleep(1)
