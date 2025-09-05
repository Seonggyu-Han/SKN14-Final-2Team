/**
 * 향상된 향수 지식 로더 시스템
 * - 원형 프로그레스 바
 * - 동적 로딩 텍스트
 * - LLM 응답 대기 모드
 * - 완전 모듈화
 */

class EnhancedPerfumeLoader {
    constructor(options = {}) {
        this.defaultOptions = {
            boxId: 'enhanced-perfume-loader',
            endpoint: '/spinner-tip/fact/',
            position: 'center',
            theme: 'default',
            showProgress: true,
            showLoadingText: true,
            progressDuration: 30000, // 30초 기본값 (LLM 응답 시간)
            factChangeInterval: 3000, // 3초마다 지식 변경
            autoHide: true
        };
        
        this.options = { ...this.defaultOptions, ...options };
        this.isVisible = false;
        this.progressInterval = null;
        this.factInterval = null;
        this.currentProgress = 0;
        this.facts = [];
        this.currentFactIndex = 0;
        
        this.init();
    }

    init() {
        this.createLoaderBox();
        this.addStyles();
        this.preloadFacts();
    }

    async preloadFacts() {
        try {
            // 여러 향수 지식을 미리 로드
            for (let i = 0; i < 5; i++) {
                const response = await fetch(this.options.endpoint);
                const data = await response.json();
                this.facts.push(data.fact);
                // 요청 간격을 두어 서버 부하 방지
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        } catch (error) {
            console.warn('Failed to preload facts:', error);
            this.facts = [
                '향수의 첫인상은 톱 노트, 그 다음이 미들 노트, 마지막이 베이스 노트입니다.',
                '향수의 지속력은 부향률만이 아니라 피부타입과 온도에도 좌우됩니다.',
                '시향할 때는 손목에 뿌리고 체취와 어우러지는지 확인하는 것이 중요합니다.',
                '향수는 햇빛과 고온을 피해 어둡고 서늘한 곳에 보관하는 것이 좋습니다.',
                '한 번에 3-4개 이상의 향수를 시향하면 후각이 둔해집니다.'
            ];
        }
    }

    createLoaderBox() {
        // 기존 로더가 있으면 제거
        const existingBox = document.getElementById(this.options.boxId);
        if (existingBox) {
            existingBox.remove();
        }

        const box = document.createElement('div');
        box.id = this.options.boxId;
        box.className = `enhanced-perfume-loader ${this.options.theme} ${this.options.position}`;
        box.style.display = 'none';
        
        box.innerHTML = `
            <div class="loader-content">
                <div class="progress-container">
                    <svg class="progress-ring" width="80" height="80">
                        <circle class="progress-ring-bg" cx="40" cy="40" r="35"></circle>
                        <circle class="progress-ring-fill" cx="40" cy="40" r="35"></circle>
                    </svg>
                    <div class="progress-icon">💡</div>
                    <div class="progress-text">0%</div>
                </div>
                <div class="loading-status">
                    <div class="status-text">로딩 중...</div>
                    <div class="knowledge-text">향수 지식을 불러오는 중...</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(box);
        this.box = box;
        this.setupProgressRing();
    }

    setupProgressRing() {
        const circle = this.box.querySelector('.progress-ring-fill');
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = circumference;
        this.circumference = circumference;
    }

    updateProgress(percent) {
        const circle = this.box.querySelector('.progress-ring-fill');
        const progressText = this.box.querySelector('.progress-text');
        
        const offset = this.circumference - (percent / 100) * this.circumference;
        circle.style.strokeDashoffset = offset;
        progressText.textContent = `${Math.round(percent)}%`;
    }

    updateKnowledge() {
        const knowledgeText = this.box.querySelector('.knowledge-text');
        if (this.facts.length > 0) {
            knowledgeText.textContent = this.facts[this.currentFactIndex];
            this.currentFactIndex = (this.currentFactIndex + 1) % this.facts.length;
        }
    }

    updateStatus(status) {
        const statusText = this.box.querySelector('.status-text');
        statusText.textContent = status;
    }

    addStyles() {
        if (document.getElementById('enhanced-perfume-loader-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'enhanced-perfume-loader-styles';
        style.textContent = `
            .enhanced-perfume-loader {
                position: fixed;
                z-index: 10000;
                background: rgba(255, 255, 255, 0.95);
                border: none;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                backdrop-filter: blur(15px);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                max-width: 400px;
                min-width: 320px;
            }

            .enhanced-perfume-loader.center {
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }

            .enhanced-perfume-loader.top {
                top: 50px;
                left: 50%;
                transform: translateX(-50%);
            }

            .enhanced-perfume-loader.bottom {
                bottom: 50px;
                left: 50%;
                transform: translateX(-50%);
            }



            .loader-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
                text-align: center;
            }

            .progress-container {
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .progress-ring {
                transform: rotate(-90deg);
            }

            .progress-ring-bg {
                fill: none;
                stroke: #e0e0e0;
                stroke-width: 3;
            }

            .progress-ring-fill {
                fill: none;
                stroke: #667eea;
                stroke-width: 3;
                stroke-linecap: round;
                transition: stroke-dashoffset 0.3s ease;
            }

            .progress-icon {
                position: absolute;
                font-size: 24px;
                animation: pulse 2s infinite;
            }

            .progress-text {
                position: absolute;
                font-size: 12px;
                font-weight: bold;
                color: #667eea;
                margin-top: 35px;
            }

            .loading-status {
                display: flex;
                flex-direction: column;
                gap: 10px;
                width: 100%;
            }

            .status-text {
                font-size: 18px;
                font-weight: 600;
                color: #333;
                margin-bottom: 5px;
            }

            .knowledge-text {
                font-size: 14px;
                line-height: 1.6;
                color: #666;
                padding: 15px;
                background: rgba(102, 126, 234, 0.1);
                border-radius: 12px;
                border-left: 4px solid #667eea;
                min-height: 60px;
                display: flex;
                align-items: center;
                transition: all 0.5s ease;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.1); }
            }

            /* 다크 테마 */
            .enhanced-perfume-loader.dark {
                background: rgba(30, 30, 30, 0.95);
                color: #fff;
            }

            .enhanced-perfume-loader.dark .status-text {
                color: #fff;
            }

            .enhanced-perfume-loader.dark .knowledge-text {
                background: rgba(255, 255, 255, 0.1);
                color: #e0e0e0;
                border-color: #667eea;
            }

            .enhanced-perfume-loader.dark .progress-ring-bg {
                stroke: #444;
            }

            /* 모바일 대응 */
            @media (max-width: 480px) {
                .enhanced-perfume-loader {
                    margin: 0 20px;
                    padding: 25px 20px;
                    max-width: calc(100vw - 40px);
                }
                
                .knowledge-text {
                    font-size: 13px;
                    padding: 12px;
                }
                
                .status-text {
                    font-size: 16px;
                }
            }

            /* 애니메이션 */
            .enhanced-perfume-loader.fade-in {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.8);
                animation: fadeInScale 0.4s ease-out forwards;
            }

            .enhanced-perfume-loader.fade-out {
                animation: fadeOutScale 0.3s ease-in forwards;
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
                    transform: translate(-50%, -50%) scale(0.8);
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    async show(taskFn, options = {}) {
        const mergedOptions = { ...this.options, ...options };
        
        if (this.isVisible) {
            console.warn('EnhancedPerfumeLoader is already visible');
            return;
        }

        this.isVisible = true;
        this.currentProgress = 0;
        
        // 로더 표시
        this.box.style.display = 'block';
        this.box.classList.add('fade-in');
        
        // 초기 상태 설정
        this.updateProgress(0);
        this.updateStatus('로딩 중...');
        this.updateKnowledge();
        
        // 프로그레스 바 애니메이션 시작
        this.startProgress(mergedOptions.progressDuration);
        
        // 지식 변경 애니메이션 시작
        this.startFactRotation(mergedOptions.factChangeInterval);
        
        try {
            const result = await taskFn();
            return result;
        } finally {
            this.hide();
        }
    }

    startProgress(duration) {
        const startTime = Date.now();
        const updateInterval = 100; // 100ms마다 업데이트
        
        this.progressInterval = setInterval(() => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min((elapsed / duration) * 100, 100);
            
            this.updateProgress(progress);
            
            // 진행률에 따른 상태 메시지 변경
            if (progress < 25) {
                this.updateStatus('요청 처리 중...');
            } else if (progress < 50) {
                this.updateStatus('데이터 분석 중...');
            } else if (progress < 75) {
                this.updateStatus('응답 생성 중...');
            } else if (progress < 100) {
                this.updateStatus('마무리 중...');
            } else {
                this.updateStatus('완료!');
            }
        }, updateInterval);
    }

    startFactRotation(interval) {
        this.factInterval = setInterval(() => {
            this.updateKnowledge();
        }, interval);
    }

    hide() {
        if (!this.isVisible) return;
        
        // 인터벌 정리
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        if (this.factInterval) {
            clearInterval(this.factInterval);
            this.factInterval = null;
        }
        
        // 페이드아웃 애니메이션
        this.box.classList.remove('fade-in');
        this.box.classList.add('fade-out');
        
        setTimeout(() => {
            this.box.style.display = 'none';
            this.box.classList.remove('fade-out');
            this.isVisible = false;
        }, 300);
    }

    // 정적 메서드
    static async show(taskFn, options = {}) {
        const loader = new EnhancedPerfumeLoader(options);
        return await loader.show(taskFn, options);
    }

    static create(options = {}) {
        return new EnhancedPerfumeLoader(options);
    }
}

// 전역 함수 등록
window.EnhancedPerfumeLoader = EnhancedPerfumeLoader;
window.showEnhancedLoading = EnhancedPerfumeLoader.show;
window.createEnhancedLoader = EnhancedPerfumeLoader.create;

// LLM 전용 편의 함수
window.showLLMLoading = function(taskFn, options = {}) {
    const llmOptions = {
        progressDuration: 30000, // 30초
        factChangeInterval: 4000, // 4초마다 지식 변경
        theme: 'default',
        position: 'center',
        ...options
    };
    return EnhancedPerfumeLoader.show(taskFn, llmOptions);
};

// 자동 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.globalEnhancedLoader = new EnhancedPerfumeLoader();
});

export default EnhancedPerfumeLoader;
