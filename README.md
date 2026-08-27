# test1111

## test2222

## 기술 스택

- **Git / GitHub**: 버전 관리 및 원격 저장소 (`edumgt/test1111`)
- **GitHub CLI (`gh`)**: 저장소, secret 등 GitHub 리소스 관리 (사용법은 [gh.md](gh.md) 참고)
- **GitHub Actions**: CI 워크플로우 (`.github/workflows/test.yml`)

## GitHub Actions 상세

워크플로우 이름: `Test` (`.github/workflows/test.yml`)

### 트리거

| 이벤트 | 브랜치 | 설명 |
|---|---|---|
| `push` | `main` | main에 push될 때마다 실행 |
| `pull_request` | `main` | main 대상 PR 생성/갱신 시 실행 |
| `workflow_dispatch` | - | Actions 탭 또는 `gh workflow run`으로 수동 실행 |

### 권한

- `permissions: contents: write` — 워크플로우가 저장소에 커밋/푸시할 수 있도록 부여

### Job: `test` (`ubuntu-latest`)

1. **Checkout** — `actions/checkout@v4`로 저장소 코드 가져오기
2. **List repo files** — `ls -la`로 파일 목록 출력 (디버깅용)
3. **Print environment info** — `github.actor`, `github.ref_name`, `github.sha` 등 컨텍스트 값 출력
4. **Sanity check** — `README.md`, `gh.md` 존재 여부 확인
5. **Generate test.md** — 실행 번호, 트리거 이벤트, 액터, 브랜치, 커밋 SHA, 생성 시각을 담은 `test.md` 리포트 생성
6. **Commit and push test.md** — 변경된 `test.md`를 `github-actions[bot]` 계정으로 커밋 후 원격 저장소로 push
   - `pull_request` 이벤트에서는 이 단계를 건너뜀 (PR 컨텍스트는 push 권한이 제한적일 수 있음)
   - 커밋 메시지에 `[skip ci]`를 붙여 재귀 실행 방지 (GITHUB_TOKEN으로 만든 push는 기본적으로 워크플로우를 재트리거하지 않지만, 이중 안전장치로 추가)
   - 변경 사항이 없으면 커밋 없이 스킵

### 로컬에서 수동 실행

```bash
gh workflow run test.yml
gh run list --workflow test.yml
gh run view --log
```
