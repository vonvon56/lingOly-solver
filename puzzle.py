# puzzle.py
import json, copy, re
from gpt_utils import gpt
from prompt_templates import SOLVER_PROMPT
class Puzzle:
    def __init__(self, path: str):
        data = json.load(open(path, encoding="utf8"))
        self.source = data["source_language"].capitalize()
        self.target = data["target_language"].capitalize()
        self.meta   = data["meta"]
        # train 데이터를 "소스 -> 타겟" 형식의 문자열로 변환
        self.train  = '\n'.join([f"{pair[0]} -> {pair[1]}" for pair in data["train"]])
        self.tests  = copy.deepcopy(data["test"])
        self.response = []
        # self.train_prompt = "\n".join(self.train)

    # 테스트 데이터를 문자열로 변환
    def render_tests(self):
        out = []
        for idx, row in enumerate(self.tests, 1):
            if row[2] == "<":
                out.append(f"translate \"{row[1]}\" into {self.source}.")
            else:
                out.append(f"translate \"{row[0]}\" into {self.target}.")
        return "\n".join(out)


    def get_answer(self, rules):
        """
        rules와 test 데이터를 받아 각 테스트에 대해 답을 생성한다.
        답 생성은 GPT api를 활용한다.
        """
        # 테스트 데이터를 JSON 형식으로 변환
        tests_json = json.dumps(self.tests, ensure_ascii=False, indent=2)
        
        # SOLVER_PROMPT 사용
        prompt = SOLVER_PROMPT.format(
            source=self.source,
            target=self.target,
            rules=rules,
            tests_json=self.render_tests()
        )
        print("최종 prompt에 rule 있나?", prompt)
        # GPT 호출
        rsp = gpt(prompt).choices[0].message.content.strip()
        
        # 응답을 줄바꿈으로 분리하여 각 테스트에 적용
        answers = rsp.split('\n')
        print('생 응답 보자', answers)
        for i, answer in enumerate(answers):
            if i < len(self.tests):
                if self.tests[i][2] == '>':
                    # [정답 index, 정답]
                    self.response.append([1, answer])
                else:
                    self.response.append([0, answer])
        print('리스폰스는?', self.response)

    def save(self, path: str):
        """
        puzzle 객체를 json 파일로 저장한다.
        """
        data = {
            "source_language": self.source,
            "target_language": self.target,
            "meta": self.meta,
            "train": self.train,
            "test": self.tests,
            "response": self.response
        }
        with open(path, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # def rule_parser(self, all_rules):
    #     answer = ""
    #     for rules in all_rules:
    #         temp = rules[0] + '\n' + rules[1]
    #     answer = answer + temp + '-------------'
    #     return answer
        
