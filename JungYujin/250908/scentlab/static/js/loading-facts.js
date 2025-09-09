class PerfumeFactsLoader {
    constructor() {
        this.facts = [];
        this.loadFacts();
    }

    async loadFacts() {
        try {
            const response = await fetch('/static/js/perfume_facts.json');
            this.facts = await response.json();
        } catch (error) {
            console.error('Error loading perfume facts:', error);
        }
    }

    createLoadingUI() {
        const container = document.createElement('div');
        container.className = 'loading-container';
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        const factBox = document.createElement('div');
        factBox.className = 'fact-box';
        factBox.innerHTML = '<span class="fact-icon">💡</span> <span class="fact-text"></span>';
        
        container.appendChild(spinner);
        container.appendChild(factBox);
        
        return { container, factBox };
    }

    getRandomFact() {
        return this.facts[Math.floor(Math.random() * this.facts.length)];
    }

    showLoading(targetElement) {
        const { container, factBox } = this.createLoadingUI();
        targetElement.appendChild(container);

        const updateFact = () => {
            const factText = factBox.querySelector('.fact-text');
            factText.textContent = this.getRandomFact();
        };

        updateFact();
        return setInterval(updateFact, 3000);
    }

    hideLoading(targetElement, intervalId) {
        const container = targetElement.querySelector('.loading-container');
        if (container) {
            container.remove();
        }
        if (intervalId) {
            clearInterval(intervalId);
        }
    }
}