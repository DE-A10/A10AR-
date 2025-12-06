import uvicorn
import random
from fastapi import FastAPI

# --- 緊急用サーバー設定 ---
app = FastAPI(title="【緊急用】帽子推薦モックサーバー")

# --- 判定ロジック (本番と同じ基準) ---
def score_to_star(score: float) -> dict:
    if score >= 0.90: star = 5
    elif score >= 0.85: star = 4
    elif score >= 0.70: star = 3
    elif score >= 0.50: star = 2
    else: star = 1
    
    star_str = "★" * star + "☆" * (5 - star)
    return {"rating": star, "display": star_str}

# --- ダミーデータ定義 ---
DUMMY_HATS = [
    {"id": 1, "name": "レッドキャップ"},
    {"id": 2, "name": "ストローハット"},
    {"id": 3, "name": "ブラックバケット"},
    {"id": 4, "name": "ウールベレー"},
    {"id": 5, "name": "ニットビーニー"},
    {"id": 6, "name": "中折れハット"},
    {"id": 7, "name": "ハンチング"},
]

# ==========================================
# 1. 推薦リスト取得 (ランキング形式)
# ==========================================
@app.get("/recommendations/{user_id}", summary="【モック】似合い度リスト取得")
async def get_mock_recommendations(user_id: int):
    # ユーザーIDを種にして、毎回同じ結果が出るように固定する
    random.seed(user_id) 
    
    # 帽子をランダムに並び替える
    shuffled_hats = random.sample(DUMMY_HATS, len(DUMMY_HATS))
    
    results = []
    
    # 上から順に高いスコアを割り当てる
    for i, hat in enumerate(shuffled_hats):
        # 1位は0.98, 2位は0.88... とスコアを作る
        base_score = 0.98 - (i * 0.12)
        # 少しゆらぎを与える
        variation = random.uniform(-0.02, 0.02)
        dummy_score = base_score + variation
        
        # 範囲調整
        if dummy_score < 0.1: dummy_score = 0.1
        if dummy_score > 0.99: dummy_score = 0.99

        star_info = score_to_star(dummy_score)
        
        results.append({
            "hat_id": hat["id"],
            "hat_name": hat["name"],
            "S_final": round(dummy_score, 4),
            "star_rating": star_info["rating"],
            "star_display": star_info["display"]
        })

    # スコアが高い順にソートして返す
    sorted_results = sorted(results, key=lambda x: x["S_final"], reverse=True)
    return {"recommendations": sorted_results}


# ==========================================
# 2. 単体スコア取得 (帽子を選んだ時用)
# ==========================================
@app.get("/recommendations/{user_id}/hat/{hat_id}", summary="【モック】単体似合い度取得")
async def get_mock_single_hat_score(user_id: int, hat_id: int):
    # 帽子名を探す
    target_hat = next((h for h in DUMMY_HATS if h["id"] == hat_id), {"name": f"帽子{hat_id}"})
    
    # ユーザーIDと帽子IDの組み合わせで乱数を固定
    random.seed(user_id + hat_id * 100)
    
    # スコア生成
    dummy_score = random.uniform(0.1, 0.99)
    
    # ★演出用設定 (任意)
    # 「User 1 が 帽子 1 を選んだら絶対に★5にする」などの演出
    if user_id == 1 and hat_id == 1:
        dummy_score = 0.95

    star_info = score_to_star(dummy_score)

    return {
        "hat_id": hat_id,
        "hat_name": target_hat["name"],
        "S_final": round(dummy_score, 4),
        "star_rating": star_info["rating"],
        "star_display": star_info["display"]
    }

# ==========================================
# 3. ダミーの登録・フィードバック (エラーを出さないためだけのエンドポイント)
# ==========================================
@app.post("/users/register/")
async def mock_register_user():
    return {"message": "ユーザー登録成功(モック)", "user_id": 1, "V_user_impression": [0.5, -0.5]}

@app.post("/feedback/")
async def mock_feedback():
    return {"message": "フィードバック保存成功(モック)"}


# サーバー実行 (ポート 8002 で起動)
if __name__ == "__main__":
    print("--- 【緊急用】モックサーバーを起動します ---")
    print("URL: http://127.0.0.1:8002/docs")
    # 本番と被らないポート(8002)で起動
    uvicorn.run(app, host="127.0.0.1", port=8002)