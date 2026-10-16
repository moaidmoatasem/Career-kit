"""Flag anything in a tailored CV/cover note that is not backed by the facts file.

Rules (each is an error):
  TC001 a number/percentage/year that does not appear anywhere in the facts file
  TC002 a known tool/technology that does not appear in the facts file
  TC003 a term from `anonymize` (client names) appears in the text
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from apply_kit.facts import corpus

NUMBER = re.compile(r"\d+(?:[.,]\d+)?\+?%?")

# Common QA/dev tools; extend via `extra_vocabulary` in the facts file.
VOCAB = [
    "Selenium",
    "Appium",
    "Cypress",
    "Playwright",
    "Postman",
    "Bruno",
    "REST Assured",
    "JMeter",
    "k6",
    "Gatling",
    "LoadRunner",
    "TestNG",
    "JUnit",
    "Cucumber",
    "Robot Framework",
    "pytest",
    "Jenkins",
    "GitLab CI",
    "GitHub Actions",
    "Azure DevOps",
    "Docker",
    "Kubernetes",
    "Terraform",
    "AWS",
    "Azure",
    "GCP",
    "Datadog",
    "Grafana",
    "Prometheus",
    "Splunk",
    "Kafka",
    "RabbitMQ",
    "MongoDB",
    "PostgreSQL",
    "MySQL",
    "DynamoDB",
    "Oracle",
    "Redis",
    "Elasticsearch",
    "Jira",
    "Power BI",
    "Tableau",
    "SonarQube",
    "BrowserStack",
    "Sauce Labs",
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C#",
    "Salesforce",
    "SAP",
    "Dynamics 365",
    "Temenos",
    "T24",
    "Xray",
    "TestRail",
    "Zephyr",
    "SoapUI",
    "Katalon",
    "Tosca",
    "Appian",
    "ServiceNow",
    "Snowflake",
    "Databricks",
]


@dataclass(frozen=True)
class Issue:
    rule: str
    text: str

    def __str__(self) -> str:
        return f"{self.rule} {self.text}"


def check(text: str, facts: dict) -> list[Issue]:
    base = corpus(facts)
    issues: list[Issue] = []
    seen: set[str] = set()
    for m in NUMBER.finditer(text):
        tok = m.group(0)
        bare = tok.rstrip("+%")
        if bare.lower() not in base and tok.lower() not in base and tok not in seen:
            seen.add(tok)
            issues.append(Issue("TC001", f"unsupported number: {tok}"))
    vocab = VOCAB + list(facts.get("extra_vocabulary", []))
    low = text.lower()
    for term in vocab:
        pattern = rf"(?<![\w]){re.escape(term.lower())}(?![\w])"
        if re.search(pattern, low) and not re.search(pattern, base):
            issues.append(Issue("TC002", f"tool not in facts: {term}"))
    for term in facts.get("anonymize", []):
        if re.search(rf"(?<!\w){re.escape(str(term).lower())}(?!\w)", low):
            issues.append(Issue("TC003", f"must stay anonymous: {str(term)[:2]}***"))
    return issues
