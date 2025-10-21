Changelog
=========

v0.4.0 (2025-10-21)
-------------------

- Upgrade bundled JS library to latest ALTCHA v2.2.4 release.
  https://github.com/aboutcode-org/django-altcha/pull/20

- Add support for Python 3.14
  https://github.com/aboutcode-org/django-altcha/pull/21

- Add support for providing dict values to AltchaWidget.
  https://github.com/aboutcode-org/django-altcha/pull/20

v0.3.0 (2025-07-25)
-------------------

- Add the ``ALTCHA_HMAC_KEY`` setup as part of the installation.
  A DeprecationWarning is raised when the ``ALTCHA_HMAC_KEY`` is not explicitly defined.
  Providing the ``ALTCHA_HMAC_KEY`` will be mandatory in future release.
  https://github.com/aboutcode-org/django-altcha/issues/15

- Add a ``ALTCHA_VERIFICATION_ENABLED`` setting, default to ``True``.
  This setting, when set to ``False``, allows to skip Altcha validation altogether.

v0.2.0 (2025-06-17)
-------------------

Special thanks to Alex Vandiver alexmv@zulip.com for reporting these issues.

**Important Security Note:**
If you have previously set and used a static ``ALTCHA_HMAC_KEY``,
you **must rotate this key** as part of upgrading to this release.

Earlier versions of ``django-altcha`` accepted challenges that were generated without
an expiration (``expires``) value.
This allowed older challenges to remain valid indefinitely.
As a result, any attacker with access to an old challenge could reuse it to bypass
CAPTCHA validation.

To fully benefit from the security improvements in this release,
you must also **invalidate any existing challenges** by rotating the HMAC key used
to generate and verify them.

- Add a AltchaChallengeView to allow  `challengeurl` a setup.
  This view returns a challenge as JSON to be fetched by the Altcha JS widget.
  https://github.com/aboutcode-org/django-altcha/pull/9

- Add challenge expiration support.
  Default to 20 minutes as per Altcha security recommendations.
  Can be customized through the `ALTCHA_CHALLENGE_EXPIRE` setting.
  https://altcha.org/docs/v2/security-recommendations/
  https://github.com/aboutcode-org/django-altcha/pull/7

- Add protection against replay attacks.
  Verified challenges are now marked as used and cannot be reused,
  helping to prevent repeated or spoofed submissions.
  https://github.com/aboutcode-org/django-altcha/issues/10

v0.1.3 (2025-04-15)
-------------------

- Use the value from the AltchaField `maxnumber` option, when provided, to generate the
  challenge in `get_altcha_challenge`.
  https://github.com/aboutcode-org/django-altcha/issues/5

v0.1.2 (2025-03-31)
-------------------

- Add missing templates/ and static/ directories in the distribution builds.

v0.1.1 (2025-03-31)
-------------------

- Add unit tests.

v0.1.0 (2025-03-31)
-------------------

- Initial release.
