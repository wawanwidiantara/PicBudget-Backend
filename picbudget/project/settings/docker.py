if IN_DOCKER:  # type: ignore
    print("Running in Docker mode ...")
    assert MIDDLEWARE[:1] == [  # type: ignore
        "django.middleware.security.SecurityMiddleware",
    ]
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # type: ignore # noqa: F821
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
