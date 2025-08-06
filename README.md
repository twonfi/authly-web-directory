# authly Web Directory
[![license | GPLv3](https://img.shields.io/badge/license-GPLv3-blue)](https://www.gnu.org/licenses/gpl-3.0.html)
[![built at | Hack Club](https://img.shields.io/badge/built_at-Hack_Club-%23ec3750?logo=hackclub)](https://hackclub.com)
[![part of | authly](https://img.shields.io/badge/part_of-authly-%23f1c40f)](https://authly.hackclub.com)

This is the <b>authly Web Directory</b>, which uses this great PKI system called <b>Certificate Transparency</b>.

## How does it work?
When you try to access your dashboard, it doesn't use a boring `<meta>` element, or an HTML file upload, or DNS verification&mdash;it has you issue a TLS certificate.

Here's a step-by-step overview:

### 1. Enter your domain name
You enter your domain name as usual, like `example.com`.

### 2. Certificate prompt
The system asks you to issue a certificate for a domain name like `kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.example.com`.

Here, you can use a certificate authority like Let's Encrypt. 
Any trusted CA works, but you need to wait 5 minutes for the certificate to be in the APIs.
Wildcard certificates don't count; it needs to explicitly specify the domain name.
```shell
sudo certbot certonly --manual
# Enter domains: kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.example.com
# Requesting cert for kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.example.com
# Create a file containing "certKey.123" and make it available at /.well-known/acme-challenge/certKey
```
```shell
echo 'certKey.123' > certKey
```

### 3. Confirm via Certificate Transparency
The system verifies that a valid certificate was issued using Certificate Transparency logs.

### Logout
Logout works by checking certificate revocation lists (CRLs). By revoking the certificate, the user is logged out.

APIs are flimsy so I added a button to manually invalidate the session.
