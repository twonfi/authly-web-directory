from datetime import datetime, timezone
from base64 import b64decode

from django.db import models
from requests import get, JSONDecodeError
import pki_tools as pki


def check_crl_from_cert(cert: pki.Certificate) -> bool:
    """Check if a certificate is revoked using a Certificate Revocation
    List (CRL).

    This checks if a certificate is revoked by using
    ``pki_tools.Certificate`` from the URI specified from the
    certificate and checking if the certificate is in the CRL.

    :param cert: ID of certificate from crt.sh
    :type cert: pki.Certificate
    :return: Whether the certificate is valid
    :rtype: bool
    """

    print('checking crl')

    crl_uri = (cert.extensions.crl_distribution_points
           .crl_distribution_points[0].full_name[0].value)
    crl = pki.CertificateRevocationList.from_uri(crl_uri, cache_time_seconds=1)

    return not crl.get_revoked(cert.serial_number)


class Challenge(models.Model):
    domain = models.CharField(max_length=223)
    challenge_domain = models.CharField(max_length=255)
    authenticated = models.BooleanField(default=False)
    key = models.CharField(max_length=128)

    def endgame(self) -> None:
        if self.authenticated:
            self.delete()
        else:
            self.authenticated = False
            self.save()

    def check_ct(self) -> bool:
        """Check Certificate Transparency and Certificate Revocation
        List of this challenge.

        Calling this also saves the status to ``self.authenticated``.

        :return: Whether the challenge succeeded
        :rtype: bool
        """

        if self.challenge_domain[:1] == "_":
            self.authenticated = True
            self.save()
            return self.authenticated

        today = datetime.now(timezone.utc)
        print(self.challenge_domain)

        r = get(f"https://crt.sh/?Identity={self.challenge_domain}"
                f"&exclude=expired&output=json")
        if r.text:
            try:
                certs = r.json()
            except JSONDecodeError:
                pass
            else:
                print('crtsh')
                for cert in certs:
                    print('crtsh trying', cert)
                    if (
                        # Manually make timezone-aware
                        datetime.fromisoformat(cert["not_before"] + "Z")
                            < today
                            < datetime.fromisoformat(cert["not_after"] + "Z")
                    ):
                        cert = pki.Certificate.from_uri(
                            f"https://crt.sh/?d={cert["id"]}")
                        if check_crl_from_cert(cert):
                            self.authenticated = True
                            self.save()
                            return self.authenticated

        # SSLMate backup
        # (crt.sh isn't reliable but put here due to SSLMate's limits)
        s = get("https://api.certspotter.com/v1/issuances"
                f"?domain={self.challenge_domain}"
                "&expand=revocation&expand=cert_der")
        if s.text:
            try:
                certs = s.json()
            except JSONDecodeError:
                self.endgame()
                return False
            else:
                print('sslmate')
                for cert in certs:
                    print('sslmate trying', cert)
                    if (
                        datetime.fromisoformat(cert["not_before"])
                            < today < datetime.fromisoformat(cert["not_after"])
                        and not cert["revocation"]["time"]
                    ):
                        der = b64decode(cert["cert_der"].encode("ascii"))
                        cert = pki.Certificate.from_der_bytes(der)
                        if check_crl_from_cert(cert):
                            self.authenticated = True
                            self.save()
                            return self.authenticated
                self.endgame()
                return False

        return self.authenticated
