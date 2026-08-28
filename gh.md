# gh 명령어 실행 기록

## 0-1. gh CLI 설치 (Ubuntu/Debian 기준)
```bash
sudo apt update
sudo apt install -y gh
```

## 0-2. gh 로그인 인증
```bash
gh auth login
```
    
## 1. gh 설치 여부 확인
```bash
which gh && gh --version
```

## 2. gh 로그인 사용자 확인
```bash
gh auth status
```

## 3. 내 repo 목록 5개 조회
```bash
gh repo list edumgt --limit 5
```

## 4. public 저장소 생성 (test1010)
```bash
gh repo create test1010 --public
```

## 5. repository Actions secret 생성 (test1111 repo, VVV=1111)
```bash
gh secret set vvv --body "1111" --repo edumgt/test1111
```

## 6. Codespaces에서 사용할 KRX secret 생성
```bash
gh secret set KRX_KEY --user --app codespaces
```

등록 후 Codespace를 새로 만들거나 다시 시작하면 애플리케이션이 `KRX_KEY` 환경변수에서 값을 읽습니다.

Codespaces secret의 값은 보안상 `gh secret`으로 다시 조회할 수 없습니다.

## 7. secret 목록 확인
```bash
gh secret list --repo edumgt/test1111
```
