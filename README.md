# 📌 Google Order agent MCP Toolbox for CloudSQL
> CloudSQL 의 데이터를 에이전트가 조회, 변경하는 에이전트
> 
> 에이전트가 SQL 에 허용된 작업만 하도록 도구로 정의하는 Google 의 MCP Toolbox for Databases 를 사용

## ⚡ 주요 기능 (Features)
> 에이전트가 허용된 작업만 CloudSQL 에 진행

## 🛠 기술 스택 (Tech Stack)
- Google ADK, MCP Toolbox for Databases, MCP, Python

## 💻 시작 가이드 (Getting Started)
- Google Cloud 인증
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project ax-gemini-lab
```

- CloudSQL 및 DB 생성
```bash
export GOOGLE_CLOUD_PROJECT="프로젝트명"
export REGION=asia-northeast3
export DB_INSTANCE=shop-db-inst
export DB_NAME=shopdb
export DB_USER=postgres
export DB_PASSWORD='<강한 비밀번호>'

gcloud sql instances create $DB_INSTANCE \
  --database-version=POSTGRES_17 --edition=ENTERPRISE \
  --tier=db-custom-1-3840 --region=$REGION \
  --root-password="$DB_PASSWORD"
gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
```

- CloudSQL 에 테스트용 더미 데이터 입력
```bash
-- 상품(재고) 테이블
CREATE TABLE products (
  -- 자동 증가 기본키
  id SERIAL PRIMARY KEY,
  -- 상품 코드 (중복 불가)
  sku TEXT UNIQUE NOT NULL,
  -- 상품명
  name TEXT NOT NULL,
  -- 상품 분류
  category TEXT NOT NULL,
  -- 현재 재고 수량
  stock INT NOT NULL,
  -- 재주문 기준 수량 (재고가 이보다 적으면 부족)
  reorder_level INT NOT NULL
);

-- 주문 테이블
CREATE TABLE orders (
  -- 자동 증가 기본키
  id SERIAL PRIMARY KEY,
  -- 업무에서 쓰는 주문번호 (중복 불가)
  order_no TEXT UNIQUE NOT NULL,
  -- 고객사 이름
  customer_name TEXT NOT NULL,
  -- 주문 상품 (products.id 참조)
  product_id INT REFERENCES products(id),
  -- 주문 수량
  qty INT NOT NULL,
  -- 주문 상태, 기본값은 '접수'
  status TEXT NOT NULL DEFAULT '접수'
    -- 허용된 4개 값만 들어오게 하는 제약 (에이전트 실수에 대한 마지막 방어선)
    CHECK (status IN ('접수', '출고', '배송완료', '취소')),
  -- 주문 시각, 기본값은 현재 시각
  ordered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 실습용 상품 4개 입력
INSERT INTO products (sku, name, category, stock, reorder_level) VALUES
 -- 재고 12 < 기준 20 → 부족
 ('KB-100', '무선 키보드', '주변기기', 12, 20),
 -- 재고 충분
 ('MS-200', '인체공학 마우스', '주변기기', 85, 30),
 -- 재고 4 < 기준 10 → 부족
 ('MN-270', '27인치 모니터', '디스플레이', 4, 10),
 -- 재고 충분
 ('HD-050', '노이즈켄슬링 헤드셋', '오디오', 40, 15);

-- 실습용 주문 4건 입력 (상태를 다양하게 넣어 테스트 시나리오를 만듦)
INSERT INTO orders (order_no, customer_name, product_id, qty, status) VALUES
 -- 출고 처리 테스트용
 ('ORD-1001', 'A상사', 1, 5, '접수'),
 -- 이미 출고된 주문
 ('ORD-1002', 'A상사', 3, 2, '출고'),
 -- 변경 거부 테스트용 (배송완료)
 ('ORD-1003', 'B테크', 2, 20, '배송완료'),
 -- 허용되지 않은 상태값 테스트용
 ('ORD-1004', 'B테크', 4, 10, '접수');
```

- Google ADK 설치
```bash
python -m venv .venv && source .venv/bin/activate
pip install "google-adk[gcp]" litellm
```

- Toolbox 검증
```bash
cd toolbox
curl -O https://storage.googleapis.com/mcp-toolbox-for-databases/v1.1.0/linux/amd64/toolbox
chmod +x toolbox
./toolbox --config tools.yaml --enable-api      # 기본 포트 5000

# 다른 터미널에서 도구 목록 확인
curl http://127.0.0.1:5000/api/toolset
```

- ADK 검증 (Toolbox 검증 구동 후 별도의 터미널에서 확인)
```bash
adk web
127.0.0.1:8000
```

- Agent 검증
```bash
A 상사 주문 현황 알려줘 > search_orders 호출, 승인없이 실행
재고 부족 상품 있어? > 부족 수량 순으로 표시
ORD-1001 출고 처리해줘 > get_order 후 update_order_status 에서 승인 대화상자 표시 확인
```

- 검증 완료 후 Gemini Enterprise 에 에이전트로 등록
```bash
adk deploy agent_engine \
  --project="프로젝트명" \
  --region="리전명" \
  --display_name="에이전트명" \
  "에이전트 프로젝트 경로"
```
