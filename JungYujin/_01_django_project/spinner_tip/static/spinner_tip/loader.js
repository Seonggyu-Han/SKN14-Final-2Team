// 사용처에서: import { showDuring } from "/static/spinner_tip/loader.js";
async function fetchFact(endpoint = "/spinner-tip/fact/") {
  try {
    const r = await fetch(endpoint, { 
      headers: { 
        "X-Requested-With": "fetch",
        "Accept": "application/json"
      } 
    });
    
    if (!r.ok) {
      throw new Error(`HTTP ${r.status}`);
    }
    
    const j = await r.json();
    return j.fact; // 이모지는 템플릿에서 처리
  } catch (error) {
    console.warn("Failed to fetch perfume fact:", error);
    throw error;
  }
}

/**
 * 긴 작업 Promise를 받아, 대기 중에는 지식 문구를 표시하고
 * 완료되면 자동으로 감춥니다.
 *
 * @param {() => Promise<any>} taskFn  - 긴 작업(서버 호출 등)을 반환하는 함수
 * @param {string} boxId                - 로더 박스 element id
 * @param {string} factEndpoint         - JSON API endpoint
 */
export async function showDuring(taskFn, boxId = "spinner-tip-box", factEndpoint = "/spinner-tip/fact/") {
  const box = document.getElementById(boxId);
  if (!box) throw new Error(`loader box #${boxId} not found`);
  const textEl = box.querySelector(".loader-text");
  const iconEl = box.querySelector(".loader-icon");

  if (!textEl) throw new Error(`loader text element not found in #${boxId}`);

  // 먼저 로딩표시 → 지식 치환
  box.style.display = "block";
  textEl.textContent = "로딩 중...";
  
  // 지식 가져오기 (비동기)
  const factPromise = fetchFact(factEndpoint).catch(() => {
    return "향수의 지속력은 부향률만이 아니라 피부타입과 온도에도 좌우됩니다.";
  });

  // 지식 표시 (최대 1초 후)
  setTimeout(async () => {
    try {
      const fact = await factPromise;
      textEl.textContent = fact;
      if (iconEl) {
        iconEl.textContent = "💡";
        iconEl.style.animation = "pulse 2s infinite";
      }
    } catch (e) {
      console.warn("Failed to display perfume fact:", e);
    }
  }, 1000);

  try {
    const result = await taskFn();
    return result;
  } finally {
    box.style.display = "none";
  }
}
