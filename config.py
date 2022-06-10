#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "ac87b7f2-adaa-4e87-897b-a88608b2ef11")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "bCM8Q~ySn5ktHPeGk41qAcLZniw2sOwRH545Wate")
