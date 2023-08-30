#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

# Copyright 2023 Tiger Computing Ltd
# Author: Chris Boot <bootc@bootc.net>

"""
NATS PubSub to HTTP Webhook adapter.
"""

import asyncio
import logging
import os
import re
import ssl
import sys
from functools import partial
from types import SimpleNamespace

import aiohttp

import nats

DEFAULT_URL = "nats://localhost:4222"
DEFAULT_SUBJECT = "test"
DEFAULT_WEBHOOK = "http://localhost:8080"

cfg = SimpleNamespace()
log = logging.getLogger("nats_subscribe")


def configure() -> None:
    envs = {
        "DEBUG",
        "NATS_URL",
        "NATS_USER",
        "NATS_PASSWORD",
        "NATS_CREDS",
        "NATS_NKEY",
        "NATS_CERT",
        "NATS_KEY",
        "NATS_CA",
        "NATS_TIMEOUT",
        "SUBJECT",
        "WEBHOOK",
    }

    for env in envs:
        setattr(cfg, env.lower(), os.environ.get(env))

    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if cfg.debug else logging.INFO,
    )


async def nats_error_callback(ex: Exception) -> None:
    log.error("nats: encountered error", exc_info=ex)
    sys.exit(1)


async def connect() -> nats.NATS:
    options = {
        "servers": re.split(r"[, ]+", cfg.nats_url or DEFAULT_URL),
        "user": cfg.nats_user,
        "password": cfg.nats_password,
        "user_credentials": cfg.nats_creds,
        "nkeys_seed": cfg.nats_nkey,
    }

    if cfg.nats_cert or cfg.nats_key or cfg.nats_ca:
        tls = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

        if cfg.nats_ca:
            tls.load_verify_locations(cfg.nats_ca)

        if cfg.nats_cert or cfg.nats_key:
            tls.load_cert_chain(cfg.nats_cert, cfg.nats_key)

        options["tls"] = tls

    if cfg.nats_timeout is not None:
        options["connect_timeout"] = int(cfg.nats_timeout)

    return await nats.connect(
        error_cb=nats_error_callback,
        verbose=(cfg.debug is not None),
        **options,
    )


async def handle_message(
    msg: nats.aio.msg.Msg,
    session: aiohttp.ClientSession,
) -> None:
    subject = msg.subject
    data = msg.data.decode()

    log.info(f"Received on '{subject}'")
    log.info(data)

    async with session.post(
        cfg.webhook or DEFAULT_WEBHOOK,
        data=msg.data,
        headers={
            "Content-Type": "application/json",
            "X-NATS-Subject": subject,
        },
    ) as resp:
        log.info(f"Webhook status: {resp.status} {resp.reason}")

        async for _ in resp.content.iter_chunks():
            # just throw away the response data
            pass


async def main() -> None:
    configure()
    nc = await connect()

    async with aiohttp.ClientSession() as session:
        sub = await nc.subscribe(
            cfg.subject or DEFAULT_SUBJECT,
            cb=partial(handle_message, session=session),
        )
        log.info(f"Subscribed on '{sub.subject}'")

        try:
            # Wait forever
            await asyncio.wait_for(asyncio.Future(), timeout=None)
        except asyncio.CancelledError:
            pass
        finally:
            await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
