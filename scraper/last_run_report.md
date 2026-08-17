# Directory check — run report

Run at: 2026-08-17T05:38:41Z

- Checked: 53
- Link OK: 28
- Confirmed broken (server returned an error): 12
- Unverified (network/SSL issue, not confident either way): 13
- Skipped (robots.txt): 0
- OK but no attachment/internship keyword found: 17

## Confirmed broken — the server itself returned an error

These got a real HTTP error response, which is a fairly confident signal.

- **Cellulant Kenya** — HTTP 403 — https://cellulant.io/careers
- **Davis & Shirtliff Ltd** — HTTP 404 — https://www.dayliff.com/careers
- **Equity Bank Kenya** — HTTP 404 — https://equitygroupholdings.com/careers
- **Family Bank Kenya** — HTTP 404 — https://www.familybank.co.ke/careers
- **Huawei Technologies Kenya** — HTTP 404 — https://www.huawei.com/en/careers
- **Interswitch East Africa** — HTTP 404 — https://interswitchgroup.com/careers
- **KCB Bank Kenya** — HTTP 404 — https://ke.kcbgroup.com/about/careers
- **Kenya Pipeline Company (KPC)** — HTTP 404 — https://www.kpc.co.ke/careers
- **Kenya Power (KPLC)** — HTTP 403 — https://www.kplc.co.ke/careers
- **KPMG East Africa** — HTTP 404 — https://kpmg.com/ke/en/careers
- **NHIF – National Hospital Insurance Fund** — HTTP 404 — https://www.nhif.or.ke
- **UNICEF Kenya** — HTTP 403 — https://www.unicef.org/careers/internships

## Unverified — worth a manual click before trusting this

The request failed at the network level (timeout, connection refused, or an
SSL/certificate error), even after a retry. This is often a corporate firewall
or bot-protection rejecting an automated request that a real browser would get
through fine — it is NOT strong evidence the link is actually dead. Open a few
of these yourself before assuming anything is wrong.

- **ABSA Bank Kenya** — SSLError: HTTPSConnectionPool(host='www.absa.co.ke', port=443): Max retries exceeded with url: /about-us/careers/ (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1010)'))) — https://www.absa.co.ke/about-us/careers/
- **DTB – Diamond Trust Bank** — SSLError: HTTPSConnectionPool(host='www.dtbgroup.com', port=443): Max retries exceeded with url: /careers (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1010)'))) — https://www.dtbgroup.com/careers
- **ICTA – ICT Authority of Kenya** — ConnectTimeout: HTTPSConnectionPool(host='icta.go.ke', port=443): Max retries exceeded with url: / (Caused by ConnectTimeoutError(<HTTPSConnection(host='icta.go.ke', port=443) at 0x7f43f2c76360>, 'Connection to icta.go.ke timed out. (connect timeout=15)')) — https://icta.go.ke
- **Kenya National Bureau of Statistics (KNBS)** — SSLError: HTTPSConnectionPool(host='www.knbs.or.ke', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)'))) — https://www.knbs.or.ke
- **Kenya Ports Authority (KPA)** — SSLError: HTTPSConnectionPool(host='www.kpa.co.ke', port=443): Max retries exceeded with url: /careers (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)'))) — https://www.kpa.co.ke/careers
- **Kenya Revenue Authority (KRA)** — SSLError: HTTPSConnectionPool(host='kra.go.ke', port=443): Max retries exceeded with url: /careers (Caused by SSLError(SSLCertVerificationError(1, "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Hostname mismatch, certificate is not valid for 'kra.go.ke'. (_ssl.c:1010)"))) — https://kra.go.ke/careers
- **Momentum Labs Africa** — ConnectionError: HTTPSConnectionPool(host='momentumlabs.africa', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPSConnection(host='momentumlabs.africa', port=443): Failed to resolve 'momentumlabs.africa' ([Errno -2] Name or service not known)")) — https://momentumlabs.africa
- **Nairobi City County – City Hall** — ConnectTimeout: HTTPSConnectionPool(host='www.nairobi.go.ke', port=443): Max retries exceeded with url: / (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.nairobi.go.ke', port=443) at 0x7f43f2999c70>, 'Connection to www.nairobi.go.ke timed out. (connect timeout=15)')) — https://www.nairobi.go.ke
- **NTSA – National Transport & Safety Authority** — SSLError: HTTPSConnectionPool(host='www.ntsa.go.ke', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)'))) — https://www.ntsa.go.ke
- **Ramco Group Kenya** — ConnectionError: HTTPSConnectionPool(host='www.ramco.co.ke', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("HTTPSConnection(host='www.ramco.co.ke', port=443): Failed to resolve 'www.ramco.co.ke' ([Errno -2] Name or service not known)")) — https://www.ramco.co.ke
- **Sendy Ltd** — ConnectionError: HTTPSConnectionPool(host='www.sendyit.com', port=443): Max retries exceeded with url: /careers (Caused by NameResolutionError("HTTPSConnection(host='www.sendyit.com', port=443): Failed to resolve 'www.sendyit.com' ([Errno -5] No address associated with hostname)")) — https://www.sendyit.com/careers
- **Strathmore University – @iLabAfrica** — ConnectTimeout: HTTPSConnectionPool(host='www.ilabafrica.ac.ke', port=443): Max retries exceeded with url: / (Caused by ConnectTimeoutError(<HTTPSConnection(host='www.ilabafrica.ac.ke', port=443) at 0x7f43f30e61b0>, 'Connection to www.ilabafrica.ac.ke timed out. (connect timeout=15)')) — https://www.ilabafrica.ac.ke
- **University of Nairobi – ICT Centre** — ConnectTimeout: HTTPSConnectionPool(host='ict.uonbi.ac.ke', port=443): Max retries exceeded with url: / (Caused by ConnectTimeoutError(<HTTPSConnection(host='ict.uonbi.ac.ke', port=443) at 0x7f43f2c4a9f0>, 'Connection to ict.uonbi.ac.ke timed out. (connect timeout=15)')) — https://ict.uonbi.ac.ke

## Loaded fine, but no internship/attachment keyword found

Not necessarily a problem — some programs sit behind a login or a
separate portal — but these are worth a skim next time you're updating listings.

- **Africa's Talking** — https://www.africastalking.com/careers
- **Airtel Kenya** — https://airtelkenya.com/career
- **Amref International University** — https://amref.org/careers
- **Andela Kenya** — https://www.andela.com
- **Augusta Software House Ltd** — https://www.augusta.co.ke
- **Co-operative Bank of Kenya** — https://co-opbank.co.ke/careers
- **Craft Silicon** — https://craftsilicon.com/careers
- **Deloitte East Africa** — https://www.deloitte.com/ke/en/careers
- **iHub Nairobi** — https://ihub.co.ke
- **Liquid Intelligent Technologies** — https://www.liquid.tech/careers
- **Microsoft Africa Development Centre** — https://careers.microsoft.com
- **Moringa School** — https://moringaschool.com/careers
- **Nairobi Garage** — https://nairobigarage.com
- **Onfon Media** — https://www.onfonmedia.com
- **Sybrin Kenya** — https://www.sybrin.com/careers
- **UN-Habitat** — https://careers.un.org
- **Zuku (Wananchi Group)** — https://www.zuku.co.ke/careers
