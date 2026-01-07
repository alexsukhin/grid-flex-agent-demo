# Grid Flex Agent Demo
A demo showing how AI agents can coordinate grid flexibility actions in response to predicted feeder overloads. Built for the AI Agent Hackathon x DEG finalist round.

# Overview
This demo simulates a three-agent system that:
1. Predicts feeder overloads
2. Discovers & selects DER flexibility using a simple optimisation step
3. Dispatches chosen actions through a mock Beckn-style flow
It reflects the core orchestration loop described in the DEG hackathon materials and the Demand Flexibility flow (discover → confirm → status) defined in the official guide.

# Architecture
- Prediction Agent: forecasts load and triggers flexibility requests
- Optimisation Agent: selects the best DERs using a small knapsack-style model
- Dispatch Agent: activates chosen DERs and logs decisions

## Demo Video

Check out the demo of Grid Flex Agent on YouTube:

[Watch the demo on YouTube](https://www.youtube.com/watch?v=Fs1ccy__-T8)

> Click the link to watch the full video on YouTube.
