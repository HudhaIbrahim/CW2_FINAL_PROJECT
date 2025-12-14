# Multi-Domain Intelligence Platform

**STUDENT ID:** M01088116  
**COURSE:** AI and Data Science  
**MODULE:** CST1510

##  System Overview

A unified web application built with Python and Streamlit that provides data-driven insights across three domains: Cybersecurity, Data Science, and IT Operations. The platform features secure authentication, interactive dashboards, real-time analytics, and AI-powered assistance.

##  Key Features

### Authentication & Security
- Bcrypt password hashing
- Role-based access control (Admin, Analyst, User)
- SQL injection protection

### Dashboards
- **Cybersecurity Dashboard** - Incident tracking, threat analysis, attack type visualization
- **Data Science Dashboard** - Dataset management, resource consumption analysis
- **IT Operations Dashboard** - Ticket management, staff performance monitoring

### Analytics & Visualizations
- Interactive Plotly charts (pie, bar, line charts)
- Real-time KPI metrics
- Time-series trend analysis

### AI Integration
- GPT-4.1-mini powered chatbots
- Domain-specific expert guidance
- Streaming responses

##  How to Run

### 1. Install Dependencies
pip install streamlit pandas plotly bcrypt openai

### 2. Launch Application
streamlit run Home.py

### 3. Login
Register with an account first then login


### 4. Navigate
Select a dashboard from the drop down menu and click go to access domain specific features
