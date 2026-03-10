# ALC Breach Screening Tool
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Docker](https://img.shields.io/badge/Docker-supported-blue)
![Tests](https://img.shields.io/badge/Tests-Pytest-green)

## Overview

This project implements a Python-based breach screening tool developed for **Antrim Logistics Company (ALC)**. The application scans a list of customer email addresses against publicly available breach intelligence APIs to identify whether the accounts have appeared in known data breaches.

The tool helps security analysts identify potentially compromised customer accounts and supports proactive mitigation measures such as password resets or additional authentication checks.

The application is designed with **DevOps best practices**, including modular architecture, automated testing, logging, configuration management, and containerisation.

---

# Features

-CSV email input processing  
-Integration with breach intelligence APIs  
-Multi-provider support (LeakCheck and IntelX)  
-Retry logic with exponential backoff  
-Provider health monitoring and failover  
-Structured logging for observability  
-Automated unit testing with coverage reporting  
-Docker containerisation for reproducible environments  
-Analyst summary reporting  

---

# Project Structure

```
ALC_Breach_Screening
│
├── src
│   ├── main.py
│   ├── screening_service.py
│   ├── logger_config.py
│   └── providers
│       ├── base_provider.py
│       ├── intelx_client.py
│       └── leakcheck_client.py
│
├── tests
│   ├── test_main.py
│   ├── test_screening_service.py
│   ├── test_intelx.py
│   └── test_leakcheck.py
│
├── config.yaml
├── requirements.txt
├── email_list.csv
├── output_result.csv
├── Dockerfile
└── README.md
```


---

# Architecture

The system follows a **modular service architecture** separating core logic, API integrations, and input/output handling.

```
CSV Input
   ↓
main.py
   ↓
ScreeningService
   ↓
Provider Layer
 ├ LeakCheckClient
 └ IntelXClient
   ↓
External Breach Intelligence APIs
   ↓
Processed Results
   ↓
CSV Output + Analyst Summary
```


This architecture allows additional breach intelligence providers to be integrated easily in the future.

---


# Installation

### 1. Clone the repository

```
git clone https://github.com/itsthecommander-bot/alc-breach-screening.git
cd ALC_Breach_Screening
```

---

# Requirements

-Python 3.10 or newer  
-Docker (optional for containerised execution)  
-LeakCheck API key  
-IntelX API key


### 2. Create a virtual environment

```
python -m venv venv
```

Activate the environment:

**Windows**

```
venv\Scripts\activate
```

**Linux / macOS**
```
source venv/bin/activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

# Configuration

API credentials are stored securely using environment variables.

Create a `.env` file:

Example `.env` file:

```
LEAKCHECK_API_KEY=your_leakcheck_api_key
INTELX_API_KEY=your_intelx_api_key
```

Note: The `.env` file should **not be committed to version control**.  
Add `.env` to `.gitignore` to protect API credentials.

The application configuration is defined in:

`config.yaml`

```yaml
api:
  leakcheck:
    base_url: https://leakcheck.io/api/public
    timeout: 10

  intelx:
    base_url: https://free.intelx.io
    timeout: 10
```



# Running the Application

Run the program with:

```
python -m src.main
```

The application will prompt the user to select the breach intelligence provider:

```
Select primary provider:
1. LeakCheck
2. IntelX
```

The program will then:

-Read email addresses from the input file `email_list.csv`  
-Query the selected API  
-Process the responses  
-Output the results to `output_result.csv`  
-Display an analyst summary

### Example Output

```
--- Analyst Summary ---
Total Valid Emails Processed: 4
Total Breached Emails: 2

Top Breach Sources:
Jobandtalent.com: 1
EyeEm.com: 1
pt.airecampingcar.com: 1
Taobao.com: 1
housesholidays.com: 1
```


# Testing

Unit tests were implemented using pytest with coverage reporting.

Run tests with:

```
pytest --cov=src --cov-report=term-missing
```

### Example Output

```
9 passed in 9.27s
TOTAL coverage: 84%
```

Testing includes:

-API response parsing
-CSV input/output handling
-retry logic and failure scenarios
-provider failover behaviour


# Docker Deployment

The application can be executed within a containerised environment using Docker.

### Build the container

```
docker build -t alc-breach-screening .
```

### Run the container

```
docker run -it --env-file .env alc-breach-screening
```

Docker ensures consistent execution across environments and demonstrates containerised deployment practices.


# Logging & Observability

The application implements structured logging using Python's logging module.

Logs include:

-INFO – processing status
-DEBUG – detailed execution tracing
-WARNING – retry attempts
-ERROR – API failures

Logs are written to:

`screening_service.log`

This enables troubleshooting and operational monitoring.


# Security & Ethical Considerations

This tool is intended for defensive security analysis only.

Key ethical considerations:

-Only authorised datasets should be used
-No real customer data should be processed without consent
-API usage must comply with provider terms of service
-Data handling must comply with GDPR principles, including data minimisation and purpose limitation

All testing in this project uses synthetic or publicly available breach data.


# Limitations

-Free API tiers restrict the number of daily queries
-Breach intelligence coverage depends on provider datasets
-Some breaches may not be publicly accessible
-Results should be treated as indicators of exposure, not definitive proof of compromise


# Future Improvements

Potential enhancements include:

-asynchronous API requests for improved performance
-additional breach intelligence providers
-automated CI pipelines for testing
-visual dashboards for breach statistics


# Conclusion

This project demonstrates a production-style Python application implementing API-driven automation using modern DevOps practices including:

-modular architecture
-automated testing
-configuration management
-logging and observability
-containerisation with Docker

The tool provides a scalable foundation for automated breach intelligence screening within an organisational security workflow.

# License

This project is provided for educational purposes as part of the Cloud Development Technologies coursework.