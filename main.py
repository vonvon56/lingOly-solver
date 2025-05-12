# main.py
import json, os
from tqdm import tqdm
from puzzle import Puzzle
from agents import GrammarAgent, VerifierAgent, MAX_AGENT_ITER
from gpt_utils import gpt
from prompt_templates import AGENT_SELECTION_PROMPT
from logger import log_gpt_response

DATASET_FOLDER = "Experiment_Dataset"
# file_path = "b1886646ac3f6e86da88a9b743a52e960849f488b9e04c65d7371394d631da61.json"

def select_agents(puzzle, temperature=0.5) -> list:
    prompt = AGENT_SELECTION_PROMPT.format(
        meta=puzzle.meta,
        source=puzzle.source,
        target=puzzle.target,
        train=puzzle.train,
    )
    # print(prompt)
    rsp = gpt(prompt, temp=temperature).choices[0].message.content
    print("<select agents>\n", rsp)
    log_gpt_response(prompt, rsp, "agent_selection")
    
    try:
        names = rsp.split("\n")
    except json.JSONDecodeError:
        names = ["GrammarAgent", "VerifierAgent"]  # fallback 가정
    agent_objs = []
    for name in names:
        print(name)
        try:
          agent_objs.append(GrammarAgent(name))
        except:
            print(f"[WARN] Unknown agent {name}, skipped.")
    return agent_objs

def run_pipeline(puzzle_path: str, temperature=0.5):
    puzzle = Puzzle(puzzle_path)
    agents = select_agents(puzzle, temperature=temperature)
    all_rules = ""  # 빈 문자열로 초기화
    history = [] # 각 반복에서 규칙과 검증 결과를 저장


    for agent in agents:
        grammar_agent = agent
        print("현재 agent", grammar_agent.name)
        all_rules += grammar_agent.name + '\n'
        rules = grammar_agent.run(puzzle, temperature=temperature)
        all_rules += rules

        verifier_agent = VerifierAgent(grammar_agent.name)    
        for i in range(MAX_AGENT_ITER):
            print(f"\n=== Verification Iteration {i+1} : {agent.name} ===")
            rules, verified = verifier_agent.run(puzzle, rules, temperature=temperature, iteration=i+1)
            history.append({"rules": rules, "verified": verified})
            print("verified: ", verified)
            if verified == 3:
                break
        # 마지막 verification rule이 들어가도록. 
        all_rules += rules + "\n----------------\n"
        print('아니 되긴 하는 거임?', all_rules)

    # 규칙 적용 & 출력
    print("all_rules!!", all_rules)
    puzzle.get_answer(all_rules)

    # ✅ 디렉토리 없으면 자동 생성
    os.makedirs("rules", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # 파일 이름 추출 (확장자 제거)
    base_filename = os.path.splitext(os.path.basename(file_path))[0]

    # all_rules 저장
    rules_output_path = f"rules/{base_filename}.txt"
    with open(rules_output_path, "w", encoding="utf-8") as f:
        f.write(all_rules)
        
    # 정답 저장
    puzzle.save(f"outputs/{base_filename}_answer.json")
    print("\n=== FINAL RULES & VERIFICATION ===")
    for idx, h in enumerate(history, 1):
        print(f"{idx}. rules: {h['rules']} | verified: {h['verified']}")
    print("\n=== FINAL ANSWERS ===")
    for line in puzzle.render_tests().splitlines():
        print(line)

# if __name__ == "__main__":
#     run_pipeline(f"Experiment_Dataset/{file_path}", temperature=0.5)
if __name__ == "__main__":
    for file_name in os.listdir(DATASET_FOLDER):
        if file_name.endswith(".json"):
            file_path = os.path.join(DATASET_FOLDER, file_name)
            run_pipeline(file_path, temperature=0.5)