from datetime import datetime, timezone

from django.db import models
from requests import get, JSONDecodeError
import pki_tools as pki


def check_crl_from_crtsh(crtsh_id: int) -> bool:
    """Check if a certificate is revoked using a Certificate Revocation
    List (CRL).

    This checks if a certificate is revoked by downloading its CRL from
    the URI specified from the certificate and checking if the
    certificate (from crt.sh) is in the CRL.

    :param crtsh_id: ID of certificate from crt.sh
    :type crtsh_id: int
    :return: Whether the certificate is valid
    :rtype: bool
    """

    cert = pki.Certificate.from_uri(f"https://crt.sh/?d={crtsh_id}")

    crl_uri = (cert.extensions.crl_distribution_points
           .crl_distribution_points[0].full_name[0].value)
    crl = pki.CertificateRevocationList.from_uri(crl_uri, cache_time_seconds=1)

    return not crl.get_revoked(cert.serial_number)


class Challenge(models.Model):
    domain = models.CharField(max_length=223)
    challenge_domain = models.CharField(max_length=255)
    authenticated = models.BooleanField(default=False)
    key = models.CharField(max_length=255)

    def endgame(self) -> None:
        if self.authenticated:
            self.delete()
        else:
            self.authenticated = False

    def check_ct(self) -> bool:
        """Check Certificate Transparency and Certificate Revocation
        List of this challenge.

        Calling this also saves the status to ``self.authenticated``.

        :return: Whether the challenge succeeded
        :rtype: bool
        """

        today = datetime.now(timezone.utc)

        r = get(f"https://crt.sh/?Identity={self.challenge_domain}"
                f"&exclude=expired&output=json")
        if r.text:
            try:
                certs = r.json()
            except JSONDecodeError:
                pass
            else:
                for cert in certs:
                    if (
                        # Manually make timezone-aware
                        datetime.fromisoformat(cert["not_before"] + "Z")
                            < today
                            < datetime.fromisoformat(cert["not_after"] + "Z")
                    ):
                        if check_crl_from_crtsh(cert["id"]):
                            self.authenticated = True
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
                for cert in certs:
                    if (
                        datetime.fromisoformat(cert["not_before"])
                            < today < datetime.fromisoformat(cert["not_after"])
                        and not cert["revocation"]["time"]
                    ):
                        self.authenticated = True
                    return self.authenticated
                self.endgame()

        return self.authenticated
