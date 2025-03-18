# Misinformation Spread Simulation

## **§A. Overview of the Current Implementation State**
This interim prototype models misinformation spread across social media networks using an agent-based simulation built with the Mesa framework. The model comprises UserAgent objects representing various user roles, including susceptible, spreader, fact-checker, influencer, and skeptical agents. Each agent interacts within a network generated either as a small-world or random network. Current agent interactions simulate misinformation spread and labeling based on fixed probabilities. The simulation collects data on infected and labeled content and calculates precision, recall, and F1-score metrics for fact-checking effectiveness. Visualization includes real-time statistics and network graph portrayals showing infection spread and labeling activity.

### **Key Features Implemented:**
- **Agent-Based Modeling (ABM)**: Users are classified into five roles: 
  - **Spreader** 🔴 (actively spreading misinformation)
  - **Fact Checker** 🔵 (labeling AI-generated content)
  - **Influencer** 🟠 (amplifying misinformation)
  - **Skeptical** 🟣 (questioning misinformation but still susceptible)
  - **Susceptible** ⚫ (neutral users)
- **Network Structure**: 
  - Agents interact on a **Small-World** or **Erdős–Rényi** graph to simulate realistic connections.
- **Agent Interactions**:
  - Spreaders and influencers increase misinformation spread.
  - Fact-checkers label misinformation, reducing its impact.
  - Skeptical users sometimes ignore fact-checks.
- **Data Collection & Visualization**:
  - **Live visualization** of misinformation spread.
  - **Line graph tracking** infected and labeled content over time.
  - **Legend & stats panel** to track simulation progress.
- **Simulation Controls**:
  - Model runs until misinformation reaches equilibrium (no further spread).
  - Stopping condition when **no new infections or fact-checking occurs**.

---

## **§B. How to Run the Simulation**
### **1. Install Dependencies**
Ensure you have Python installed (preferably Python 3.9+).  
Run the following command to install the required dependencies:
```bash
pip install -r requirements.txt
```
### **2. Running the Simulation**
1.  Clone the repository.
    ```bash
    git clone https://github.com/vidhipandya29 battle-of-the-ais.git
    ```

2.  Navigate to the project directory.
    ```bash
    cd battle-of-the-ais/src
    ```

3.  Run the Simulation:   
    ```bash
    python server.py
    ```
    After execution, the simulation will start and open a web interface automatically in the browser at:
     ```
    http://127.0.0.1:[PORT]
    ```
  
    The port is dynamically assigned.

4.  After the simulation completes, a CSV file named `misinformation_simulation_results.csv` containing the collected simulation data will be generated in your current directory.
    
### Controls

*   **Start:** The simulation runs automatically.
    
*   **Stop:** Manually stops the simulation.
    
*   **Step:** Advances the simulation one step at a time.
    
*   **Reset:** Restarts the simulation.
    
---

## **§C. Limitations and Planned Improvements**

### Current Limitations

*   The model does not differentiate between human and bot interactions, limiting realism.
    
*   Misinformation spread currently uses fixed probabilities, which does not fully capture viral dynamics or feed algorithm effects.
    
*   Users have limited ability to dynamically adjust parameters during simulation runs.
    
*   Visualization lacks detailed differentiation between types of agents and strength of connections.
    
*   Data collection currently focuses only on infection and labeling without broader content dynamics analysis.
    

### Planned Improvements for Next Phase

*   Introduce bot-specific behaviors for misinformation and fact-checking agents to differentiate from human interactions.
    
*   Implement a realistic feed algorithm to model content spread based on engagement and virality.
    
*   Add interactive UI sliders to dynamically adjust simulation parameters, including misinformation spread probability, fact-checking effectiveness, and bot-to-human ratios.
    
*   Enhance visualization by clearly distinguishing bot agents, applying weighted edges to represent misinformation strength, and using distinctive node representations.
    
*   Expand data collection to include misinformation saturation metrics, providing deeper analytical insights into content dynamics over simulation steps.
