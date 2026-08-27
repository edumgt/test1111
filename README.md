# test1111

## test2222

## 기술 스택

- **Git / GitHub**: 버전 관리 및 원격 저장소 (`edumgt/test1111`)
- **GitHub CLI (`gh`)**: 저장소, secret 등 GitHub 리소스 관리 (사용법은 [gh.md](gh.md) 참고)
- **GitHub Actions**: CI 워크플로우 (`.github/workflows/test.yml`)
  - 실행 환경: `ubuntu-latest`
  - `actions/checkout@v4`로 코드 체크아웃
  - Bash 스크립트 기반 테스트/리포트 생성 단계
