#!/usr/bin/env python3

import asyncio
import io
import json
from collections.abc import Sequence
from contextlib import redirect_stdout
from pathlib import Path

from mitmproxy import options
from mitmproxy import optmanager
from mitmproxy.tools.web import master

here = Path(__file__).parent.absolute()

filename = here / "../src/js/ducks/_options_gen.ts"


def _ts_type(t):
    if t is bool:
        return "boolean"
    if t is str:
        return "string"
    if t is int:
        return "number"
    if t == Sequence[str]:
        return "string[]"
    if t == str | None:
        return "string | undefined"
    if t == int | None:
        return "number | undefined"
    raise RuntimeError(t)


async def make() -> str:
    o = options.Options()
    m = master.WebMaster(o)
    opt: optmanager._Option

    with redirect_stdout(io.StringIO()) as s:
        print("/** Auto-generated by web/gen/options_js.py */")

        print("export interface OptionsState {")
        for _, opt in sorted(m.options.items()):
            print(f"    {opt.name}: {_ts_type(opt.typespec)};")
        print("}")
        print("")
        print("export type Option = keyof OptionsState;")
        print("")
        print("export const defaultState: OptionsState = {")
        for _, opt in sorted(m.options.items()):
            print(
                f"    {opt.name}: {json.dumps(opt.default)},".replace(
                    ": null", ": undefined"
                )
            )
        print("};")

    await m.done()
    return s.getvalue()


if __name__ == "__main__":
    filename.write_bytes(asyncio.run(make()).encode())
