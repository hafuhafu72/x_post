import tweepy
import random
import json
import os
from datetime import datetime

class TwitterAutoPost:
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        """
        Twitter自動投稿システムの初期化
        """
        # Twitter API v2クライアント
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
    
    def load_tweet_templates(self, filepath='tweets.json'):
        """
        投稿テンプレートをJSONファイルから読み込む
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('tweets', data)  # 'tweets'キーがあればそれを、なければ全体を返す
        except FileNotFoundError:
            print("❌ tweets.jsonが見つかりません")
            return []
    
    def create_tweet_content(self, templates):
        """
        ツイート内容を生成（ランダムにテンプレートを選択）
        """
        if not templates:
            return "定期投稿です"
        
        template = random.choice(templates)
        return template
    
    def post_tweet(self, content, reply_settings="mentionedUsers"):
        """
        ツイートを投稿
        
        reply_settings:
        - "everyone": 全員が返信可能（デフォルト）
        - "mentionedUsers": メンション相手のみ返信可能
        - "following": フォロー中のユーザーのみ返信可能
        """
        try:
            response = self.client.create_tweet(
                text=content,
                reply_settings=reply_settings
            )
            
            print(f"✅ 投稿成功: {datetime.now()}")
            print(f"内容: {content}")
            print(f"Tweet ID: {response.data['id']}")
            print(f"リプライ設定: {reply_settings}")
            
            # GitHub Actionsの出力として保存
            if os.getenv('GITHUB_ACTIONS'):
                with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                    f.write(f"tweet_id={response.data['id']}\n")
                    f.write(f"posted_at={datetime.now().isoformat()}\n")
            
            return True
        except Exception as e:
            print(f"❌ 投稿失敗: {e}")
            return False
    
    def post_random_tweet(self, reply_settings="mentionedUsers"):
        """
        ランダムに選んだツイートを投稿
        """
        templates = self.load_tweet_templates()
        content = self.create_tweet_content(templates)
        return self.post_tweet(content, reply_settings)


if __name__ == "__main__":
    # 環境変数からAPIキーを取得
    API_KEY = os.getenv('TWITTER_API_KEY')
    API_SECRET = os.getenv('TWITTER_API_SECRET')
    ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    # 必須環境変数のチェック
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("❌ Twitter APIの認証情報が設定されていません")
        exit(1)
    
    # リプライ設定を環境変数から取得（デフォルト: mentionedUsers = リプ欄実質クローズ）
    reply_settings = os.getenv('REPLY_SETTINGS', 'mentionedUsers')
    
    # 自動投稿システムを初期化
    bot = TwitterAutoPost(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    # ツイートを投稿
    success = bot.post_random_tweet(reply_settings=reply_settings)
    
    if success:
        print("✅ 処理完了")
        exit(0)
    else:
        print("❌ 処理失敗")
        exit(1)
