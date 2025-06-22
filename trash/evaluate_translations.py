# evaluate_translations.py

import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction

# punkt tokenizer 모델이 없으면 다운받습니다.
nltk.download('punkt', quiet=True)


def load_json(path: str) -> dict:
    """
    주어진 경로의 JSON 파일을 로드해서 반환합니다.
    """
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def evaluate(predicted_file: str) -> dict:
    """
    예측 JSON을 읽어서 Exact Match와 BLEU 점수를 출력하고,
    결과를 다음과 같은 딕셔너리로 반환합니다:
      {
        "total": int,
        "attempted": int,
        "skipped": int,
        "correct": int,
        "accuracy": float,
        "coverage": float,
        "bleu": float
      }
    """
    pred = load_json(predicted_file)

    golds = []       # BLEU용 gold 리스트
    hyps = []        # BLEU용 예측 리스트
    exact_count = 0
    attempted = 0
    skipped = 0

    test_list = pred.get('test', [])
    response_list = pred.get('response', [])
    total = len(test_list)
    min_len = min(len(test_list), len(response_list))

    for idx in range(min_len):
        test = test_list[idx]
        pred_item = response_list[idx]

        try:
            # 정상 형식: [정답 인덱스, 번역문]
            answer_idx = pred_item[0]
            hypothesis = pred_item[1].strip()
            gold = test[answer_idx].strip()

            # 번역이 영어가 아닌 원문 그대로인 경우 스킵
            if not any(c.isalpha() for c in hypothesis):
                skipped += 1
                continue

            attempted += 1

            # Exact Match
            if hypothesis == gold:
                exact_count += 1

            # BLEU 계산용 토큰화
            tokenized_gold = word_tokenize(gold)
            tokenized_hyp = word_tokenize(hypothesis)
            golds.append([tokenized_gold])
            hyps.append(tokenized_hyp)

        except Exception as e:
            print(f"[WARN] 예측 {idx}번 처리 중 오류: {e}")
            skipped += 1
            continue

    # BLEU 계산 (시도한 경우에 한해)
    smoothing = SmoothingFunction().method4
    bleu_score = corpus_bleu(golds, hyps, smoothing_function=smoothing) * 100 if hyps else 0.0

    # 정확도 및 커버리지 계산
    exact_acc = (exact_count / total * 100) if total else 0.0
    coverage = (attempted / total * 100) if total else 0.0

    # 콘솔 출력
    print(f"\n[Evaluation: {predicted_file}]")
    print(f"Total examples: {total}")
    print(f"Attempted translations: {attempted}")
    print(f"Skipped (untranslated or invalid): {skipped}")
    print(f"Exact Match: {exact_count}/{total} = {exact_acc:.2f}%")
    print(f"Coverage: {coverage:.2f}%")
    print(f"Corpus BLEU: {bleu_score:.2f}")

    return {
        "total": total,
        "attempted": attempted,
        "skipped": skipped,
        "correct": exact_count,
        "accuracy": round(exact_acc, 2),
        "coverage": round(coverage, 2),
        "bleu": round(bleu_score, 2)
    }
