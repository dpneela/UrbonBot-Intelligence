# 🌆 UrbanBot — AI Powered Urban Monitoring & Analytics System
UrbanBot is a smart urban monitoring and analytics platform that provides structured dashboards, machine learning predictions, and real-time-style city data insights.
It integrates multiple urban domains such as traffic, crowd density, AQI, alerts, and complaints into a unified multi-page dashboard.
The system is designed to support data-driven decision making for smart city analysis and monitoring.

UrbanBot is deployed on AWS EC2 for scalable and remote dashboard access.

# 🚀 System Architecture
User → Streamlit Dashboard (AWS EC2)

→ ML/DL Models (Local + AWS S3)

→ MySQL Database (AWS RDS)

# Core Modules
# Traffic Forecasting
* Model: LSTM (.h5)
  
* Framework: TensorFlow / Keras

* Time-series prediction

# Air Quality Prediction
* Model: ARIMA (.pkl)
  
* Statistical forecasting model

# Pothole Detection
* YOLO-based road damage detection

# Crowd Density Estimation
* CNN (.h5)
  
* Image-based classification

# Complaint NLP Analysis
* Text preprocessing

* CSV-based classification pipeline

# Smart Chatbot
* AI-Powered assistant for user interaction

# 🛠 Technology Stack
**Frontend**
* Streamlit
  
**Backend**

-> Python

-> TensorFlow

-> PyTorch (Ultralytics YOLOv8)

**Database**
* MySQL (AWS RDS)
  
**Cloud**
-> AWS EC2

-> AWS S3

-> AWS RDS

**Version Control**
* Git
  
* GitHub

# ⚡ Key Highlights

* Multi-model AI integration
  
* AWS cloud deployment

* S3-based model storage
  
* AWS RDS integration
  
* Real-time image processing
  
* Time-series forecasting
  
* NLP pipeline integration
