import json
import openai
from app.core.config import REVIEW_LABELS, POLARITY_LABELS, OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

class LabelingService:
    def embed_and_label(self, text: str, mode: str):
        """
        텍스트를 KoSimCSE 임베딩 + OpenAI 라벨링으로 변환
        """
        target_word = "리뷰" if mode == "review" else "질문"

        prompt = f"""
        너는 리뷰 분석기야. {target_word} 문장을 보고 아래 후보 중 라벨과 polarity를 정해줘.
        라벨 후보: {", ".join(REVIEW_LABELS)}
        폴라리티 후보: {", ".join(POLARITY_LABELS)}
        출력 형식: JSON {{ "label": "...", "polarity": "..." }}
        {target_word}: {text}
        """

        resp = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        parsed = json.loads(resp.choices[0].message.content)
        return parsed["label"], parsed["polarity"]
