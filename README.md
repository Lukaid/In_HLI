# In_HLI
time in HLI


## git 명령어 요약

 - clone: 원격 저장소(github)를 내 컴퓨터에 복사해 온다.
 - add: 내 컴퓨터에서 작업한 파일들을 stage에 추가
 - commit: stage에 올라온 파일들을 가지고 내 컴퓨터에 저장 (save와 비슷.)
 - push: commit들을 원격 저장소에 업로드
 - 코드 뭉치 버리기: 마지막 commit으로 되돌아가고 싶을 때 사용
    특정 파일의 내용을 마지막 commit으로 되돌리고 싶다면, 해당 파일을 선택 후 '코드 뭉치 버리기'를 선택
 - branch: 기능 변경을 하고 싶을 때 생성 및 사용
 - merge: 한 branch의 내용을 다른 branch에 반영
 - checkout: 저장소에서 특정 commit이나 branch로 돌아가고 싶을 때 사용


## branch 변경하기

 - branch란, 기존 내용을 유지하면서 새로운 내용을 추가하고 싶을때 사용한다.
 - checkout이란, 특정 branch(혹은 commit)으로 돌아가고 싶을 때 사용한다.
 - source_tree의 checkout은, branch의 이름을 더블클릭하는 것 만으로 checkout 가능.

 - main branch는 가장 기본 branch
 - 따라서 main branch에는 최종본이 들어가 있어야 한다.
 - 다른 branch에는 이것저것 시험해보고 main branch에 합침 (merge)