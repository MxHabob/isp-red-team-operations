# Data Classification Policy

## Classification Levels

| Level | Description | Examples |
|---|---|---|
| **PUBLIC** | Information that can be freely shared | Project README, methodology description, glossary |
| **INTERNAL** | Internal project information | Architecture docs, scenario designs, test plans |
| **CONFIDENTIAL** | Sensitive operational data | Scope definitions, operator identities, environment configs |
| **RESTRICTED** | Evidence and findings | Test results, evidence manifests, finding details, PCAP metadata |
| **HIGHLY_RESTRICTED** | Credentials and raw sensitive data | API keys, tokens, raw PCAP, customer data, provider exports |

## Handling Requirements

| Requirement | PUBLIC | INTERNAL | CONFIDENTIAL | RESTRICTED | HIGHLY_RESTRICTED |
|---|---|---|---|---|---|
| **Storage** | Git | Git | Git (metadata) | External store | External encrypted store |
| **Encryption at rest** | No | No | Optional | Required | Required |
| **Access control** | Open | Team | Need-to-know | Named operators | Named operators + approval |
| **Retention** | Indefinite | Project lifetime | Project lifetime | Per policy | Per policy + legal |
| **Logging** | No | No | Optional | Required | Required |
| **Git allowed** | Yes | Yes | Metadata only | Metadata only | NEVER |
| **Export** | Free | Team approval | Lead approval | Lead + legal | Lead + legal + data owner |

## What MUST NOT be in Git

- Raw PCAP files (`.pcap`, `.pcapng`, `.cap`)
- Credentials, tokens, API keys (`.pem`, `.key`, `.p12`, `.pfx`, `.env`)
- Customer data or real subscriber information
- Production exports from ISP systems
- Raw sensitive logs containing PII
- Unredacted provider infrastructure details

## Evidence Classification

All evidence items must be classified at creation time. The default classification is **RESTRICTED**. Evidence containing subscriber data, credentials, or raw network captures must be classified as **HIGHLY_RESTRICTED**.
