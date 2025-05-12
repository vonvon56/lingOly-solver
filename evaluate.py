# evaluate.py
import os
import csv
from evaluate_translations import evaluate  # evaluate()가 dict를 반환한다고 가정

OUTPUT_DIR = "outputs"
CSV_PATH = "evaluation_results.csv"

def main():
    results = []

    # outputs 폴더 내 모든 *_answer.json 파일 평가
    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith("_answer.json"):
            filepath = os.path.join(OUTPUT_DIR, filename)
            print(f"[Evaluating] {filename}")
            result = evaluate(filepath)

            if isinstance(result, dict):
                result["file"] = filename
                results.append(result)
            else:
                print(f"[WARN] 평가 결과가 dict가 아닙니다: {result}")

    # 결과를 CSV로 저장
    if results:
        # 전체 키셋을 모아서 fieldnames 구성 (file 포함)
        all_keys = set()
        for r in results:
            all_keys.update(r.keys())
        fieldnames = sorted(all_keys)

        with open(CSV_PATH, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                extrasaction='ignore',  # dict에 없는 키는 무시
            )
            writer.writeheader()
            for row in results:
                # 누락된 키는 빈 문자열로 채워서 안전하게 출력
                complete_row = {key: row.get(key, "") for key in fieldnames}
                writer.writerow(complete_row)

        print(f"\n✅ 평가 결과가 {CSV_PATH}에 저장되었습니다.")
    else:
        print("❌ 저장할 평가 결과가 없습니다.")

if __name__ == "__main__":
    main()
