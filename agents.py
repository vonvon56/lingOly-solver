# agents.py
from abc import ABC, abstractmethod
from gpt_utils import gpt
from prompt_templates import GRAMMAR_PROMPT, VERIFIER_PROMPT
import re 
from logger import log_gpt_response

MAX_AGENT_ITER = 3   # 그림의 '5회까지 반복'

class Agent(ABC):
    """모든 Agent의 공통 인터페이스"""
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, puzzle, rules, temperature=0.5, iteration=None) -> list[str]:
        """규칙 목록을 업데이트해서 반환"""
        raise NotImplementedError


class GrammarAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.name = name

    def run(self, puzzle, temperature=0.5, iteration=None):
        prompt = GRAMMAR_PROMPT.format(
            name=self.name,
            source=puzzle.source,
            target=puzzle.target,
            meta=puzzle.meta,
            train=puzzle.train,
            tests=puzzle.render_tests()
        )
        # print("grammar prompt", prompt)
        rsp = gpt(prompt, temp=temperature).choices[0].message.content
        print("<grammar rsp>\n", rsp)
        log_gpt_response(prompt, rsp, f"grammar_{self.name}", iteration)
        
        return rsp


class VerifierAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.name = name

    def run(self, puzzle, rules, temperature=0.5, iteration=None):
        prompt = VERIFIER_PROMPT.format(
            name=self.name,
            source=puzzle.source,
            target=puzzle.target,
            meta=puzzle.meta,
            tests=puzzle.render_tests(),
            rules=rules
        )
        # print("verifier prompt", prompt)
        rsp = gpt(prompt, temp=temperature).choices[0].message.content
        print("<verifier rsp>\n", rsp)
        log_gpt_response(prompt, rsp, f"verifier_{self.name}", iteration)
        lines = rsp.strip().splitlines()
    
        # 마지막 줄에서 검증 결과(0,1,2,3) 추출
        verified = None
        if lines:
            try:
                verified = int(lines[-1])
            except ValueError:
                verified = None
        return "\n".join(lines[:-2]), verified
