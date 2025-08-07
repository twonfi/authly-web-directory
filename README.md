# authly Web Directory
[![license | GPLv3](https://img.shields.io/badge/license-GPLv3-blue)](https://www.gnu.org/licenses/gpl-3.0.html)
[![built at | Hack Club](https://img.shields.io/badge/built_at-Hack_Club-%23ec3750?logo=hackclub)](https://hackclub.com)
[![part of | authly](https://img.shields.io/badge/part_of-authly-%23f1c40f)](https://authly.hackclub.com)

This is the <b>authly Web Directory</b>, which uses this great PKI system called <b>Certificate Transparency</b>.

## How does it work?
When you try to access your dashboard, it doesn't use a boring `<meta>` element, or an HTML file upload, or DNS verification&mdash;it has you issue a TLS certificate. 

You might consider this interesting as the system doesn't even touch the original certificate; instead, it uses the magic of [Certificate Transparency](//certificate.transparency.dev/) and crt.sh and other APIs to search if a certificate has been issued for a domain.

It _might_ be considered "secure" as it builds on Web PKI 
(which is powering our _certificates_, which is much more critical infrastructure than this impractical auth system). I don't _actually_ check CT properly (only used crt.sh and SSLMate API), but people are using CDNs without SRI for production. 

Here's a step-by-step overview:

### 1. Enter your domain name
You enter your domain name as usual, like `example.com`.

### 2. Certificate prompt
The system asks you to issue a certificate for a domain name like `kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.example.com`.

Here, you can use a certificate authority like Let's Encrypt. 
Any trusted CA works, but you need to wait 5 minutes for the certificate to be in the APIs. Wildcard certificates don't count; it needs to explicitly specify the domain name.
```shell
sudo certbot certonly --manual
# Enter domains: kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.example.com
# Requesting cert for kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.example.com
# Create a file containing "certKey.123" and make it available at /.well-known/acme-challenge/certKey
^Z
echo 'certKey.123' > certKey
fg
```

### 3. Confirm via Certificate Transparency
The system verifies that a valid certificate was issued using Certificate Transparency logs.

### Logout
Logout works by checking certificate revocation lists (CRLs). By revoking the certificate, the user is logged out.

APIs are flimsy, so I added a button to manually invalidate the session.

## Using this with Nest
On the website, go through the steps as usual, but enter your Nest subdomain.

Then, use this command but use the "challenge" domain name.
I'll use `kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.orpheus.hackclub.app`:
```shell
nest caddy add kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.orpheus.hackclub.app
```

Edit your `Caddyfile` (yes, HTTP):
```
http://kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.orpheus.hackclub.app {
  bind unix/.kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.orpheus.hackclub.app.webserver.sock|777
  root * /home/orpheus/pub  # You'll add your Let's Encrypt file to /home/orpheus/pub/.well-known/acme-challenge/...
  file_server
}
```

```shell
systemctl --user reload caddy
```

Set up the certificate:

Go to the domain in your browser. If it doesn't work (404 means it _did_ get a certificate):
```shell
mkdir le
mkdir le/conf
mkdir le/log
mkdir le/work
chmod -R go-rwx le

certbot --config-dir le/conf --logs-dir le/log --work-dir le/work certonly --manual
```
After the prompt, press <kbd><kbd>Control</kbd>-<kbd>Z</kbd></kbd> (<kbd>^Z</kbd>) to suspend Certbot
```
Create a file containing "certKey.123" and make it available at http://kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.orpheus.hackclub.app/.well-known/acme-challenge/certKey
Press Enter to Continue^Z
```
```shell
echo 'certKey.123' > ~/.well-known/acme-challenge/certKey
fg
```
It won't show anything after `fg`; press <kbd>Enter</kbd>
```
↵
```

If that doesn't work, then DM me

Once you get the certificate, you don't need to do anything with it.

### Revoking the certificate
```shell
certbot --config-dir le/conf --logs-dir le/log --work-dir le/work revoke kr3yse35fx8dasod6h2xs3zscj32i3dy-awd.orpheus.hackclub.app
```
