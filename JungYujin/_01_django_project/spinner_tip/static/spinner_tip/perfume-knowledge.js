/**
 * 향수 지식 전달 시스템 - 전역 모듈
 * 어느 페이지에서든 쉽게 사용할 수 있는 향수 지식 로더
 */

class PerfumeKnowledgeLoader {
    constructor(options = {}) {
        this.defaultOptions = {
            boxId: 'perfume-knowledge-box',
            endpoint: '/spinner-tip/fact/',
            showDelay: 1000, // 1초 후 지식 표시
            fadeInDuration: 300,
            fadeOutDuration: 200,
            autoHide: true,
            position: 'center', // 'center', 'top', 'bottom'
            theme: 'default' // 'default', 'dark', 'minimal'
        };
        
        this.options = { ...this.defaultOptions, ...options };
        this.isVisible = false;
        this.currentTimeout = null;
        
        this.init();
    }

    init() {
        this.createLoaderBox();
        this.addStyles();
    }

    createLoaderBox() {
        // 이미 존재하는 경우 제거
        const existingBox = document.getElementById(this.options.boxId);
        if (existingBox) {
            existingBox.remove();
        }

        const box = document.createElement('div');
        box.id = this.options.boxId;
        box.className = `perfume-knowledge-box ${this.options.theme}`;
        box.style.display = 'none';
        
        box.innerHTML = `
            <div class="knowledge-content">
                <div class="knowledge-icon">💡</div>
                <div class="knowledge-text">로딩 중...</div>
                <div class="knowledge-progress">
                    <div class="progress-bar"></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(box);
        this.box = box;
    }

    addStyles() {
        if (document.getElementById('perfume-knowledge-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'perfume-knowledge-styles';
        style.textContent = `
            .perfume-knowledge-box {
                position: fixed;
                z-index: 10000;
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px 32px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                backdrop-filter: blur(12px);
                max-width: 450px;
                min-width: 300px;
                text-align: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                transform: translate(-50%, -50%);
            }

            .perfume-knowledge-box.center {
                top: 50%;
                left: 50%;
            }

            .perfume-knowledge-box.top {
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
            }

            .perfume-knowledge-box.bottom {
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
            }

            .knowledge-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 12px;
            }

            .knowledge-icon {
                font-size: 28px;
                animation: knowledgePulse 2s infinite;
            }

            .knowledge-text {
                font-size: 15px;
                line-height: 1.6;
                color: #333;
                font-weight: 500;
                margin: 0;
            }

            .knowledge-progress {
                width: 100%;
                height: 3px;
                background: rgba(0, 0, 0, 0.1);
                border-radius: 2px;
                overflow: hidden;
                margin-top: 8px;
            }

            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 2px;
                animation: progressMove 2s infinite;
                width: 0%;
            }

            @keyframes knowledgePulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.05); }
            }

            @keyframes progressMove {
                0% { width: 0%; }
                50% { width: 70%; }
                100% { width: 100%; }
            }

            /* 다크 테마 */
            .perfume-knowledge-box.dark {
                background: rgba(30, 30, 30, 0.95);
                border-color: #444;
                color: #fff;
            }

            .perfume-knowledge-box.dark .knowledge-text {
                color: #fff;
            }

            .perfume-knowledge-box.dark .knowledge-progress {
                background: rgba(255, 255, 255, 0.2);
            }

            /* 미니멀 테마 */
            .perfume-knowledge-box.minimal {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #ddd;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                padding: 16px 24px;
            }

            .perfume-knowledge-box.minimal .knowledge-icon {
                font-size: 20px;
            }

            .perfume-knowledge-box.minimal .knowledge-text {
                font-size: 14px;
            }

            .perfume-knowledge-box.minimal .knowledge-progress {
                display: none;
            }

            /* 모바일 대응 */
            @media (max-width: 480px) {
                .perfume-knowledge-box {
                    margin: 0 16px;
                    padding: 20px 24px;
                    max-width: calc(100vw - 32px);
                }
                
                .knowledge-text {
                    font-size: 14px;
                }
            }

            /* 페이드 인/아웃 애니메이션 */
            .perfume-knowledge-box.fade-in {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.9);
                animation: fadeInScale 0.3s ease-out forwards;
            }

            .perfume-knowledge-box.fade-out {
                animation: fadeOutScale 0.2s ease-in forwards;
            }

            @keyframes fadeInScale {
                to {
                    opacity: 1;
                    transform: translate(-50%, -50%) scale(1);
                }
            }

            @keyframes fadeOutScale {
                to {
                    opacity: 0;
                    transform: translate(-50%, -50%) scale(0.9);
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    async show(taskFn, customOptions = {}) {
        const options = { ...this.options, ...customOptions };
        
        if (this.isVisible) {
            console.warn('PerfumeKnowledgeLoader is already visible');
            return;
        }

        this.isVisible = true;
        this.box.style.display = 'block';
        this.box.classList.add('fade-in');
        
        // 로딩 텍스트 표시
        const textEl = this.box.querySelector('.knowledge-text');
        textEl.textContent = '로딩 중...';
        
        // 지식 가져오기
        const factPromise = this.fetchFact(options.endpoint);
        
        // 지연 후 지식 표시
        this.currentTimeout = setTimeout(async () => {
            try {
                const fact = await factPromise;
                textEl.textContent = fact;
            } catch (error) {
                console.warn('Failed to fetch perfume fact:', error);
                textEl.textContent = '향수의 지속력은 부향률만이 아니라 피부타입과 온도에도 좌우됩니다.';
            }
        }, options.showDelay);

        try {
            const result = await taskFn();
            return result;
        } finally {
            this.hide();
        }
    }

    async fetchFact(endpoint) {
        const response = await fetch(endpoint, {
            headers: {
                'X-Requested-With': 'fetch',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data.fact;
    }

    hide() {
        if (!this.isVisible) return;
        
        if (this.currentTimeout) {
            clearTimeout(this.currentTimeout);
            this.currentTimeout = null;
        }
        
        this.box.classList.remove('fade-in');
        this.box.classList.add('fade-out');
        
        setTimeout(() => {
            this.box.style.display = 'none';
            this.box.classList.remove('fade-out');
            this.isVisible = false;
        }, 200);
    }

    // 정적 메서드들
    static async show(taskFn, options = {}) {
        const loader = new PerfumeKnowledgeLoader(options);
        return await loader.show(taskFn);
    }

    static create(options = {}) {
        return new PerfumeKnowledgeLoader(options);
    }
}

// 전역에서 사용할 수 있도록 window 객체에 추가
window.PerfumeKnowledgeLoader = PerfumeKnowledgeLoader;

// 편의 함수들
window.showPerfumeKnowledge = PerfumeKnowledgeLoader.show;
window.createPerfumeKnowledgeLoader = PerfumeKnowledgeLoader.create;

// 자동 초기화 (DOM이 로드된 후)
document.addEventListener('DOMContentLoaded', () => {
    // 기본 로더 인스턴스 생성
    window.perfumeKnowledgeLoader = new PerfumeKnowledgeLoader();
});

export default PerfumeKnowledgeLoader;
