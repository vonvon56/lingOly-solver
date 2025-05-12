# logger.py
import json
import os
from datetime import datetime

def log_gpt_response(prompt: str, response: str, agent_type: str, iteration: int = None):
    """
    GPT 응답을 로깅하는 함수
    
    Args:
        prompt (str): GPT에 전달된 프롬프트
        response (str): GPT의 응답
        agent_type (str): 에이전트 타입 (예: grammar_WordOrderAgent, verifier_VerifierAgent)
        iteration (int, optional): 현재 반복 횟수
    """
    # logs 디렉토리가 없으면 생성
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 현재 시간을 파일명에 포함
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'logs/gpt_log_{agent_type}_{timestamp}.json'
    
    # 로그 데이터 구성
    log_data = {
        'timestamp': timestamp,
        'agent_type': agent_type,
        'iteration': iteration,
        'prompt': prompt,
        'response': response
    }
    
    # JSON 파일로 저장
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2) 