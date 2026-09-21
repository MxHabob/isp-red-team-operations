# 01 — Operations Environment Selection Assessment

## 1. Executive Summary

Executing an authorized Red Team assessment against ISP network controls, traffic classification engines, and accounting systems introduces unique architectural demands:
1. **Strict Operator Identity Protection:** The operator's personal credentials, devices, cloud accounts, and browser profiles must be completely isolated from operational infrastructure.
2. **Deterministic Layer 2 / Layer 3 Control:** The execution environment must interact with physical or virtualized ISP CPE, PPPoE/DHCP access concentrators, DNS resolvers, and IPv4/IPv6 dual-stack gateways with packet-level fidelity.
3. **Auditability and Evidence Confidentiality:** All telemetry and evidence artifacts must be cryptographically verified and stored in encrypted, air-gapped or dedicated storage—never mixed with personal data or committed to Git.
4. **Safety and Fail-Closed Governance:** The operational control plane must enforce hard scope checks and responsive kill-switch mechanisms before any network traffic is emitted.

This assessment evaluates nine candidate operational environments across forty rigorous evaluation criteria to establish the authoritative infrastructure architecture.

---

## 2. Candidate Architectures Evaluated

### Option A: Dedicated Local Workstation
- **Description:** A dedicated physical PC or laptop provisioned solely for this Red Team operation, containing no personal data or accounts, directly connected to the test network.
- **Key Characteristics:** Full hardware control, physical NIC access (raw packet capture, VLAN tagging, PPPoE encapsulation), complete air-gap capability from personal life.

### Option B: Dedicated Local Virtual Machine (Type-1 / Type-2 Hypervisor)
- **Description:** An isolated VM (e.g., KVM/QEMU, VMware ESXi, or hardened Hyper-V) running on dedicated hardware with bridged network interfaces directly to the test CPE.
- **Key Characteristics:** Instant snapshot/rollback, fast recovery, memory isolation, software-defined network taps.

### Option C: Dedicated Physical Server (On-Premises Lab Appliance)
- **Description:** A dedicated 1U/rackmount server situated in an access-controlled physical lab with multi-port enterprise NICs connecting to ISP test lines and lab gear.
- **Key Characteristics:** High throughput, continuous monitoring, hardware security modules (HSM) capability, multi-operator support with segregated RBAC.

### Option D: Virtual Private Server (VPS) / Public Cloud Single VM (AWS/GCP/DigitalOcean)
- **Description:** A single rented virtual machine in a commercial public cloud or hosting provider executing tests over the public internet.
- **Key Characteristics:** Fast provisioning, remote reachability, but **lacks Layer 2/PPPoE/CPE visibility**, introduces third-party hypervisor/snapshot exposure, risks hosting TOS violations, and cannot test subscriber-side ISP edge controls.

### Option E: Bare-Metal Dedicated Remote Server
- **Description:** A dedicated remote bare-metal server in a tier-3/4 datacenter.
- **Key Characteristics:** High CPU/RAM, no shared hypervisor, but still remote from the ISP subscriber loop and edge BRAS/BNG access nodes.

### Option F: Isolated Private Cloud Environment (Self-Hosted OpenStack/Proxmox Cluster)
- **Description:** A private virtualization cluster operating in an owned lab environment with software-defined networking (SDN) and isolated management VLANs.
- **Key Characteristics:** Full programmatic orchestration, synthetic scale simulation, zero external third-party dependencies.

### Option G: Hybrid Multi-Tier Architecture (RECOMMENDED)
- **Description:** A distributed, tiered architecture that cleanly decouples responsibilities:
  1. **Tier 0 — Operator Management Workstation:** Dedicated air-gapped/isolated control workstation (no personal accounts).
  2. **Tier 1 — Control Plane & Orchestration Node:** Manages mission state, scope validation, safety engine, and kill-switch arbitration.
  3. **Tier 2 — Execution Agent Nodes:** Dedicated test probe appliances connected directly to the authorized ISP subscriber line / lab CPE.
  4. **Tier 3 — External Telemetry & Sensor Nodes:** Passive optical/span taps collecting flow data and PCAP metadata.
  5. **Tier 4 — Isolated Encrypted Evidence Vault:** Dedicated storage system with LUKS/BitLocker encryption, strict access control, and SHA-256 manifest validation.

---

## 3. Evaluation Criteria Matrix (40 Criteria)

| # | Criterion | A: Local Dedicated | B: Local VM | C: Lab Server | D: VPS / Cloud | G: Hybrid (Recommended) |
|---|---|---|---|---|---|---|
| 1 | Identity Separation | HIGH | HIGH | HIGH | MEDIUM | **MAXIMUM** |
| 2 | Operational Confidentiality | HIGH | HIGH | HIGH | LOW-MED | **MAXIMUM** |
| 3 | Network Isolation | HIGH | HIGH | HIGH | LOW | **MAXIMUM** |
| 4 | Administrative Control | HIGH | HIGH | HIGH | MEDIUM | **HIGH** |
| 5 | Provider Visibility (ISP side) | ACCURATE | ACCURATE | ACCURATE | DISTORTED | **ACCURATE** |
| 6 | Third-Party Infra Dependency | NONE | NONE | NONE | HIGH | **ZERO** |
| 7 | Evidence Confidentiality | HIGH | HIGH | HIGH | LOW | **MAXIMUM** |
| 8 | Evidence Storage Security | HIGH | HIGH | HIGH | MEDIUM | **MAXIMUM** |
| 9 | Cryptographic Key Protection | HIGH | HIGH | HIGH | MEDIUM | **MAXIMUM** |
| 10 | Secret Management | HIGH | HIGH | HIGH | MEDIUM | **HIGH** |
| 11 | Attack Surface Reduction | HIGH | HIGH | HIGH | MEDIUM | **MAXIMUM** |
| 12 | Host Security | HIGH | HIGH | HIGH | MEDIUM | **HIGH** |
| 13 | VM / Container Isolation | N/A | HIGH | HIGH | SHARED | **HIGH** |
| 14 | Snapshot Capability | LOW | HIGH | HIGH | HIGH | **HIGH** |
| 15 | Recovery Capability | MED | HIGH | HIGH | HIGH | **MAXIMUM** |
| 16 | Network Performance | HIGH | HIGH | MAXIMUM | VARIABLE | **HIGH** |
| 17 | Latency Fidelity | EXACT | EXACT | EXACT | SKEWED | **EXACT** |
| 18 | Packet Capture Fidelity (L2/L3) | MAXIMUM | HIGH | MAXIMUM | L3 ONLY | **MAXIMUM** |
| 19 | DNS/TLS Analysis Capability | HIGH | HIGH | HIGH | HIGH | **HIGH** |
| 20 | IPv4 Capability | FULL | FULL | FULL | VARIABLE | **FULL** |
| 21 | IPv6 / Dual-Stack Fidelity | FULL | FULL | FULL | VARIABLE | **FULL** |
| 22 | Traffic-Analysis Precision | HIGH | HIGH | HIGH | LOW | **MAXIMUM** |
| 23 | Lab Simulation Integration | HIGH | HIGH | MAXIMUM | POOR | **MAXIMUM** |
| 24 | CPE / Modem Integration | DIRECT | VIA TAP | DIRECT | IMPOSSIBLE | **DIRECT** |
| 25 | Test-Client Integration | HIGH | HIGH | HIGH | LOW | **HIGH** |
| 26 | Remote Management Security | N/A | LOCAL | RBAC | SSH/PUBLIC | **MUTUAL-TLS/WG** |
| 27 | Real-time Telemetry | HIGH | HIGH | HIGH | MEDIUM | **MAXIMUM** |
| 28 | Comprehensive Audit Logging | HIGH | HIGH | HIGH | MEDIUM | **MAXIMUM** |
| 29 | Auditability / Chain of Custody | HIGH | HIGH | HIGH | LOW | **MAXIMUM** |
| 30 | Kill-Switch Responsiveness | IMMEDIATE | IMMEDIATE | IMMEDIATE | NETWORK-DEP | **IMMEDIATE** |
| 31 | Scope Enforcement Enforcement | STRICT | STRICT | STRICT | STRICT | **STRICT (Fail-Closed)** |
| 32 | Financial Cost | LOW-MED | LOW | MED | RECURRING | **BALANCED** |
| 33 | Infrastructure Reliability | HIGH | HIGH | HIGH | HIGH | **HIGH** |
| 34 | High Availability | N/A | MED | HIGH | HIGH | **HIGH** |
| 35 | Horizontal Scalability | LOW | MED | HIGH | HIGH | **HIGH** |
| 36 | Data Residency Compliance | 100% OWNED | 100% OWNED | 100% OWNED | UNCERTAIN | **100% JURISDICTIONAL** |
| 37 | Legal / Authorization Alignment | CLEAN | CLEAN | CLEAN | TOS RISKS | **COMPLIANT** |
| 38 | Operational Complexity | LOW | LOW-MED | MED | LOW | **MODERATE** |
| 39 | Failure Recovery & Rollback | MED | RAPID | RAPID | RAPID | **AUTOMATED** |
| 40 | Long-Term Maintainability | HIGH | HIGH | HIGH | MEDIUM | **MAXIMUM** |

---

## 4. Why Public VPS/Cloud Alone is Unsuitable for ISP Red Team Operations

1. **Missing Subscriber Edge Visibility:** A VPS lives in a datacenter upstream of the internet backbone. It cannot test captive portal redirection, PPPoE/DHCP option manipulation, subscriber VLAN isolation, TR-069 ACS interactions, or customer-premises traffic shaping.
2. **Third-Party Exposure & Multi-Tenancy:** Hypervisor co-tenancy and cloud provider administrative snapshots introduce risk of sensitive evidence leakage.
3. **Terms of Service (TOS) Constraints:** Network scanning, protocol fuzzing, and egress traffic manipulation frequently trigger automated cloud abuse filters.
4. **Identity Linkage:** Cloud accounts require personal billing credit cards, phone verification, and corporate emails, creating accidental identity linkages unless complex organizational provisioning is in place.

---

## 5. Assessment Conclusion

The **Hybrid Multi-Tier Architecture (Option G)** is selected as the optimal operational environment. It guarantees complete identity isolation, full Layer 2/3 fidelity with subscriber modems/CPEs, deterministic kill-switch responsiveness, and cryptographically verified evidence storage.
