Scenario
You are a software architect at a major financial institution. Your company has completed a major migration and uplift of their services to be cloud native. The one laggard is the aging, batch driven, fraud detection system. The bank needs and is willing to invest in uplift of this in order to better detect fraudulent transactions and remain compliant with new requirements for real-time detection that are due to come into effect soon.

In this project you will analyze the needs of, and design a system that enables a high volume, low latency, financial fraud detection system. The system will accept transactions that the bank processes, analyze and classify these using a machine learning model, and report on the results, as well as issue alerts for transactions found to be fraudulent with a high level of confidence.

There are a number of key criteria that this new system needs to implement in order to fulfill the bank's legal requirements:

The system must provide real time analysis of transactions
Transactions that pass through the system must be captured and be replayable for compliance reasons
The system must support a peak transaction volume of 1,000 transactions per second
There must be elastic scaling of services in order to meet demand during peak load without continuing to incur peak level costs at all times
The system must provide real time alerting of finding via a frontend for fraud analysts
The solution must include observability and alerting components to allow it to be operationalised
