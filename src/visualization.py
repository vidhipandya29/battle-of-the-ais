from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import NetworkModule, ChartModule, TextElement
from mesa.visualization.UserParam import Slider, Checkbox

# Create a legend element to explain the node colors
class LegendElement(TextElement):
    def __init__(self):
        pass
        
    def render(self, model):
        return """
        <div style="background-color: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin-bottom: 15px;">
            <h3 style="margin-top: 0;">Node Color and Size Legend:</h3>
            <ul style="margin-bottom: 0;">
                <li><span style="color: gray; font-weight: bold;">Small Gray:</span> Unexposed Users - users who haven't encountered deepfake content</li>
                <li><span style="color: red; font-weight: bold;">Large Red:</span> Generator AI Bots - AI systems creating and spreading deepfake content</li>
                <li><span style="color: red; font-weight: bold;">Small Red:</span> Exposed Users - regular users who have encountered deepfake content</li>
                <li><span style="color: gray; font-weight: bold;">Large Gray:</span> Detector AI Bots - AI systems that identify and neutralize deepfake content</li>
                <li><span style="color: gray; font-weight: bold;">Large Gray (with X):</span> Neutralized Generator AIs - generators whose effectiveness dropped below 40%</li>
                <li><span style="color: green; font-weight: bold;">Small Green:</span> Labeled Users - users whose content has been identified and labeled</li>
            </ul>
        </div>
        """

# Create a battle status element to show AI vs AI interactions
class BattleStatusElement(TextElement):
    def __init__(self):
        pass
        
    def render(self, model):
        active_generators = model.count_active_generators()
        neutralized_generators = model.count_neutralized_generators()
        total_generators = active_generators + neutralized_generators
        detector_win_pct = 0
        if total_generators > 0:
            detector_win_pct = (neutralized_generators / total_generators) * 100
            
        generator_win_pct = 0
        total_users = model.count_unexposed() + model.count_exposed() + model.count_labeled()
        if total_users > 0:
            exposed_pct = ((model.count_exposed() + model.count_labeled()) / total_users) * 100
            generator_win_pct = exposed_pct
        
        # Calculate percentage bars
        gen_success_bar = int(generator_win_pct)
        det_success_bar = int(detector_win_pct)
        
        return f"""
        <div style="padding: 12px; margin: 0;">
            <h3 style="margin-top: 0; margin-bottom: 8px; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px;">
                <i class="fas fa-chart-line" style="margin-right: 6px;"></i> AI Battle Status
            </h3>
            
            <div class="battle-status">
                <div class="battle-status-section" style="border-left: 3px solid #e03131;">
                    <h4 style="color: #e03131; margin: 0 0 8px 0;">
                        <i class="fas fa-robot" style="margin-right: 5px;"></i> Generator AI
                    </h4>
                    <div style="margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 12px;">Active</span>
                            <strong>{active_generators}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 12px;">Neutralized</span>
                            <strong>{neutralized_generators}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 12px;">Success Rate</span>
                            <strong>{generator_win_pct:.1f}%</strong>
                        </div>
                    </div>
                    
                    <div style="margin-top: 10px;">
                        <div style="font-size: 11px; margin-bottom: 3px;">Users Exposed</div>
                        <div style="height: 6px; background-color: #f1f3f5; border-radius: 3px; overflow: hidden;">
                            <div style="height: 100%; width: {gen_success_bar}%; background-color: #e03131; border-radius: 3px;"></div>
                        </div>
                    </div>
                </div>
                
                <div class="battle-status-section" style="border-left: 3px solid #2b8a3e;">
                    <h4 style="color: #2b8a3e; margin: 0 0 8px 0;">
                        <i class="fas fa-shield-alt" style="margin-right: 5px;"></i> Detector AI
                    </h4>
                    <div style="margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 12px;">Active</span>
                            <strong>{model.num_detectors}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 12px;">Neutralized</span>
                            <strong>{neutralized_generators}/{total_generators}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 12px;">Success Rate</span>
                            <strong>{detector_win_pct:.1f}%</strong>
                        </div>
                    </div>
                    
                    <div style="margin-top: 10px;">
                        <div style="font-size: 11px; margin-bottom: 3px;">Generators Neutralized</div>
                        <div style="height: 6px; background-color: #f1f3f5; border-radius: 3px; overflow: hidden;">
                            <div style="height: 100%; width: {det_success_bar}%; background-color: #2b8a3e; border-radius: 3px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

class AIBattleDescriptionElement(TextElement):
    def __init__(self):
        pass
        
    def render(self, model):
        return """
        <div style="background-color: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin-bottom: 15px;">
            <h3 style="margin-top: 0;">AI vs AI Battle Simulation:</h3>
            <p>This simulation shows bot vs bot battles between:</p>
            <ul>
                <li><strong style="color: red;">Generator AIs</strong> - bots designed to create and spread misinformation</li>
                <li><strong style="color: green;">Detector AIs</strong> - bots designed to identify and neutralize misinformation sources</li>
            </ul>
            <p>When detector bots encounter generator bots, they attempt to reduce their effectiveness. 
               If a generator's effectiveness drops below 40%, it becomes neutralized (turns grey).</p>
            <p>Generator bots can also evade detection based on their evasion skill.</p>
        </div>
        """

# Create a combined legend and description element
class CombinedLegendElement(TextElement):
    def __init__(self):
        pass
        
    def render(self, model):
        return """
        <div style="padding: 12px; margin: 0;">
            <h3 style="margin-top: 0; margin-bottom: 8px; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px;">
                <i class="fas fa-info-circle" style="margin-right: 6px;"></i> AI Battle Simulation
            </h3>
            
            <div style="font-size: 13px; line-height: 1.5; margin-bottom: 10px;">
                <p style="margin: 0 0 8px 0;">
                    <strong style="color: #e03131;">Generator AIs</strong> create misinformation while 
                    <strong style="color: #2b8a3e;">Detector AIs</strong> try to neutralize them. 
                    Generators become neutralized when their effectiveness drops below 40%.
                </p>
            </div>
            
            <div style="display: flex; flex-wrap: wrap; background-color: #f8f9fa; border-radius: 6px; padding: 8px; margin-top: 5px;">
                <div style="flex: 1; min-width: 120px;">
                    <div style="font-weight: 600; font-size: 12px; margin-bottom: 6px; color: #495057;">Network Nodes</div>
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #1971c2; margin-right: 8px;"></span>
                        <span style="font-size: 12px;">Unexposed Users</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #e03131; margin-right: 8px;"></span>
                        <span style="font-size: 12px;">Generators/Exposed</span>
                    </div>
                </div>
                <div style="flex: 1; min-width: 120px;">
                    <div style="font-weight: 600; font-size: 12px; margin-bottom: 6px; color: #495057;">AI Types</div>
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #2b8a3e; margin-right: 8px;"></span>
                        <span style="font-size: 12px;">Detector AIs</span>
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #495057; margin-right: 8px;"></span>
                        <span style="font-size: 12px;">Neutralized/Labeled</span>
                    </div>
                </div>
            </div>
        </div>
        """

# New combined element that merges battle status and simulation info
class CombinedBattleElement(TextElement):
    def __init__(self):
        pass
        
    def render(self, model):
        active_generators = model.count_active_generators()
        neutralized_generators = model.count_neutralized_generators()
        total_generators = active_generators + neutralized_generators
        detector_win_pct = 0
        if total_generators > 0:
            detector_win_pct = (neutralized_generators / total_generators) * 100
            
        generator_win_pct = 0
        total_users = model.count_unexposed() + model.count_exposed() + model.count_labeled()
        if total_users > 0:
            exposed_pct = ((model.count_exposed() + model.count_labeled()) / total_users) * 100
            generator_win_pct = exposed_pct
        
        # Calculate percentage bars
        gen_success_bar = int(generator_win_pct)
        det_success_bar = int(detector_win_pct)
        
        return f"""
        <div style="padding: 12px; margin: 0;">
            <h3 style="margin-top: 0; margin-bottom: 8px; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px;">
                <i class="fas fa-robot" style="margin-right: 6px;"></i> AI Battle Dashboard
            </h3>
            
            <!-- Combined description and legend -->
            <div style="font-size: 13px; line-height: 1.4; margin-bottom: 15px;">
                <p style="margin: 0 0 8px 0;">
                    <strong style="color: #e03131;">Generator AIs</strong> create misinformation while 
                    <strong style="color: #2b8a3e;">Detector AIs</strong> try to neutralize them. 
                    Generators become neutralized when their effectiveness drops below 40%.
                </p>
                
                <!-- Compact legend -->
                <div style="display: flex; flex-wrap: wrap; background-color: #f8f9fa; border-radius: 6px; padding: 8px; margin: 8px 0;">
                    <div style="flex: 1; min-width: 120px;">
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #1971c2; margin-right: 6px;"></span>
                            <span style="font-size: 11px;"><strong>Small Blue:</strong> Unexposed Users</span>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="display: inline-block; width: 16px; height: 16px; border-radius: 50%; background-color: #e03131; margin-right: 6px;"></span>
                            <span style="font-size: 11px;"><strong>Large Red:</strong> Generator AI Bots</span>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #e03131; margin-right: 6px;"></span>
                            <span style="font-size: 11px;"><strong>Small Red:</strong> Exposed Users</span>
                        </div>
                    </div>
                    <div style="flex: 1; min-width: 120px;">
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="display: inline-block; width: 16px; height: 16px; border-radius: 50%; background-color: #2b8a3e; margin-right: 6px;"></span>
                            <span style="font-size: 11px;"><strong>Large Green:</strong> Detector AIs</span>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="display: inline-block; width: 16px; height: 16px; border-radius: 50%; background-color: #495057; margin-right: 6px;"></span>
                            <span style="font-size: 11px;"><strong>Large Grey:</strong> Neutralized Generators</span>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #495057; margin-right: 6px;"></span>
                            <span style="font-size: 11px;"><strong>Small Grey:</strong> Labeled Users</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Battle status metrics -->
            <div class="battle-status" style="margin-top: 0;">
                <div class="battle-status-section" style="border-left: 3px solid #e03131;">
                    <h4 style="color: #e03131; margin: 0 0 6px 0; font-size: 13px;">
                        <i class="fas fa-robot" style="margin-right: 5px;"></i> Generator AI
                    </h4>
                    <div style="margin-bottom: 6px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 11px;">Active</span>
                            <strong>{active_generators}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 11px;">Neutralized</span>
                            <strong>{neutralized_generators}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 11px;">Success Rate</span>
                            <strong>{generator_win_pct:.1f}%</strong>
                        </div>
                    </div>
                    
                    <div style="margin-top: 6px;">
                        <div style="font-size: 10px; margin-bottom: 2px;">Users Exposed</div>
                        <div style="height: 5px; background-color: #f1f3f5; border-radius: 3px; overflow: hidden;">
                            <div style="height: 100%; width: {gen_success_bar}%; background-color: #e03131; border-radius: 3px;"></div>
                        </div>
                    </div>
                </div>
                
                <div class="battle-status-section" style="border-left: 3px solid #2b8a3e;">
                    <h4 style="color: #2b8a3e; margin: 0 0 6px 0; font-size: 13px;">
                        <i class="fas fa-shield-alt" style="margin-right: 5px;"></i> Detector AI
                    </h4>
                    <div style="margin-bottom: 6px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 11px;">Active</span>
                            <strong>{model.num_detectors}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 11px;">Neutralized</span>
                            <strong>{neutralized_generators}/{total_generators}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                            <span style="font-size: 11px;">Success Rate</span>
                            <strong>{detector_win_pct:.1f}%</strong>
                        </div>
                    </div>
                    
                    <div style="margin-top: 6px;">
                        <div style="font-size: 10px; margin-bottom: 2px;">Generators Neutralized</div>
                        <div style="height: 5px; background-color: #f1f3f5; border-radius: 3px; overflow: hidden;">
                            <div style="height: 100%; width: {det_success_bar}%; background-color: #2b8a3e; border-radius: 3px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

# Add a new class for custom JavaScript to fix chart labels
class FixChartLabelsElement(TextElement):
    def __init__(self):
        pass
        
    def render(self, model):
        return """
        <script>
        // Direct Chart.js legend override - browser cache-busting approach
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Initializing direct Chart.js legend override');
            
            // Force clear any potential browser cache for chart elements
            localStorage.removeItem('chartjs.legend.cache');
            sessionStorage.removeItem('chartjs.legend.cache');
            
            // Add a version flag to URLs to bypass cache
            const cacheBuster = new Date().getTime();
            document.querySelectorAll('canvas').forEach(canvas => {
                canvas.setAttribute('data-version', cacheBuster);
            });
            
            // First-level fix: Apply custom labels directly to chart options
            setTimeout(directChartLabelOverride, 10);
            setTimeout(directChartLabelOverride, 200);
            setTimeout(directChartLabelOverride, 1000);
            
            // Detect browser for specific fixes
            const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
            const isChrome = /chrome/i.test(navigator.userAgent) && !/edge/i.test(navigator.userAgent);
            
            function directChartLabelOverride() {
                console.log('Applying direct chart label override...');
                
                // Get all chart instances from Chart.js registry
                let chartInstances = Object.values(Chart.instances || {});
                
                if (chartInstances.length === 0) {
                    console.log('No chart instances found yet, will retry');
                    return; // Will retry on next timeout
                }
                
                console.log(`Found ${chartInstances.length} chart instances to fix`);
                
                // Define correct labels for each chart
                const correctLabels = [
                    // First chart - User States Chart
                    ['Unexposed', 'Exposed', 'Labeled'],
                    // Second chart - Generator States Chart
                    ['Active Generators', 'Neutralized Generators']
                ];
                
                // Apply fixes to each chart
                chartInstances.forEach((chart, idx) => {
                    if (!chart || !chart.config) return;
                    
                    const chartIndex = idx % 2; // Alternate between the two types of charts
                    const labels = correctLabels[chartIndex];
                    
                    // Direct override of legend labels in the chart configuration
                    if (chart.config.data && chart.config.data.datasets) {
                        chart.config.data.datasets.forEach((dataset, i) => {
                            if (i < labels.length) {
                                dataset.label = labels[i];
                            }
                        });
                    }
                    
                    try {
                        // Force rebuild legend with new labels
                        if (chart.legend && chart.legend.legendItems) {
                            chart.legend.legendItems.forEach((item, i) => {
                                if (i < labels.length) {
                                    item.text = labels[i];
                                    if (item.fillStyle) {
                                        // Keep original colors
                                    }
                                }
                            });
                        }
                        
                        // Update the chart
                        chart.update();
                        console.log(`Fixed chart ${idx+1} labels`);
                    } catch (e) {
                        console.error('Error updating chart:', e);
                    }
                });
                
                // Second-level fix: Replace text nodes directly in the DOM
                fixLegendLabelsInDOM();
            }
            
            function fixLegendLabelsInDOM() {
                console.log('Applying DOM-level text replacement for chart labels');
                
                // Target every span in legend containers
                document.querySelectorAll('.legend span').forEach((span) => {
                    const text = span.textContent.toLowerCase().trim();
                    
                    // Fix "unkabeled" specifically - exact match for the typo
                    if (text === 'unkabeled' || text === 'unlabeled' || text === 'undefined') {
                        span.textContent = 'Labeled';
                        console.log('Fixed "unkabeled/unlabeled/undefined" to "Labeled"');
                    }
                    
                    // Apply browser-specific fixes
                    if (isSafari || isChrome) {
                        // Get the chart container
                        const chartContainer = span.closest('.chart-container');
                        if (!chartContainer) return;
                        
                        // Get chart index (determine if it's the first or second chart)
                        const allCharts = Array.from(document.querySelectorAll('.chart-container'));
                        const chartIndex = allCharts.indexOf(chartContainer);
                        
                        // Get color box
                        const colorDiv = span.previousElementSibling;
                        if (!colorDiv) return;
                        
                        const bgColor = window.getComputedStyle(colorDiv).backgroundColor;
                        
                        // Apply correct label based on color and chart position
                        if (chartIndex === 0) { // First chart - User States
                            if (bgColor.includes('73, 113') || bgColor.includes('25, 113') || 
                                bgColor.includes('rgb(25, 113') || bgColor.includes('rgb(33, 150')) {
                                span.textContent = 'Unexposed';
                            } else if (bgColor.includes('224, 49') || bgColor.includes('229, 57') || 
                                       bgColor.includes('rgb(224, 49') || bgColor.includes('rgb(229, 57')) {
                                span.textContent = 'Exposed';
                            } else if (bgColor.includes('73, 80') || bgColor.includes('rgb(73, 80')) {
                                span.textContent = 'Labeled';
                            }
                        } else { // Second chart - Generator States
                            if (bgColor.includes('224, 49') || bgColor.includes('229, 57') || 
                                bgColor.includes('rgb(224, 49') || bgColor.includes('rgb(229, 57')) {
                                span.textContent = 'Active Generators';
                            } else if (bgColor.includes('73, 80') || bgColor.includes('rgb(73, 80')) {
                                span.textContent = 'Neutralized Generators';
                            }
                        }
                    }
                });
            }
            
            // Monitor for any chart updates or redraws
            const observer = new MutationObserver(function(mutations) {
                let needsFix = false;
                
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length || 
                        (mutation.type === 'characterData' && 
                         mutation.target.parentNode && 
                         mutation.target.parentNode.closest('.legend'))) {
                        needsFix = true;
                    }
                });
                
                if (needsFix) {
                    directChartLabelOverride();
                    fixLegendLabelsInDOM();
                }
            });
            
            // Start observing with expanded options
            observer.observe(document.body, { 
                childList: true, 
                subtree: true, 
                characterData: true,
                attributes: true,
                attributeFilter: ['class', 'style']
            });
            
            // Third-level fix: Periodically check for any remaining issues
            setInterval(function() {
                document.querySelectorAll('.legend span').forEach(span => {
                    const text = span.textContent.toLowerCase().trim();
                    if (text === 'unkabeled' || text === 'unlabeled' || text === 'undefined' || text === '') {
                        // Trigger a full refresh of charts
                        directChartLabelOverride();
                        fixLegendLabelsInDOM();
                    }
                });
            }, 2000);
            
            // Final method: Hard-coded legend replacement for stubborn browsers
            setTimeout(function() {
                document.querySelectorAll('.chart-container').forEach((container, idx) => {
                    // Force completely new legend for the really stubborn cases
                    const legend = container.querySelector('.legend');
                    if (legend) {
                        // Create backup of original to preserve structure
                        const originalHTML = legend.innerHTML;
                        
                        // Determine chart type
                        const chartLabels = (idx % 2 === 0) ? 
                            ['Unexposed', 'Exposed', 'Labeled'] : 
                            ['Active Generators', 'Neutralized Generators'];
                        
                        // Get all the color boxes
                        const colorBoxes = Array.from(legend.querySelectorAll('div > div')).filter(
                            div => !div.textContent && 
                            window.getComputedStyle(div).width === '14px' && 
                            window.getComputedStyle(div).height === '14px'
                        );
                        
                        // If we have the right structure, perform direct label fix
                        if (colorBoxes.length === chartLabels.length) {
                            const labelSpans = Array.from(legend.querySelectorAll('span'));
                            
                            if (labelSpans.length === chartLabels.length) {
                                labelSpans.forEach((span, i) => {
                                    if (span.textContent.toLowerCase().includes('unkabel') ||
                                        span.textContent.toLowerCase().includes('undefined') ||
                                        span.textContent.toLowerCase().includes('unlabel')) {
                                        span.textContent = chartLabels[i];
                                        console.log(`Hard-fixed label ${i+1} to: ${chartLabels[i]}`);
                                    }
                                });
                            }
                        }
                    }
                });
            }, 3000);
        });
        </script>
        """

# Add a custom CSS element for layout control
class CustomCSSElement(TextElement):
    def __init__(self):
        pass
        
    def render(self, model):
        return """
        <script>
        // Add viewport meta tag for proper scaling across devices
        (function() {
            // Create viewport meta if it doesn't exist
            if (!document.querySelector('meta[name="viewport"]')) {
                var meta = document.createElement('meta');
                meta.name = 'viewport';
                meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
                document.getElementsByTagName('head')[0].appendChild(meta);
            }
            
            // Add browser check and class to body
            document.addEventListener('DOMContentLoaded', function() {
                var body = document.body;
                if (/chrome/i.test(navigator.userAgent)) body.classList.add('chrome');
                else if (/firefox/i.test(navigator.userAgent)) body.classList.add('firefox');
                else if (/safari/i.test(navigator.userAgent) && !/chrome/i.test(navigator.userAgent)) body.classList.add('safari');
                else if (/edge/i.test(navigator.userAgent)) body.classList.add('edge');
                
                // Add modern theme class
                document.body.classList.add('modern-theme');
                
                // Force a layout refresh for browsers that need it
                setTimeout(function() {
                    window.dispatchEvent(new Event('resize'));
                    
                    // Add smooth animation to panels
                    var containers = document.querySelectorAll('.element-container');
                    containers.forEach(function(container, index) {
                        setTimeout(function() {
                            container.classList.add('visible');
                        }, 100 * index);
                    });
                }, 300);
                
                // Enhance model title
                var titleBar = document.querySelector('.model-title');
                if (titleBar) {
                    // Add battle icon to title
                    var title = titleBar.querySelector('span');
                    if (title && title.textContent.includes('Battle')) {
                        title.innerHTML = '<i class="fas fa-robot" style="margin-right:8px;"></i>' + title.textContent;
                    }
                    
                    // Style the buttons
                    var buttons = titleBar.querySelectorAll('button');
                    buttons.forEach(function(btn) {
                        btn.classList.add('modern-button');
                        if (btn.textContent.trim() === 'Start') {
                            btn.innerHTML = '<i class="fas fa-play"></i> Start';
                        } else if (btn.textContent.trim() === 'Stop') {
                            btn.innerHTML = '<i class="fas fa-stop"></i> Stop';
                        } else if (btn.textContent.trim() === 'Reset') {
                            btn.innerHTML = '<i class="fas fa-sync"></i> Reset';
                        }
                    });
                }
            });
        })();
        </script>
        
        <!-- Add Font Awesome for icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        
        <style>
        /* Reset and base styles for cross-browser consistency */
        * {
            box-sizing: border-box;
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
        }
        
        /* Modern UI and viewport optimizations - with scrolling enabled */
        html, body {
            max-height: 100vh;
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background-color: #f8f9fa;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
            color: #343a40;
            line-height: 1.5;
            /* Allow scrolling */
            overflow-y: auto;
        }
        
        /* Make header look more modern */
        .model-title {
            background: linear-gradient(to right, #2a2d3e, #3a3d4e) !important;
            padding: 12px 20px !important;
            color: white !important;
            display: flex;
            display: -webkit-flex;
            display: -moz-flex;
            display: -ms-flexbox;
            justify-content: space-between;
            -webkit-justify-content: space-between;
            -moz-justify-content: space-between;
            -ms-justify-content: space-between;
            align-items: center;
            -webkit-align-items: center;
            -moz-align-items: center;
            -ms-align-items: center;
            box-shadow: 0 3px 5px rgba(0,0,0,0.1);
            -webkit-box-shadow: 0 3px 5px rgba(0,0,0,0.1);
            -moz-box-shadow: 0 3px 5px rgba(0,0,0,0.1);
            z-index: 1000;
            position: sticky;
            top: 0;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        .model-title span {
            display: flex;
            align-items: center;
            font-size: 16px;
        }
        
        /* Modern buttons */
        .modern-button {
            background-color: rgba(255,255,255,0.15) !important;
            border: none !important;
            border-radius: 4px !important;
            color: white !important;
            padding: 6px 12px !important;
            margin-left: 8px !important;
            font-size: 13px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        .modern-button:hover {
            background-color: rgba(255,255,255,0.25) !important;
            transform: translateY(-1px);
        }
        
        .modern-button i {
            margin-right: 5px;
        }
        
        /* Cross-browser grid layout with scrolling */
        #elements-container {
            display: grid !important;
            display: -ms-grid !important; /* For Edge */
            grid-template-columns: 35% 65%;
            -ms-grid-columns: 35% 65%; /* For Edge */
            grid-template-rows: auto auto auto auto auto;
            -ms-grid-rows: auto auto auto auto auto; /* For Edge */
            min-height: calc(100vh - 100px);
            width: 100%;
            gap: 12px;
            grid-gap: 12px; /* Older syntax */
            padding: 12px;
            box-sizing: border-box;
            /* Allow scrolling */
            overflow-y: auto;
        }
        
        /* For browsers that don't fully support grid */
        @supports not (display: grid) {
            #elements-container {
                display: flex !important;
                flex-wrap: wrap !important;
            }
            
            #elements-container > div {
                flex: 1 1 300px;
                margin: 5px;
            }
        }
        
        /* Model params in a scrollable area */
        #model-params {
            grid-column: 1;
            -ms-grid-column: 1;
            grid-row: 1;
            -ms-grid-row: 1;
            max-height: 100px;
            overflow-y: auto;
            margin: 0;
            padding: 12px;
            background-color: white;
            border-radius: 10px;
            -webkit-border-radius: 10px;
            -moz-border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            -webkit-box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            -moz-box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid rgba(0,0,0,0.04);
        }
        
        /* Scrollbar styling for webkit browsers */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f3f5;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #adb5bd;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #868e96;
        }
        
        /* Shared card styling */
        .element-container {
            margin: 0 !important;
            background-color: white;
            border-radius: 10px;
            -webkit-border-radius: 10px;
            -moz-border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            -webkit-box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            -moz-box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.04);
            opacity: 0;
            transform: translateY(5px);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .element-container.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        /* AI Battle Dashboard (CombinedBattleElement) - moved to bottom */
        .element-container:nth-of-type(1) {
            grid-column: 1 / span 2; /* Span across both columns */
            -ms-grid-column: 1;
            -ms-grid-column-span: 2;
            grid-row: 5; /* Move to bottom row */
            -ms-grid-row: 5;
        }
        
        /* Network view */
        .element-container:nth-of-type(2) {
            grid-column: 2;
            -ms-grid-column: 2;
            grid-row: 1 / span 3;
            -ms-grid-row: 1;
            -ms-grid-row-span: 3;
        }
        
        /* First chart - User States */
        .element-container:nth-of-type(3) {
            grid-column: 1;
            -ms-grid-column: 1;
            grid-row: 2;
            -ms-grid-row: 2;
        }
        
        /* Second chart - Generator States */
        .element-container:nth-of-type(4) {
            grid-column: 1;
            -ms-grid-column: 1;
            grid-row: 3;
            -ms-grid-row: 3;
        }
        
        /* Fix Chart Labels element (hidden) */
        .element-container:nth-of-type(5) {
            grid-column: 2;
            -ms-grid-column: 2;
            grid-row: 4;
            -ms-grid-row: 4;
            display: none; /* Hide this element as it's just JS */
        }
        
        /* Element content styling */
        .element-container > div {
            padding: 12px !important;
            margin-bottom: 0 !important;
            background-color: transparent !important;
            border: none !important;
        }
        
        /* Typography */
        .element-container h3 {
            margin-top: 0;
            margin-bottom: 8px;
            font-size: 15px;
            color: #2a2d3e;
            font-weight: 600;
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 8px;
        }
        
        .element-container h4 {
            font-size: 14px;
            margin: 5px 0;
            font-weight: 600;
        }
        
        .element-container p, 
        .element-container ul {
            margin: 5px 0;
            font-size: 13px;
            color: #555;
            line-height: 1.5;
        }
        
        .element-container li {
            margin-bottom: 4px;
        }
        
        /* Chart container styling */
        .chart-container {
            height: 130px !important;
            margin-top: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 !important;
        }
        
        /* Fix for chart overflows */
        .chart-container canvas {
            max-width: 100% !important;
            border-radius: 4px;
        }
        
        /* Network styling */
        .NetworkModule_component {
            width: 100% !important;
            height: 450px !important;
            max-height: calc(100vh - 200px) !important;
            background-color: #fafafa !important;
            border-radius: 4px;
        }
        
        /* Browser-specific adjustments */
        .firefox .NetworkModule_component {
            height: 440px !important;
        }
        
        .safari .chart-container {
            height: 125px !important;
        }
        
        .chrome .element-container:nth-of-type(2) {
            height: calc(100vh - 250px) !important;
        }
        
        .edge #elements-container {
            display: flex !important;
            flex-wrap: wrap !important;
        }
        
        /* Slider styling */
        .slider-container {
            margin-bottom: 8px !important;
            border-radius: 4px;
            padding: 5px 8px !important;
            background-color: #f8f9fa;
        }
        
        .slider-label {
            font-size: 13px !important;
            font-weight: 500;
            color: #444;
            margin-bottom: 4px;
            display: block;
        }
        
        /* Cross-browser slider styling */
        input[type="range"] {
            height: 4px;
            border-radius: 2px;
            -webkit-border-radius: 2px;
            -moz-border-radius: 2px;
            background: #e9ecef;
            outline: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            width: 100%;
            max-width: 100%;
            margin: 8px 0;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            -webkit-border-radius: 50%;
            background: #4263eb;
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        input[type="range"]::-moz-range-thumb {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            -moz-border-radius: 50%;
            background: #4263eb;
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        input[type="range"]::-ms-thumb {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #4263eb;
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Control buttons */
        .button-container {
            display: flex;
            display: -webkit-flex;
            display: -moz-flex;
            display: -ms-flexbox;
            gap: 8px;
        }
        
        .button {
            background-color: #4263eb !important;
            color: white !important;
            border: none !important;
            padding: 6px 12px !important;
            border-radius: 6px !important;
            -webkit-border-radius: 6px !important;
            -moz-border-radius: 6px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            -webkit-transition: all 0.2s ease !important;
            -moz-transition: all 0.2s ease !important;
            box-shadow: 0 2px 4px rgba(66, 99, 235, 0.2) !important;
        }
        
        .button:hover {
            background-color: #3b5bdb !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(66, 99, 235, 0.25) !important;
        }
        
        /* Current step display */
        .current-step {
            font-size: 13px;
            color: #555;
            background-color: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }
        
        /* Chart legends */
        .legend {
            font-size: 12px !important;
            margin-top: 5px !important;
            display: flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
        }
        
        .legend > div {
            margin: 0 8px !important;
            display: flex !important;
            align-items: center !important;
        }
        
        /* Checkbox styling */
        input[type="checkbox"] {
            accent-color: #4263eb;
            width: 16px;
            height: 16px;
            margin-right: 6px;
        }
        
        /* Status colors */
        .generator-color {
            color: #e03131 !important;
        }
        
        .detector-color {
            color: #2b8a3e !important;
        }
        
        .unexposed-color {
            color: #1971c2 !important;
        }
        
        .neutralized-color {
            color: #495057 !important;
        }
        
        /* Fix colors for better visibility across browsers */
        strong[style*="color: red"], span[style*="color: red"] {
            color: #e03131 !important;
        }
        
        strong[style*="color: green"], span[style*="color: green"] {
            color: #2b8a3e !important;
        }
        
        strong[style*="color: blue"], span[style*="color: blue"] {
            color: #1971c2 !important;
        }
        
        strong[style*="color: grey"], span[style*="color: grey"] {
            color: #495057 !important;
        }
        
        /* Battle status styling */
        .battle-status {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
        }
        
        .battle-status-section {
            flex: 1;
            padding: 8px;
            border-radius: 6px;
            background-color: #f8f9fa;
        }
        
        .battle-status-section:first-child {
            margin-right: 5px;
            border-left: 3px solid #e03131;
        }
        
        .battle-status-section:last-child {
            margin-left: 5px;
            border-left: 3px solid #2b8a3e;
        }
        
        /* Responsive design for different screen sizes */
        @media (max-width: 1200px) {
            #elements-container {
                grid-template-columns: 40% 60%;
            }
            .NetworkModule_component {
                height: 340px !important;
            }
        }
        
        @media (max-width: 992px) {
            #elements-container {
                grid-template-columns: 45% 55%;
            }
            .chart-container {
                height: 120px !important;
            }
            .NetworkModule_component {
                height: 320px !important;
            }
        }
        
        @media (max-width: 768px) {
            #elements-container {
                display: flex !important;
                flex-direction: column !important;
                overflow-y: auto !important;
                height: auto !important;
                max-height: none !important;
            }
            .element-container {
                margin: 5px 0 !important;
                width: 100% !important;
            }
            body {
                overflow-y: auto !important;
                max-height: none !important;
            }
            .chart-container, .NetworkModule_component {
                width: 100% !important;
                height: 200px !important;
            }
        }
        </style>
        """

def network_portrayal(G):
    """Draw the network of agents and their states."""
    # Initialize empty portrayal
    portrayal = dict()
    
    # Add nodes
    portrayal["nodes"] = []
    for node_id in G.nodes():
        # Get agents at this node
        agents = G.nodes[node_id].get("agent", [])
        if not agents:
            continue
            
        # Get the first agent
        agent = agents[0]
        
        # Determine color based on agent state
        color = "blue"  # Default for unexposed users - matches BLUE line in chart
        size = 5       # Default size for regular users
        
        # Special colors for different agent types and states
        if agent.agent_type == "generator":
            # Check if generator is neutralized
            if hasattr(agent, 'neutralized') and agent.neutralized:
                color = "grey"   # Neutralized generators are GREY
            else:
                color = "red"    # Active generators are RED
            size = 8             # Larger size for special agents
            
        elif agent.agent_type == "detector":
            color = "green"   # Content detectors are GREEN (not tracked in chart)
            size = 8          # Larger size for special agents
            
            # Highlight detectors with victories
            if hasattr(agent, 'ai_victories') and agent.ai_victories > 0:
                size = 8 + agent.ai_victories  # Grow with victories
                
        elif agent.exposed:
            if agent.labeled:
                color = "grey"  # Labeled users are GREY - matches GREY line in chart
            else:
                color = "red"   # Exposed users are RED - matches RED line in chart
        
        # Determine label text
        label = agent.agent_type
        if agent.agent_type == "generator" and hasattr(agent, 'effectiveness'):
            # Show effectiveness for generators
            label = f"Generator ({agent.effectiveness:.1f})"
            if agent.neutralized:
                label = "Generator (neutralized)"
                
        # Add node to portrayal
        portrayal["nodes"].append({
            "id": node_id,
            "size": size,
            "color": color,
            "label": label
        })
    
    # Add edges
    portrayal["edges"] = []
    for source, target in G.edges():
        portrayal["edges"].append({
            "source": source,
            "target": target,
            "color": "black",
            "width": 1
        })
    
    return portrayal

def create_model_visualization(model_class):
    """Create a visualization server for the model."""
    # Create elements
    combined_battle = CombinedBattleElement()  # New combined element
    fix_labels = FixChartLabelsElement()  # Add the fix labels element
    custom_css = CustomCSSElement()  # Add custom CSS for demo layout
    
    # Network visualization - increased size for better visibility
    network = NetworkModule(network_portrayal, 550, 450)
    
    # Chart for user states - smaller height for Chrome window 
    user_chart = ChartModule(
        [
            {"Label": "Unexposed", "Color": "blue"},
            {"Label": "Exposed", "Color": "red"},
            {"Label": "Labeled", "Color": "grey"}
        ],
        canvas_height=110,
        canvas_width=400,
        data_collector_name="datacollector"
    )
    
    # Chart for AI battle metrics - smaller height for Chrome window
    battle_chart = ChartModule(
        [
            {"Label": "ActiveGenerators", "Color": "red"},
            {"Label": "NeutralizedGenerators", "Color": "grey"}
        ],
        canvas_height=110,
        canvas_width=400,
        data_collector_name="datacollector"
    )
    
    # Model parameters
    model_params = {
        "num_users": Slider(
            "Number of Users", 
            value=30,
            min_value=10, 
            max_value=100, 
            step=10,
            description="Number of regular users"
        ),
        "num_generators": Slider(
            "Number of Generators", 
            value=3, 
            min_value=1, 
            max_value=10, 
            step=1,
            description="Number of content generators (RED nodes)"
        ),
        "num_detectors": Slider(
            "Number of Detectors", 
            value=5, 
            min_value=1, 
            max_value=15, 
            step=1,
            description="Number of content detectors (GREEN nodes)"
        ),
        "generation_rate": Slider(
            "Generation Rate", 
            value=0.3, 
            min_value=0.01, 
            max_value=1.0, 
            step=0.01,
            description="Rate of content generation"
        ),
        "detection_rate": Slider(
            "Detection Rate", 
            value=0.3, 
            min_value=0.01, 
            max_value=1.0, 
            step=0.01,
            description="Rate of content detection"
        ),
        "detection_accuracy": Slider(
            "Detection Accuracy", 
            value=0.8, 
            min_value=0.5, 
            max_value=1.0, 
            step=0.05,
            description="Accuracy of detection"
        ),
        "spread_rate": Slider(
            "Spread Rate", 
            value=0.4, 
            min_value=0.01, 
            max_value=1.0, 
            step=0.01,
            description="Rate of content spread"
        ),
        "max_steps": Slider(
            "Maximum Steps", 
            value=100, 
            min_value=10, 
            max_value=500, 
            step=10,
            description="Maximum simulation steps before auto-stopping"
        ),
        "auto_stop_when_all_exposed": Checkbox(
            "Auto-Stop When All Exposed", 
            value=True,
            description="Stop the simulation automatically when all users have been exposed"
        )
    }
    
    # Create and return server - use the combined battle element instead of separate elements
    server = ModularServer(
        model_class,
        [custom_css, combined_battle, network, user_chart, battle_chart, fix_labels],
        "Battle of the AIs: Deepfake Content Spread Model",
        model_params
    )
    
    return server  