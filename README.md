# Real-Time Transaction Anomaly Monitor

This project implements a near real-time monitoring system to detect anomalies in payment transaction data. It uses a statistical Z-score methodology to identify significant deviations from normal behavior, triggering automated alerts for incident response.

The architecture is built using Python for historical analysis, an n8n workflow for automation, an Oracle database for data storage, and Power BI for visualization.

---

## 1. Methodology: How Anomaly Thresholds Were Defined

The intelligence of the monitoring system lies in its Z-Score thresholds, which were established through a rigorous, data-driven statistical analysis of historical data.

### Approval Dips (Z-Score < -3.0)

* **Method:** Standard statistical convention.
* **Justification:** A Z-Score of -3.0 indicates an event that is **three standard deviations below the mean**. The probability of this occurring naturally is only **0.13%**, making it a statistically robust indicator of a systemic issue preventing transaction approvals.

### Failure Spikes (Z-Score > 7.0)

* **Method:** Empirical analysis of historical transaction data.
* **Justification:** Our analysis of historical data revealed that 99% of all recorded failure spikes generated a Z-Score of less than 6.79. By setting our threshold at **7.0**, we made a strategic decision to be alerted to only the **top 1% most critical** incidents, effectively filtering out 99% of operational "noise."

---

## 2. Visual Analysis: Z-Score Distribution Histogram

The visual analysis of the Z-Score distribution was fundamental in validating the failure threshold. The histogram below demonstrates a clear separation between normal operations and critical anomalies.

*(Insert the `zscore_distribution.png` image here)*

**Chart Analysis:** The histogram displays a high frequency of events with low Z-Scores, followed by a long, thin "tail" of rare, high Z-Score events. The point where this tail begins visually confirmed that a threshold of **7.0** is the ideal inflection point for identifying significant incidents.

---

## 3. Automation Architecture: n8n Workflow

The orchestration of the monitoring process is managed by the n8n automation platform, following these steps:
1.  **Scheduled Trigger:** A trigger executes the workflow every minute.
2.  **SQL Query:** The detection query is executed on the Oracle database to check the last minute.
3.  **Conditional Check (IF):** A conditional node checks if the query returned any results.
4.  **Individual Processing:** A `Split in Batches` node ensures that if multiple anomalies occur, each is processed individually.
5.  **Teams Notification:** For each anomaly, an HTML-formatted alert is sent to the incident response team's channel.
6.  **Incident Logging:** Each detected anomaly is inserted into a dedicated table (`CLOUDWALK_ANOMALIES`) in Oracle.

---

## 4. Storage and Visualization

The alert lifecycle is completed with data storage and visualization:
* **Incident Logging:** Each detected anomaly is inserted into a dedicated table (`CLOUDWALK_ANOMALIES`) in Oracle, creating an incident history.
* **Power BI Visualization:** A monitoring dashboard is connected to this table using **DirectQuery**.
* **Near Real-Time Monitoring:** By configuring an auto-page refresh in Power BI (e.g., every minute), the dashboard reflects the system's state with minimal delay, enabling a rapid incident response.

---

## 5. System Validation Through Simulation

To validate the end-to-end effectiveness of the monitoring workflow, a series of controlled simulations were performed using historical data from known incident periods. In all simulation scenarios, the system behaved as expected, correctly identifying anomalies and triggering the full alert and logging process.

The following time ranges were used for validation:
* July 13, 2025, from 00:35 to 01:30
* July 14, 2025, from 04:15 to 05:45
* July 14, 2025, from 11:40 to 12:12
