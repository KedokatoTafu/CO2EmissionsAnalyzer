import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add toggle Dark mode button to Nav
nav_btn = """<button onclick="toggleDarkMode()" class="ml-4 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition">
                        <svg id="theme-icon" class="w-5 h-5 text-gray-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
                    </button>
                </div>"""
html = html.replace('</div>\n            </div>\n        </div>\n    </nav>', nav_btn + '\n            </div>\n        </div>\n    </nav>')

# 2. Add Dark Mode classes globally
html = html.replace('<html lang="vi">', '<html lang="vi" class="light">')
html = html.replace('bg-gray-50', 'bg-gray-50 dark:bg-[#0b1121]')
html = html.replace('bg-white', 'bg-white dark:bg-gray-800 dark:border-gray-700')
html = html.replace('text-gray-800', 'text-gray-800 dark:text-gray-100')
html = html.replace('text-gray-700', 'text-gray-700 dark:text-gray-200')
html = html.replace('text-gray-600', 'text-gray-600 dark:text-gray-300')
html = html.replace('text-gray-500', 'text-gray-500 dark:text-gray-400')
html = html.replace('border-gray-100', 'border-gray-100 dark:border-gray-700')
html = html.replace('border-gray-200', 'border-gray-200 dark:border-gray-700')
html = html.replace('border-gray-300', 'border-gray-300 dark:border-gray-600')
html = html.replace('bg-blue-50 text-blue-900 border-blue-200', 'bg-blue-50 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100 border-blue-200 dark:border-blue-800')

# 3. Add Tab Navigation for Analytics / Simulation
tabs_html = """
    <div class="flex gap-4 mb-4 border-b border-gray-200 dark:border-gray-700 pb-2">
        <button onclick="switchMainTab('analytics')" id="tab-main-analytics" class="text-lg font-bold text-blue-600 border-b-2 border-blue-600 pb-1">Tổng quan Phân tích</button>
        <button onclick="switchMainTab('simulation')" id="tab-main-simulation" class="text-lg font-bold text-gray-500 dark:text-gray-400 hover:text-blue-500 pb-1">Mô phỏng Kịch bản (What-if)</button>
    </div>
    
    <div id="view-analytics">
"""
html = html.replace('<!-- Grid 4 KPIs -->', tabs_html + '\n        <!-- Grid 4 KPIs -->')

# 4. Insert Simulation View closing and HTML
sim_html = """
    </div> <!-- End view-analytics -->
    
    <div id="view-simulation" class="hidden flex flex-col gap-6">
        <div class="bg-blue-50 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100 p-4 rounded-xl shadow-sm text-sm border border-blue-200 dark:border-blue-800">
            💡 <b>Ý nghĩa Kịch bản:</b> Kéo các thanh trượt bên dưới để mô phỏng tương lai. Dữ liệu sẽ tự động tính toán dựa trên các quốc gia bạn đang chọn ở bộ lọc bên trái. Ví dụ: Nếu chọn Việt Nam và kéo Dân số lên 150%, biểu đồ sẽ dự đoán lượng phát thải và biến đổi khí hậu tương ứng.
        </div>
        
        <!-- Simulation Sliders -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                <label class="text-xs font-bold text-green-500 block mb-2">LAND USE CHANGE: <span id="val-sim-luc">100%</span></label>
                <input type="range" id="sim-slider-luc" min="0" max="200" value="100" class="w-full">
            </div>
            <div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                <label class="text-xs font-bold text-red-500 block mb-2">TEMP ANOMALY IMPACT: <span id="val-sim-temp">100%</span></label>
                <input type="range" id="sim-slider-temp" min="0" max="200" value="100" class="w-full">
            </div>
            <div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                <label class="text-xs font-bold text-purple-500 block mb-2">POPULATION GROWTH: <span id="val-sim-pop">100%</span></label>
                <input type="range" id="sim-slider-pop" min="0" max="200" value="100" class="w-full">
            </div>
            <div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                <label class="text-xs font-bold text-blue-500 block mb-2">ECONOMIC GROWTH (GDP): <span id="val-sim-gdp">100%</span></label>
                <input type="range" id="sim-slider-gdp" min="0" max="200" value="100" class="w-full">
            </div>
        </div>
        
        <!-- Main Stacked Chart -->
        <div class="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-100 dark:border-gray-700" style="height: 400px;">
            <h3 class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">🌍 MÔ PHỎNG PHÁT THẢI KHÍ NHÀ KÍNH (MtCO₂e)</h3>
            <canvas id="simMainChart"></canvas>
        </div>
        
        <!-- Sparklines -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 h-32">
            <div class="bg-white dark:bg-gray-800 p-3 rounded-xl border border-gray-100 dark:border-gray-700 relative overflow-hidden group">
                <span class="text-[10px] font-bold text-green-500 z-10 relative">LAND USE CHANGE</span>
                <canvas id="sim-spark-luc" class="absolute bottom-0 left-0 w-full h-24 opacity-70 group-hover:opacity-100 transition"></canvas>
            </div>
            <div class="bg-white dark:bg-gray-800 p-3 rounded-xl border border-gray-100 dark:border-gray-700 relative overflow-hidden group">
                <span class="text-[10px] font-bold text-red-500 z-10 relative">TEMPERATURE ANOMALY</span>
                <canvas id="sim-spark-temp" class="absolute bottom-0 left-0 w-full h-24 opacity-70 group-hover:opacity-100 transition"></canvas>
            </div>
            <div class="bg-white dark:bg-gray-800 p-3 rounded-xl border border-gray-100 dark:border-gray-700 relative overflow-hidden group">
                <span class="text-[10px] font-bold text-purple-500 z-10 relative">POPULATION GROWTH</span>
                <canvas id="sim-spark-pop" class="absolute bottom-0 left-0 w-full h-24 opacity-70 group-hover:opacity-100 transition"></canvas>
            </div>
            <div class="bg-white dark:bg-gray-800 p-3 rounded-xl border border-gray-100 dark:border-gray-700 relative overflow-hidden group">
                <span class="text-[10px] font-bold text-blue-500 z-10 relative">ECONOMIC GROWTH</span>
                <canvas id="sim-spark-gdp" class="absolute bottom-0 left-0 w-full h-24 opacity-70 group-hover:opacity-100 transition"></canvas>
            </div>
        </div>
        
    </div>
"""
# Insert right before the closing </div> of the right column
html = html.replace('            <!-- Các yếu tố tác động (Sparklines) -->', sim_html + '\n            <!-- Các yếu tố tác động (Sparklines) -->')

# 5. Add JS logic for Theme, Tabs, and Simulation
js_logic = """
        let isDarkMode = false;
        function toggleDarkMode() {
            isDarkMode = !isDarkMode;
            if(isDarkMode) {
                document.documentElement.classList.add('dark');
                document.getElementById('theme-icon').innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>';
            } else {
                document.documentElement.classList.remove('dark');
                document.getElementById('theme-icon').innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>';
            }
            // Update charts colors
            Chart.defaults.color = isDarkMode ? '#94a3b8' : '#64748b';
            Chart.defaults.borderColor = isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
            if(lineChartInst) lineChartInst.update();
            if(barChartInst) barChartInst.update();
            if(pieChartInst) pieChartInst.update();
            if(simMainChartInst) simMainChartInst.update();
        }

        let currentMainTab = 'analytics';
        function switchMainTab(tab) {
            currentMainTab = tab;
            if(tab === 'analytics') {
                document.getElementById('view-analytics').classList.remove('hidden');
                document.getElementById('view-simulation').classList.add('hidden');
                document.getElementById('tab-main-analytics').className = "text-lg font-bold text-blue-600 border-b-2 border-blue-600 pb-1";
                document.getElementById('tab-main-simulation').className = "text-lg font-bold text-gray-500 dark:text-gray-400 hover:text-blue-500 pb-1";
            } else {
                document.getElementById('view-analytics').classList.add('hidden');
                document.getElementById('view-simulation').classList.remove('hidden');
                document.getElementById('tab-main-simulation').className = "text-lg font-bold text-blue-600 border-b-2 border-blue-600 pb-1";
                document.getElementById('tab-main-analytics').className = "text-lg font-bold text-gray-500 dark:text-gray-400 hover:text-blue-500 pb-1";
                fetchSimulationData();
            }
        }

        let rawSimData = null;
        let simMainChartInst = null;
        const simColors = {
            coal: { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.4)' },
            oil: { border: '#10b981', bg: 'rgba(16, 185, 129, 0.4)' },
            cement: { border: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.4)' },
            methane: { border: '#3b82f6', bg: 'rgba(59, 130, 246, 0.4)' }
        };

        async function fetchSimulationData() {
            const qs = buildQueryString();
            try {
                const res = await fetch(`${API_URL}/api/simulation_data?${qs}`);
                rawSimData = await res.json();
                updateSimulation();
            } catch(e) { console.error(e); }
        }

        function getSimMultipliers() {
            return {
                luc: document.getElementById('sim-slider-luc').value / 100,
                temp: document.getElementById('sim-slider-temp').value / 100,
                pop: document.getElementById('sim-slider-pop').value / 100,
                gdp: document.getElementById('sim-slider-gdp').value / 100,
            }
        }

        ['luc', 'temp', 'pop', 'gdp'].forEach(id => {
            document.getElementById(`sim-slider-${id}`).addEventListener('input', (e) => {
                document.getElementById(`val-sim-${id}`).innerText = e.target.value + '%';
                updateSimulation();
            });
        });

        function updateSimulation() {
            if (!rawSimData || !rawSimData.labels) return;
            const m = getSimMultipliers();

            const simulated = {
                labels: rawSimData.labels,
                coal: rawSimData.coal.map(v => v * m.gdp), 
                oil: rawSimData.oil.map(v => v * m.pop * m.gdp), 
                cement: rawSimData.cement.map(v => v * m.pop), 
                methane: rawSimData.methane.map(v => v * m.luc), 
                luc: rawSimData.land_use.map(v => v * m.luc),
                temp: rawSimData.temperature.map(v => v * m.temp),
                pop: rawSimData.population.map(v => v * m.pop),
                gdp: rawSimData.gdp.map(v => v * m.gdp)
            };

            const ctx = document.getElementById('simMainChart').getContext('2d');
            if (simMainChartInst) simMainChartInst.destroy();
            simMainChartInst = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: simulated.labels,
                    datasets: [
                        { label: 'Coal (Than)', data: simulated.coal, borderColor: simColors.coal.border, backgroundColor: simColors.coal.bg, fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0 },
                        { label: 'Oil (Dầu)', data: simulated.oil, borderColor: simColors.oil.border, backgroundColor: simColors.oil.bg, fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0 },
                        { label: 'Cement (Xi măng)', data: simulated.cement, borderColor: simColors.cement.border, backgroundColor: simColors.cement.bg, fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0 },
                        { label: 'Methane (Metan)', data: simulated.methane, borderColor: simColors.methane.border, backgroundColor: simColors.methane.bg, fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: { legend: { position: 'bottom' } },
                    scales: { x: { grid: { display: false } }, y: { stacked: true, beginAtZero: true } }
                }
            });

            renderSparkline('sim-spark-luc', simulated.labels, simulated.luc, '#4ade80', 'rgba(74, 222, 128, 0.2)');
            renderSparkline('sim-spark-temp', simulated.labels, simulated.temp, '#f87171', 'rgba(248, 113, 113, 0.2)');
            renderSparkline('sim-spark-pop', simulated.labels, simulated.pop, '#c084fc', 'rgba(192, 132, 252, 0.2)');
            renderSparkline('sim-spark-gdp', simulated.labels, simulated.gdp, '#60a5fa', 'rgba(96, 165, 250, 0.2)');
        }
"""
html = html.replace('// Khởi tạo ban đầu', js_logic + '\n        // Khởi tạo ban đầu')

# Remove the 'Mô phỏng Kịch bản (Dark Mode)' button from the nav that was added in a previous step to avoid duplication.
html = re.sub(r'<a href="/advanced" .*?>.*?</a>', '', html, flags=re.DOTALL)

# Tweak tailwind configuration for darkmode support
html = html.replace('<script src="https://cdn.tailwindcss.com"></script>', '<script src="https://cdn.tailwindcss.com"></script>\n    <script>tailwind.config = { darkMode: "class" }</script>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Đã chỉnh sửa index.html thành công bằng script")

