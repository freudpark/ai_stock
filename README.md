# AI Stock (PyhgoShift Edition)
> AI-Agent Based Global Trading Platform deployed on Cloudflare.

## 🚀 Deployment Guide

### 1. Backend (Cloudflare Workers - Python)
백엔드는 Cloudflare Workers의 최신 Python 런타임을 사용합니다.
- **경로**: `backend/`
- **배포 방법**:
  ```bash
  cd backend
  npx wrangler deploy
  ```
- **환경 변수 설정**: Cloudflare Dashboard에서 다음 Secret들을 설정하세요:
  - `KIS_API_KEY`
  - `KIS_API_SECRET`
  - `KIS_CANO` (계좌번호)
  - `KIS_ACNT_PRDT_CD` (상품코드, 보통 01)

### 2. Frontend (Cloudflare Pages)
프론트엔드는 고성능 React(Vite) 앱으로 설계되었습니다.
- **경로**: `frontend/`
- **배포 방법**: 
  - Github 저장소(`freudpark/ai_stock`)를 Cloudflare Pages에 연결하세요.
  - 빌드 설정:
    - **Framework Preset**: Vite
    - **Build command**: `npm run build`
    - **Output directory**: `dist`
  - 환경 변수: `VITE_API_URL`을 위에서 배포한 Workers의 URL로 설정하세요.

## 🎨 Design Philosophy
- **Nebula Dark Theme**: 프리미엄 다크 모드와 글래스모피즘 적용.
- **Micro-interactions**: 부드러운 애니메이션과 직관적인 신호 강도 시각화.
- **Global Support**: 한국 및 미국 주식 통합 인터페이스.

## 🛠 Tech Stack
- **Frontend**: Vite, React, Lucide-React, CSS3 (Glassmorphism)
- **Backend**: FastAPI, Cloudflare Workers (Python), KIS OpenAPI

---
**Maintained by The 7 Parks (PyhgoShift Digital Workforce)**
