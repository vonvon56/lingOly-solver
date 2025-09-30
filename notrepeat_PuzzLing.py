# main.py – rebuilt around INITIAL_GRAMMAR_PROMPT / GRAMMAR_PROMPT / SOLVER_PROMPT
# ==================================================================================
# 주요 변경점
# ----------------------------------------------------------------------------------
# 1. 초기 코퍼스‧규칙 생성 → **INITIAL_GRAMMAR_PROMPT**  (훈련 샘플 절반 사용)
# 2. 나머지 샘플을 하나씩 추가 → **GRAMMAR_PROMPT** 로 코퍼스/규칙 확장
# 3. 모든 훈련 샘플 반영 후 → **SOLVER_PROMPT** 로 테스트 세트 번역(정답 예측)
# 4. 사용자가 건드리지 말라고 지정한 결과 저장 블록은 그대로 둠
# ----------------------------------------------------------------------------------

import json
import os
import re
from typing import List, Tuple

from tqdm import tqdm

from puzzle import Puzzle
from gpt_utils import gpt
from prompt_templates import (
    INITIAL_GRAMMAR_PROMPT,
    GRAMMAR_PROMPT,
    SOLVER_PROMPT,
)
from logger import log_gpt_response

# ---------------------------------------------------------------------------
# 응답 블록 추출 및 검증
# ---------------------------------------------------------------------------

def extract_blocks(text: str) -> Tuple[str, str]:
    # [corpus] 블록: [corpus] 다음부터 [rules] 직전까지
    c_re = re.compile(r"\[corpus\]\s*(.*?)\s*(?=\[rules\])", re.I | re.S)
    # [rules] 블록: [rules] 이후 끝까지
    r_re = re.compile(r"\[rules\]\s*(.*)$", re.I | re.S)

    cm, rm = c_re.search(text), r_re.search(text)
    if not cm or not rm:
        print(text)
        raise ValueError("CORPUS/RULES 블록 미발견")
    return cm.group(1).strip(), rm.group(1).strip()


def keeps_previous(prev: str, new: str) -> bool:
    return new.strip().startswith(prev.strip())

# ---------------------------------------------------------------------------
# LLM 프롬프트 호출
# ---------------------------------------------------------------------------

def call_initial_prompt(
    source_lang: str,
    target_lang: str,
    meta: str,
    sample_pairs: List[Tuple[str, str]],
    temperature=0.5,
):
    pairs_text = "\n".join(f"{s} ||| {t}" for s, t in sample_pairs)
    prompt = INITIAL_GRAMMAR_PROMPT.format(
        source=source_lang,
        target=target_lang,
        meta=meta,
        pairs=pairs_text,
    )
    log_json['initial prompt'] = prompt
    rsp = gpt(prompt, temp=temperature).choices[0].message.content
    # print(rsp)
    return extract_blocks(rsp)


def call_extend_prompt(
    source_lang: str,
    target_lang: str,
    meta: str,
    current_corpus: str,
    current_rules: str,
    pairs: List[Tuple[str, str]],
    temperature=0.5,
):
    pairs_text = "\n".join(f"{s} ||| {t}" for s, t in pairs)
    # pair_line = f"{new_pair[0]} ||| {new_pair[1]}"
    prompt = GRAMMAR_PROMPT.format(
        source=source_lang,
        target=target_lang,
        meta=meta,
        corpus=current_corpus,
        rules=current_rules,
        pairs=pairs_text,
    )
    # log_json[f'extended prompt {len(pair_line)}'] = prompt
    rsp = gpt(prompt, temp=temperature).choices[0].message.content
    return extract_blocks(rsp)


def call_solver_prompt(
    source_lang: str,
    target_lang: str,
    meta: str,
    train_pairs: str, 
    current_corpus: str,
    current_rules: str,
    test_src: str,
    temperature=0.5,
):
    train_pairs = "\n".join(f"{s} ||| {t}" for s, t in train_pairs)
    prompt = SOLVER_PROMPT.format(
        source=source_lang,
        target=target_lang,
        meta=meta,
        corpus=current_corpus,
        train_pairs=train_pairs,
        rules=current_rules,
        tests=test_src,
    )
    # print(prompt)
    rsp = gpt(prompt, temp=temperature).choices[0].message.content
    log_json['answer'] = rsp
    
    return rsp
# test용 문자열 생성
def render_tests(data, src_lang, tgt_lang):
    out = []
    for idx, row in enumerate(data, 1):
        if row[2] == "<":
            out.append(f"translate \"{row[1]}\" into {src_lang}.")
        else:
            out.append(f"translate \"{row[0]}\" into {tgt_lang}.")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 코퍼스/규칙 구축 로직
# ---------------------------------------------------------------------------

def build_corpus_and_rules(
    source_lang: str,
    target_lang: str,
    meta: str,
    train_pairs: List[Tuple[str, str]],
    temperature=0.5,
) -> Tuple[str, str]:
    # pivot = len(train_pairs) // 2
    # 초기 프롬프트
    # pairs = train_pairs[:pivot]
    pairs = train_pairs
    corpus, rules = call_initial_prompt(
        source_lang, target_lang, meta, pairs, temperature
    )
    log_json['initial corpus'] = corpus
    log_json['initial rules'] = rules
    
    # 확장
    # for idx, pair in enumerate(train_pairs[pivot:]):
    #     try:
    #         pairs.append(pair)
    #         nc, nr = call_extend_prompt(
    #             source_lang,
    #             target_lang,
    #             meta,
    #             corpus,
    #             rules,
    #             pairs,
    #             temperature,
    #         )

    #     except ValueError:
    #         continue

    #     corpus, rules = nc, nr
    #     log_json[f'extended corpus {idx+1}'] = corpus
    #     log_json[f'extended rules {idx+1}'] = rules
        
    #     # retries += 1
    return corpus, rules

# ---------------------------------------------------------------------------
# 파이프라인
# ---------------------------------------------------------------------------

def run_pipeline(json_path: str, temperature=0.5):
    global log_json
    log_json = {}

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    src_lang = data.get("source_language", "")
    tgt_lang = data.get("target_language", "")
    meta = data.get("meta", "")
    train_pairs = [(s, t) for s, t in data.get("train", [])]
    test_src = render_tests(data.get("test", ""), src_lang, tgt_lang)
    corpus, rules = build_corpus_and_rules(
        src_lang, tgt_lang, meta, train_pairs, temperature
    )
    print(test_src)
    # corpus = ""
    # rules = ""
    answer = call_solver_prompt(
        src_lang, tgt_lang, meta, train_pairs, corpus, rules, test_src, temperature
    )
    ans_list = answer.split('\n')
    with open(f'{DATASET_FOLDER}/{fname}', "r", encoding="utf-8") as f:
        data = json.load(f)

    # 3) data["test"] 리스트의 각 항목[1]에 대답 채워넣기
    #    test 항목이 [[src, "", ">"], ["", tgt, "<"], …] 형태라고 가정
    #    ans_list 순서대로 매핑합니다.
    for i, entry in enumerate(data["test"]):
        # entry[1] 이 비어 있으면(번역해야 할 자리)
        if entry[2] == ">":
            try:
                data["test"][i][1] = ans_list.pop(0)
            except IndexError:
                # ans_list 가 모자랄 때
                data["test"][i][1] = "<unk>"
        else:
            try:
                data["test"][i][0] = ans_list.pop(0)
            except IndexError:
                # ans_list 가 모자랄 때
                data["test"][i][0] = "<unk>"

    # 4) 수정한 data 를 다시 덮어쓰기 (UTF-8, ensure_ascii=False)
    # with open(f'{DATASET_FOLDER}/{fname}', "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)
    return answer


# ---------------------------------------------------------------------------
# 진입점
# ---------------------------------------------------------------------------

global DATASET_FOLDER
DATASET_FOLDER = "PuzzLing_Experiment_Dataset"

if __name__ == "__main__":
    output_dir = "results/gpt-4o/notrepeat"
    # 결과 저장 폴더가 없으면 생성
    os.makedirs(output_dir, exist_ok=True)

    for fname in tqdm(os.listdir(DATASET_FOLDER), desc="Processing datasets"):
        if not fname.lower().endswith(".json"):
            continue

        print(f"\n=== {fname} ===")
        answer = run_pipeline(os.path.join(DATASET_FOLDER, fname), temperature=0.5)

        out_path = os.path.join(output_dir, fname)
        with open(out_path, "w", encoding="utf-8") as f:
            # ensure_ascii=False: 한글이 깨지지 않게
            # indent=4: 사람이 읽기 좋게 들여쓰기
            json.dump(log_json, f, ensure_ascii=False, indent=4)
