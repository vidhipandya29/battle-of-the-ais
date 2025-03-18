# Battle of the AIs: Deepfake Content Spread Simulation

This project simulates the spread of AI-generated content (deepfakes) in a social network, along with the dynamics between content generators and detectors. It's implemented using the Mesa agent-based modeling framework.

## Features

- Simulates a social network with three types of agents:
  - Regular users who can be exposed to and spread content
  - Content generators who create and spread deepfake content
  - Content detectors who try to identify and label AI-generated content
- Interactive visualization showing the network structure and agent states
- Real-time charts tracking the spread of content
- Adjustable parameters to experiment with different scenarios

## Running the Simulation
1. Make sure you have Python 3.8 or higher installed

2. Clone the repository.
    ```bash
    git clone https://github.com/vidhipandya29 battle-of-the-ais.git
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Navigate to the src directory:
    ```bash
    cd src
    ```

5. Run the server:
    ```bash
    python server.py
    ```

6. Open your web browser and go to:
    ```
    http://localhost:8521
    ```

## Parameters

You can adjust the following parameters in the web interface:

- Number of Users: Total number of regular users in the network
- Number of Content Generators: Number of agents creating deepfake content
- Number of Content Detectors: Number of agents trying to identify AI content
- Content Generation Rate: How frequently new content is created
- Detection Rate: How often detectors check content
- Detection Accuracy: How accurate the detectors are
- Content Spread Rate: How quickly content spreads between users

## Visualization

The visualization includes:
- Network view showing agents and their connections
- Color coding:
  - Blue: Unexposed users
  - Red: Content generators and exposed users
  - Green: Content detectors
  - Grey: Users with labeled content
- Charts tracking the population of unexposed, exposed, and labeled users
- AI to AI interaction visualization showing the dynamic between generator and detector AIs
- Dashboard displaying key metrics:
  - Active and neutralized generators
  - Active detectors and their success rates
  - User exposure statistics
- Optimized layout with:
  - Parameter sliders on the left
  - Network visualization in the center
  - Status dashboard on the right
  - Charts at the bottom

## Project Structure

```
src/
├── model.py          # Core simulation model
├── visualization.py  # Visualization settings
└── server.py        # Server to run the simulation
```

## Overview of Current Implementation State

This is a partial functional prototype that simulates the interaction between AI-generated deepfake content and detection systems on social media platforms, with a focus on user behavior and content labeling. The simulation models:

- Social media users who can interact with and spread content
- AI content generators that create and spread deepfake content
- AI detectors that identify and label AI-generated content
- Network-based interactions between these agents
- Visualization of content spread and labeling effectiveness

The current implementation includes:
- Basic agent interactions in a network structure
- Content generation and spread mechanics
- Detection and labeling system
- Real-time visualization of the network state
- Data collection for analyzing spread patterns

### Interpreting the Visualization
- Blue nodes: Unexposed users
- Red nodes: Users exposed to unlabeled AI content
- Grey nodes: Users exposed to labeled AI content
- Large red nodes: Content generators
- Large green nodes: Content detectors
- The graph shows the real-time counts of unexposed, exposed, and labeled users
- The AI Battle Dashboard displays generator and detector performance metrics
- Charts track both user state distribution and AI effectiveness over time

## Limitations and Planned Improvements

Current limitations:
1. Simple interaction model between users
2. Basic content spread mechanics
3. Limited user engagement metrics

Planned improvements:
1. Enhanced user behavior modeling:
   - Add likes, comments, and shares as distinct interactions
   - Implement user credibility scores
2. Improved content detection:
   - Add detection delay mechanics
   - Implement false positive/negative rates
3. Advanced analytics:
   - Track content virality metrics
   - Measure effectiveness of labeling strategies
4. UI/UX enhancements:
   - Add more detailed node information
   - Implement timeline visualization 
