# Tamweel AI - 3-Minute Demo Script

This script outlines the exact steps for the final 3-minute demo flow. It showcases both the consumer-facing AI assistant and the sponsor-facing analytics dashboard.

## Overview
- **Duration**: ~3 Minutes
- **Personas**: Ahmad (Careem Driver, End User) & Admin (Sponsor / Portfolio Analyst)

---

## 🎬 Part 1: The Consumer Experience (Ahmad)

**1. Login Screen**
- **Action**: Navigate to `http://localhost:3000/login`
- **Action**: Enter credentials:
  - **Email**: `ahmad@tamweel.ai`
  - **Password**: `password123`
- **Action**: Click "Sign In"
- **Talking Point**: *"We start by logging in as Ahmad, a Careem Driver in Jordan. Traditional banks often struggle to score gig-economy workers due to irregular income streams. Tamweel’s hybrid engine has already analyzed Ahmad's alternative data—his Careem payouts, utility bills, and daily expenses."*

**2. The Dashboard & Credit Score**
- **Action**: Arrive at the main dashboard.
- **Action**: Briefly hover over the Credit Score (78/100) and the Risk Level (Low).
- **Action**: Point out the "Key Strengths" (e.g., Income Stability) and "Key Risks" (e.g., High Debt-to-Income).
- **Talking Point**: *"Ahmad sees his personalized score immediately. Because we use a hybrid ML-rules engine, we don't just give a number; we provide explainable AI insights showing exactly what factors are helping or hurting his score."*

**3. The AI Chatbot Interaction**
- **Action**: Click the floating **Tamweel AI Assistant** chat button in the bottom right corner.
- **Action**: Type the following Arabic query into the chat:
  > *"مرحباً، هل يمكنني الحصول على قرض لشراء سيارة جديدة؟"* 
  > *(Hello, can I get a loan to buy a new car?)*
- **Action**: Press **Send**.
- **Action**: Observe the loading state (`جاري المعالجة، يرجى الانتظار`).
- **Action**: Wait for the AI's contextual response (it will analyze his specific score, DTI, and the automotive intent).
- **Talking Point**: *"Ahmad can ask natural language questions. Behind the scenes, our RAG architecture securely retrieves his financial profile and intent, passing it to the LLM to provide a highly contextual, personalized, and financially sound answer in Arabic."*
- **Action**: Close the chat window.

**4. Logout**
- **Action**: Click the "Logout" button in the top navigation bar.

---

## 🎬 Part 2: The Enterprise Experience (Sponsor)

**1. Sponsor Login**
- **Action**: On the login screen, enter credentials:
  - **Email**: `admin@tamweel.ai`
  - **Password**: `admin123` *(Or whatever the admin password was set to originally)*
- **Action**: Click "Sign In".
- **Talking Point**: *"Now, let's switch perspectives. We are logging in as a Sponsor—a credit analyst or bank representative using Tamweel’s B2B portal."*

**2. Portfolio Analytics Dashboard**
- **Action**: Arrive at the Sponsor Dashboard.
- **Action**: Scroll through the aggregate metrics (Total Users, Average Score, Risk Distribution).
- **Action**: Highlight the data table at the bottom showing Ahmad, Sara (the freelance designer), and Tariq (the new micro-entrepreneur).
- **Talking Point**: *"The sponsor gets a macro view of the portfolio's health. Thanks to our role-based access control, they can monitor the risk distribution across the entire user base, allowing financial institutions to make data-driven lending decisions on previously 'invisible' credit segments."*

## 🔚 End of Demo
