---
name: green-level2-containers
description: "Create and manage level-2 (green) containers from inside a level-1 sandbox container: run Claude, Codex or Pi in nested rootless podman with a chosen set of repos, and hand results back through the exchange dir. Use when asked to start a level-2, green, nested or child container, run an agent in one, pick which repos it sees, rebuild the sbx-green image, or collect its deliveries. Requires a --green level-1 container (daily is one): /dev/fuse exists and `green` is on PATH."
---

# Green level-2 containers

Level 2 is a rootless podman container started inside the level-1 sandbox
container. It sees only what is named at launch. Use it to run Claude, Codex
or Pi on a narrowed slice of the workspace, or on nothing at all.

## Preconditions

- `command -v green` succeeds and `/dev/fuse` exists. If not, this is not a
  `--green` launch: tell the user to start one with daily.cmd or
  `sbx --green`, and stop.
- The first `green` run builds the `sbx-green` image (a few minutes). It is
  cached in a volume and survives container restarts.

## Start a level-2 container

    green claude                 Claude Code TUI; asks which repos to mount
    green claude -r skills       mount ~/repos/skills, no question
    green claude -r bi,uit-po    several repos, comma-separated; prefixes
                                 work when unique; -r a mounts all
    green claude -r none "p"     headless one-shot: claude -p "p", no repos
    green codex | green pi       same flags, other agents
    green shell                  plain bash at level 2

Repo choice is the whole point: mount the least the task needs. Default is
none. A repo mounted into level 2 is the same directory level 1 and WSL see,
so commits made there are immediately real — push still happens from WSL.

## Manage

    green status                 image built? which green containers run?
    green build --refresh        re-fetch claude/codex/pi in the image
    green help                   print the user guide
    podman ps | logs | exec      raw podman works for everything else

Every `green` call starts a NEW level-2 container — except:

    green shell -c                       jump into the running green
                                         container (asks which, if several;
                                         `green shell -c <name>` to pick)

Use it to open a second shell beside a running Claude session. It wraps
`podman exec -it <name> bash`, which also works directly.

## Getting results out

Work committed in a mounted repo is already out. For anything else the
level-2 session runs:

    deliver <file-or-dir>...

which copies to `/green-exchange/res/<id>/` and touches `<id>.done`. At
level 1 (or in WSL), `watch-green` prints deliveries as they land; the same
directory is `~/green-exchange`. Input for a session goes the other way:
drop files in `~/green-exchange/req/` before launching.

## Constraints worth repeating to the user

- Level 2 runs as container root mapped to the vscode user; that is expected
  (single-uid podman, the WSL kernel allows nothing else).
- No credentials besides the running agent's own config dir are present.
- Everything outside mounted repos and `/green-exchange` dies with the
  container.
- Egress rides level 1's firewall; private networks are blocked.
