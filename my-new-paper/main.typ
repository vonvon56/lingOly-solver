// #set document.paragraph-indent: 0pt

// This is a minimal starting document for tracl, a Typst style for ACL.
// See https://github.com/coli-saar/tracl for details.
// 
#import "@preview/tracl:0.6.1": *

#show: doc => acl(doc,
  anonymous: false,
  title: [A Blank ACL Paper],
  authors: (
    (
      name: "Gyeongseo Hwang",
      affiliation: [Department of Linguistics
      
      2023-10775 
      ],
      email: "rudtj0801@snu.ac.kr",
    ),
  ),
)


#abstract[
  table of contents
]


= Introduction 
The central question of this paper is whether LLMs are merely probabilistic machines based on statistical patterns, or whether they can truly infer linguistic rules. Traditional linguistic theories, particularly generative grammar, have characterized language as a system composed of symbolic elements and explicit rules. In contrast, LLMs operate without explicit rules, instead learning context-dependent probability distributions through the optimization of a vast number of parameters.

This raises the question of whether such models can effectively capture the rule-governed nature of human language—particularly its compositionality and capacity for generalization. Understanding the generalization capabilities and limitations of LLMs can not only help to illuminate the internal mechanisms of these black-box models, but also offer a valuable theoretical framework for exploring the cognitive underpinnings of human linguistic competence@hasson2022. \ djWJrh 





전문적인 Large Reasoning Model의 추론 능력조차 일정 난도 이상의 task에서는 collapse하기도 했다. @illusion-of-thinking 


= Related Work
아직까지 언어학 올림피아드를 중점적으로 다룬 AI 논문과 데이터셋은 많지 않다. LINGOLY 데이터셋은 90여 개의 저자원 언어를 포함하는 challenging Linguistic Olympiad puzzle이다@bean2024lingolybenchmarkolympiadlevellinguistic. PuzzLing이라는, Linguistic Olympiad에 기반한 Rosetta Stone 데이터셋이 존재한다@sahin-etal-2020-puzzling. 

한편, PuzzLing dataset에서 Tree-of-Thoughts 기법과 Standard I/O의 성능을 비교한 선행연구가 있다@lin-etal-2023-solving. input 문장에 가능한 영어 해석이 3가지 뻗어나오고, 다음 step에서 그것의 가능성을 Sure, Maybe, Impossible로 분류한다.  이 연구는 Tree-of-Thoughts를 적용했을 때 Standard I/O보다 오히려 성능이 낮아졌음을 보고하였고, 이유를 아래와 같이 추정하였다.
1. 프롬프트의 정확성: 프롬프트가 충분히 정확하지 않아 LLM이 혼동함
2. 평가 방법의 민감도: 현재 평가 방법이 새로운 후보 해결책으로 인해 발생하는 모순을 제대로 감지하지 못했을 수 있음
3. LLM의 능력: GPT-3.5-Turbo를 사용했는데, ToT의 연산량을 감당하기에는 성능이 부족했을 수 있음
4. ToT 구조의 적합성: ToT가 언어학 문제 해결에 적합하지 않을 수 있음. 즉, 언어규칙 추론에는 문제를 부분적으로 해결하는 것보다 전체적인 패턴 분석이 더 중요할 수 있음

따라서, 본 연구에서는 전체적 패턴을 분석하되 ToT보다 반복 횟수와 input length를 줄이는 방안을 모색한다.
= Method
#figure(image("Figure 2-corpus and rules.png"), caption: [Example of corpus and rules. corpus는 low-resource language:English의 형식이다.]) <figure1>

corpus와 rules, 두 가지 요소를 도입하여 문제를 전체적으로 조망하고자 했다. corpus는 예문에 등장한 단어들의 뜻을 정리한 것이며, rules은 주어진 예문을 잘 설명할 수 있는 규칙들의 목록이다. @figure1 에서  형식을 확인할 수 있다. Bean et al. (2024)에서는 가능한 여러 번역의 validity를 계산하지만, 그 방법은 도출 과정을 명시적으로 설명하지 못하는 임의적인 부분이 있을 것이라 생각하였다. 그래서 rules을 추출하고, 기존 연구에 없던 요소인 corpus를 새로 도입했다. 이는 인간의 언어 사용 양상에서 착안한 것으로, 원어민 수준이 아니라면 언어 학습/문장 생성에 있어 어휘가 중요하다고 보았기 때문이다. 또한 pilot test에서 아예 단어 자체를 채우지 못하는 경우가 많았기에 단어 의미를 매칭한 corpus를 넣어주면 성능이 향상될 것으로 보았다.

다음으로, '반복과 갱신'이 rule과 corpus를 개선하는 효과가 있는지 살펴보기 위해 2가지 구조를 설계했다. 본 연구에서는 ToT보다 연산량을 줄인 반복 갱신 method와 반복 없는 method의 성능을 비교할 것이다. 그럼으로써 LLM에 자신의 출력을 갱신하는 능력이 있는지 알아볼 것이다. 
또한 GPT-3.5-Turbo와 GPT-4o에서 각각 반복했을 때와 그렇지 않을 때를 비교하여 반복 방식의 성능 부진이 LLM의 capacity(연산량) 때문인지 알아볼 것이다.

#figure(image("Figure 1-architecture 1 explanation.png"), caption:[반복 architecture])

#figure(image("Figure 3-architecture 2 explanation.png"), caption: [반복하지 않는 architecture])



= Dataset
LINGOLY 데이터셋으로 분석한다. (설명 붙여넣기)
PuzzLing은 부록으로 수록한다. \ 
PuzzLing dataset은 LINGOLY에 비해 난도가 높은 편이지만, 정답 공개된 것이 10개뿐이고 나머지의 성능은 대시보드로만 확인할 수 있다. 그 결과는 하단에 첨부할 예정이다.
= Experiments

= Results
필요한 Figures
반복: yes, no
실험할 모델: gpt-3.5-turbo, gpt-4o
  근데 rule, corpus, rule+corpus 비교는 3.5로.

prompt 조합: rule only, corpus only, rule+corpus, 그냥 one-shot
3.5 vs. 4o 비교: one-shot & rule+corpus
example: yes, no

// 실험1
3.5: 반복o구조{rule, corpus, rule+corpus, one-shot}
     반복x{rule, corpus, rule+corpus, one-shot}


= Analysis
== rule 추출보다 corpus 추출의 효과가 더 크다. -> rule 추출은 어려운 반면 corpus는 비교적 잘한다?
필요한 것
3.5 반복x: rule, corpus, rule+corpus, one-shot

== Tree-of thought 방식은 효과가 없다.
그냥 PuzzLing 한번 돌렸던 거 그대로 내자. 
== LLM은 자신의 출력을 수정하고 검증하지 못한다. 
3.5: 반복o rule, corpus, rule+corpus, one-shot 
3.5  반복x  그대로 . 
== 문제에서 주어진 예문을 결과에 다시 한 번 통합해서 넣어주면 더 잘함
3.5: 반복x, rule+corpus+예문
4o: 반복x, rule+corpus+예문
== 번외 실험: 반복에서 모델 번갈아가며 test. gpt 3.5-gpt4o-3.5.그 반대 순서도. 
= Conclusion
jjj

// Uncomment this to include your bibliography


// #import "@preview/blinky:0.2.0": link-bib-urls
// #let bibsrc = read("custom.bib")

// #link-bib-urls()[
//    #bibliography("custom.bib", style: "./association-for-computational-linguistics-blinky.csl")
// ]

= References

#bibliography("refs.bib", style: "chicago-author-date")
