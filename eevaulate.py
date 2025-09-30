import os, csv
import json
import nltk
from nltk.translate.bleu_score import corpus_bleu
from sacrebleu.metrics import CHRF, TER          # ChrF++, TER
from typing import List

# ───────────────────────────────────────────────────────────
# 라이브러리 준비
# ───────────────────────────────────────────────────────────
nltk.download("punkt", quiet=True)
chrf = CHRF(word_order=2)        # ChrF++ 기본 = 6, 여기선 2도 OK
ter  = TER()

# ───────────────────────────────────────────────────────────
# 폴더 설정
# ───────────────────────────────────────────────────────────
DATASET_FOLDER = "PuzzLing_Experiment_Dataset"
OUTPUT_FOLDER  = "results/gpt-4o/notrepeat"

# 평균 계산용 누적 변수
sum_exact = sum_chrf = sum_cter = sum_bleu2 = 0.0
file_cnt  = 0

def cter_score(ref: str, hyp: str) -> float:
    """Character-level TER = edit distance / len(reference)."""
    import editdistance                     # pip install editdistance
    dist = editdistance.eval(ref, hyp)
    return 1.0 - dist / max(len(ref), 1)    # 1 – TER 형태로 반환(높을수록 좋음)

# ───────────────────────────────────────────────────────────
# 파일별 계산
# ───────────────────────────────────────────────────────────
for file_name in os.listdir(DATASET_FOLDER):
    gold, predicted = [], []

    # 1) gold 정답 추출
    with open(f"{DATASET_FOLDER}/{file_name}", encoding="utf-8") as f:
        data = json.load(f)
        for line in data.get("test", []):
            gold.append(line[1] if line[2] == '>' else line[0])

    # 2) 예측 결과 추출
    with open(f"{OUTPUT_FOLDER}/{file_name}", encoding="utf-8") as f:
        answer = json.load(f)['answer']
        predicted = answer.strip().split('\n')

    # 길이 맞추기
    n = len(gold)
    predicted = (predicted + [""]*n)[:n]

    # ── (1) Exact-match accuracy ───────────────────────────
    exact = sum(g == p for g, p in zip(gold, predicted)) / n

    # ── (2) ChrF (문서 수준) ───────────────────────────────
    chrf_score = chrf.corpus_score(predicted, [gold]).score / 100.0  # 0~1 스케일

    # ── (3) Character TER (편집거리 기반) ─────────────────
    cter_scores: List[float] = [cter_score(g, p) for g, p in zip(gold, predicted)]
    cter_avg = sum(cter_scores) / n  # 0~1 스케일 (높을수록 좋음)

    # ── (4) BLEU-2 (2-gram) ────────────────────────────────
    refs  = [[nltk.word_tokenize(g)] for g in gold]
    hyps  = [nltk.word_tokenize(p)   for p in predicted]
    bleu2 = corpus_bleu(refs, hyps, weights=(0.5, 0.5, 0, 0))

    # 결과 출력
    print(f"--- {file_name} ---")
    print(f"Exact Match : {exact:6.2%}")
    print(f"ChrF        : {chrf_score*100:6.2f}")
    print(f"CTER        : {cter_avg*100:6.2f}")
    print(f"BLEU-2      : {bleu2*100:6.2f}\n")

    # 평균용 누적
    sum_exact += exact
    sum_chrf  += chrf_score
    sum_cter  += cter_avg
    sum_bleu2 += bleu2
    file_cnt  += 1


# ───────────────────────────────────────────────────────────
# 전체 평균 계산
# ───────────────────────────────────────────────────────────
avg_exact = sum_exact / file_cnt
avg_chrf  = sum_chrf  / file_cnt
avg_cter  = sum_cter  / file_cnt
avg_bleu2 = sum_bleu2 / file_cnt

print("=== Averages over all files ===")
print(f"Exact Match : {avg_exact:6.2%}")
print(f"ChrF        : {avg_chrf*100:6.2f}")
print(f"CTER        : {avg_cter*100:6.2f}")
print(f"BLEU-2      : {avg_bleu2*100:6.2f}")

# 평균 결과 변수 사용
scores_file = "scores.csv"
folder_name = os.path.basename(OUTPUT_FOLDER)
metrics = ["Exact Match", "ChrF", "CTER", "BLEU-2"]
values = [avg_exact, avg_chrf, avg_cter, avg_bleu2]

# CSV에 저장하기
if os.path.exists(scores_file):
    with open(scores_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    header.append(folder_name)
    for i, row in enumerate(rows):
        row.append(f"{values[i]:.4f}")
    with open(scores_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
else:
    with open(scores_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", folder_name])
        for m, v in zip(metrics, values):
            writer.writerow([m, f"{v:.4f}"])

print(f"Summary saved to {scores_file}")