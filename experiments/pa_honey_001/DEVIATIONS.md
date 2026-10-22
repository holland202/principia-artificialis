# PA-HONEY-001: deviations from the registration (append-only, W9)

The registration ([PREREG.md](PREREG.md), commit `0c5f79b`) is unchanged. Each deviation below is recorded when it happens, before any sensor log is read.

## D1 (2026-10-22): one sensor instead of two; different size and architecture

- **Registered:** two new Azure VMs, one in West US 2 and one in Central US.
- **Actual:** one sensor, `pa-honey-c`, in Central US, size `Standard_B2ps_v2` (ARM64, Ubuntu 24.04 arm64 image). The sensor and classifier are the pinned, hash-checked files. Its startup line reads `PA-HONEY started 2026-10-22T11:58:20Z`, and both services report `active` (owner-run `az vm run-command`).
- **Why (Azure errors, owner-observed):**
  - West US 2: `QuotaExceeded`, Total Regional Cores limit 4, usage 4.
  - Central US, `Standard_B2as_v2`: `SkuNotAvailable`.
  - East US, `Standard_B2ps_v2`: `SkuNotAvailable`.
  - East US 2, `Standard_B2ats_v2`: `SkuNotAvailable`.
- **Effect:** H2 ("across both sensors") is scored on one sensor. A "no" is even weaker evidence than registered, and the write-up will say so. H1's "each sensor" applies to this one sensor.

## D2 (2026-10-22): inbound ports opened about 2 h 40 min after the sensor started

- The VM was created with no inbound rules, as designed. Ports 80 and 443 were opened by a separate owner command later, during the owner's 09:38–09:39 CDT (14:38–14:39 UTC) Cloud Shell session. The exact time is in the Azure activity log; it has not been read yet.
- **H1 as registered** counts from the first startup line (11:58:20Z), when the internet **could not reach** the sensor. H1 will be scored exactly as registered and kept, whatever the result.
- **H1b (post hoc, added here before reading any log; it does not replace H1):** at least one non-canary request within 60 minutes of the port-opening time recorded in the Azure activity log. It is labelled post hoc, and it is not confirmatory.

## Not yet done

- **C1 canary:** not sent yet. Until it is sent and detected, the instrument is not validated, and H2 cannot be scored "no".

Recorded by Claude (Anthropic, Opus 5.5) at Chad Holland's direction. Human review level: direction only.

## D3 (2026-10-22): first canary attempt did not connect

- At 09:42 CDT (14:42 UTC) the owner sent the canary from **Azure Cloud Shell**, not Termux. curl printed `000`: no HTTP response, so the request never reached the sensor or was refused before HTTP.
- Claude's workspace cannot reach the sensor's IP: its outbound proxy answered `503` itself, at connect time 0.001 s. That attempt says nothing about the sensor.
- **Status:** C1 NOT PASSED. The instrument is unvalidated. The cause is not yet diagnosed. Candidates, each to be checked on the VM and the network security group, not guessed: the inbound rule not applied, the service not listening on the public interface, or Cloud Shell's outbound path.
